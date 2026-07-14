from pathlib import Path
import sys
import os
from typing import Any
from tqdm.auto import tqdm
import spacy
from update.api.http_client import HttpClient
from update.api.parliament_api import ParliamentApi
from update.graph.builder import EdgeBuilder
from update.pipeline.updater import Updater
from update.pipeline.checkpoint import CheckpointStore, STAGES
from update.storage.postgres_storage import SQLStorage
from update.embed.cleaner import Cleaner
from update.embed.embedder import TfIdfEmbedder, Doc2VecEmbedder, Doc2VecConfig
from update.embed.evaluator import Doc2VecEvaluator

import logging

_log_handlers = [
    logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
]

# Optional: zusätzlich in eine Datei loggen. Der Pfad sollte auf einem
# gemounteten Volume liegen, damit die Logs auch bei `docker run --rm`
# nach dem Entfernen des Containers erhalten bleiben. tqdm-Fortschritts-
# balken landen nicht hier (die schreiben nach stderr), die Datei enthält
# also nur saubere Log-Zeilen.
_log_file = os.environ.get("POLITGRAPH_LOG_FILE")
if _log_file:
    Path(_log_file).parent.mkdir(parents=True, exist_ok=True)
    _log_handlers.append(logging.FileHandler(_log_file, mode="a", encoding="utf-8"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=_log_handlers,
)

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("gensim").setLevel(logging.ERROR)   

logger = logging.getLogger(__name__)

async def run_app(args: Any) -> None:
    nlp = spacy.load("de_core_news_sm", disable=["tagger", "parser", "ner", "textcat"])
    # Der deutsche Lemmatizer ist lookup-basiert und braucht weder POS noch Embeddings.
    # tok2vec/morphologizer/attribute_ruler nur deaktivieren, wenn das wirklich zutrifft.
    if "lemmatizer" in nlp.pipe_names and getattr(nlp.get_pipe("lemmatizer"), "mode", "") == "lookup":
        for pipe_name in ("tok2vec", "morphologizer", "attribute_ruler"):
            if pipe_name in nlp.pipe_names:
                nlp.disable_pipe(pipe_name)
    logger.info(f"spaCy pipes active: {nlp.pipe_names}")
    http = HttpClient(base_url='https://api.openparldata.ch/v1/', timeout_seconds=10)
    api = ParliamentApi(http=http)
    project_root = Path(__file__).parent.parent.parent.resolve()
    edge_builder = EdgeBuilder(
        n_neighbors=args.n_neighbors,
        threshold=args.threshold,
    )
    evaluate = getattr(args, "evaluate", False)

    try:
        async with SQLStorage(connection_string=os.environ["POLITGRAPH_DB_CONNECTION_WRITER"]) as storage:
            updater = Updater(api=api, storage=storage)
            cleaner = Cleaner(nlp=nlp)
            tfidf_embedder = TfIdfEmbedder()

            if args.rebuild_edges:
                members = await storage.load_members_with_vectors()
                logger.info(f"Loaded {len(members)} members with vectors")
                await storage.delete_edges()
                edges = edge_builder.calculate_neighbors_d2v(members=members)
                logger.info(f"Calculated {len(edges)} edges (threshold={args.threshold}, k={args.n_neighbors})")
                await storage.save_edges(edges)
                return

            checkpoints = CheckpointStore(
                directory=None if args.no_checkpoint else Path(args.checkpoint_dir),
                run_key=f"offset={args.offset}|active={args.active}",
            )
            resume_idx = checkpoints.latest_completed_index()

            pbar = tqdm(total=5, desc="Update", unit="tasks")

            # --- Stage 0: fetch (STAGES[0] == "fetched") ---
            if resume_idx >= 0:
                docs, members = checkpoints.load(STAGES[resume_idx])
                logger.info(f"Resuming pipeline after '{STAGES[resume_idx]}' stage")
                pbar.update(resume_idx + 1)  # abgeschlossene Stages auf dem Balken überspringen
            else:
                docs, members = await updater.fetch_documents(
                    concurrency=int(args.concurrency),
                    offset=args.offset,
                    active=args.active,
                )
                if len(docs) == 0:
                    logger.info("Everything up to date, nothing to fetch")
                    pbar.close()
                    checkpoints.clear()
                    return
                checkpoints.save("fetched", (docs, members))
                pbar.update(1)

            # --- Stage 1: clean (STAGES[1] == "cleaned") ---
            if resume_idx < 1:
                cleaner.clean_documents(docs=docs)
                checkpoints.save("cleaned", (docs, members))
                pbar.update(1)

            # --- Stage 2: embed (STAGES[2] == "embedded") ---
            if resume_idx < 2:
                if evaluate:
                    evaluator = Doc2VecEvaluator(docs=docs)
                    results = evaluator.run()
                    best_config = evaluator.best.config
                    logger.info(f"Beste Doc2Vec-Config: {evaluator.best}")
                else:
                    best_config = Doc2VecConfig()

                # tfidf_embedder.embed_documents(docs=docs)
                # tfidf_embedder.embed_members()

                d2v_embedder = Doc2VecEmbedder(config=best_config)
                d2v_embedder.embed_documents(docs=docs)
                d2v_embedder.embed_members(members=members)

                # Checkpoint direkt nach dem (teuren) Training speichern, damit ein
                # Fehler in der anschließenden Evaluation kein erneutes Training
                # erzwingt. tagged_doc wird hier bewusst noch nicht genullt, da
                # quick_evaluate es zum Inferieren der Test-Vektoren braucht.
                checkpoints.save("embedded", (docs, members))
                pbar.update(1)

                if not evaluate:
                    quick_result = Doc2VecEvaluator.quick_evaluate(
                        model=d2v_embedder.model,
                        docs=docs,
                    )
                    logger.info(f"Doc2Vec: {quick_result}")

                for _, doc in docs:
                    doc.tagged_doc = None

            # --- Edges + Persistenz (günstig / idempotent, kein Checkpoint) ---
            edges = edge_builder.calculate_neighbors_d2v(members=members)
            pbar.update(1)

            await storage.save_members(members)
            await storage.save_affairs(docs)
            await storage.save_edges(edges)
            pbar.update(1)
            pbar.close()

            checkpoints.clear()
    finally:
        await http.aclose()