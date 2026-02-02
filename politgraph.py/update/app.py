from pathlib import Path
from typing import Any

from tqdm.auto import tqdm

import de_core_news_sm

from update.api.http_client import HttpClient
from update.api.parliament_api import ParliamentApi
from update.graph.builder import EdgeBuilder
from update.pipeline.updater import Updater
from update.storage.sqlite_storage import SQLStorage
from update.embed.cleaner import Cleaner
from update.embed.embedder import TfIdfEmbedder, Doc2VecEmbedder

# Importe hier, weil app.py als composition root fungiert -> alle instanzen werden hier verwaltet
async def run_app(args: Any) -> None:

    nlp = de_core_news_sm.load(disable=["tagger", "parser", "ner", "textcat"])

    http = HttpClient(base_url='https://api.openparldata.ch/v1/', timeout_seconds=10)
    api = ParliamentApi(http=http)
    project_root = Path(__file__).parent.parent.parent.resolve()
    storage = SQLStorage(connection_string=f"{project_root}/politgraph.db")
    updater = Updater(api=api, storage=storage)
    cleaner = Cleaner(nlp=nlp)
    tfidf_embeddder = TfIdfEmbedder()
    d2v_embedder = Doc2VecEmbedder()
    edge_builder = EdgeBuilder(n_neighbors=5)

    try:
        pbar = tqdm(total=5, desc="Update", unit="tasks")

        # Sammeln
        docs, members = await updater.fetch_documents(concurrency=int(args.concurrency))
        pbar.update(1)

        if(len(docs) == 0):
            print("Everything updated")
            pbar.close()

        else:
            # Reinigen
            await cleaner.clean_documents(docs=docs, concurrency=int(args.concurrency))
            pbar.update(1)

            # Embed
            tfidf_embeddder.embed_documents(docs=docs)
            tfidf_embeddder.embed_members()
            d2v_embedder.embed_documents(docs=docs)
            d2v_embedder.embed_members()
            pbar.update(1)

            # Kanten berechnen
            edges = edge_builder.calculate_neighbors_d2v(members=members)
            pbar.update(1)

            # Speichern
            await storage.save_members(members)
            await storage.save_affairs(docs)
            await storage.save_edges(edges)
            pbar.update(1)

    finally:
        await http.aclose()
