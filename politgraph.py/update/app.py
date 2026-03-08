from pathlib import Path
import sys
from typing import Any
from tqdm.auto import tqdm
import de_core_news_sm
from update.api.http_client import HttpClient
from update.api.parliament_api import ParliamentApi
from update.graph.builder import EdgeBuilder
from update.pipeline.updater import Updater
from update.storage.sqlite_storage import SQLStorage
from update.embed.cleaner import Cleaner
from update.embed.embedder import TfIdfEmbedder, Doc2VecEmbedder, Doc2VecConfig
from update.embed.evaluator import Doc2VecEvaluator

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
        logging.FileHandler("politgraph.log", mode="a", encoding="utf-8"),
    ],
)

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("gensim").setLevel(logging.ERROR)   

logger = logging.getLogger(__name__)

async def run_app(args: Any) -> None:
    nlp = de_core_news_sm.load(disable=["tagger", "parser", "ner", "textcat"])
    http = HttpClient(base_url='https://api.openparldata.ch/v1/', timeout_seconds=10)
    api = ParliamentApi(http=http)
    project_root = Path(__file__).parent.parent.parent.resolve()
    storage = SQLStorage(connection_string=f"{project_root}/politgraph.db")
    updater = Updater(api=api, storage=storage)
    cleaner = Cleaner(nlp=nlp)
    tfidf_embedder = TfIdfEmbedder()
    edge_builder = EdgeBuilder(
        n_neighbors=args.n_neighbors,
        threshold=args.threshold,
    )

    evaluate = getattr(args, "evaluate", False)

    try:
        if args.rebuild_edges:
            members = await storage.load_members_with_vectors()
            logger.info(f"Loaded {len(members)} members with vectors")

            # Alte Edges löschen
            await storage.delete_edges()

            edges = edge_builder.calculate_neighbors_d2v(members=members)
            logger.info(f"Calculated {len(edges)} edges (threshold={args.threshold}, k={args.n_neighbors})")

            await storage.save_edges(edges)
            return

        pbar = tqdm(total=5, desc="Update", unit="tasks")

        # Sammeln
        docs, members = await updater.fetch_documents(
            concurrency=int(args.concurrency),
            offset=args.offset,
            active=args.active,
        )
        pbar.update(1)

        if len(docs) == 0:
            print("Everything updated")
            pbar.close()
        else:
            await cleaner.clean_documents(docs=docs, concurrency=int(args.concurrency))
            pbar.update(1)

            # Doc2Vec: Vollständige oder schnelle Evaluation
            if evaluate:
                evaluator = Doc2VecEvaluator(docs=docs)
                results = evaluator.run()
                best_config = evaluator.best.config
                print(f"Beste Doc2Vec-Config: {evaluator.best}")
            else:
                best_config = Doc2VecConfig()

            tfidf_embedder.embed_documents(docs=docs)
            tfidf_embedder.embed_members()

            d2v_embedder = Doc2VecEmbedder(config=best_config)
            d2v_embedder.embed_documents(docs=docs)
            d2v_embedder.embed_members(members=members)

            if not evaluate:
                quick_result = Doc2VecEvaluator.quick_evaluate(
                    model=d2v_embedder.model,
                    docs=docs,
                )
                print(f"Doc2Vec: {quick_result}")

            pbar.update(1)

            edges = edge_builder.calculate_neighbors_d2v(members=members)
            pbar.update(1)

            await storage.save_members(members)
            await storage.save_affairs(docs)
            await storage.save_edges(edges)
            pbar.update(1)
    finally:
        await http.aclose()