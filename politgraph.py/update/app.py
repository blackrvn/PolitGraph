from typing import Any

from update.api.http_client import HttpClient
from update.api.parliament_api import ParliamentApi
from update.pipeline.updater import Updater
from update.storage.sqlite_storage import SQLStorage

# Importe hier, weil app.py als composition root fungiert -> alle instanzen werden hier verwaltet
async def run_app(args: Any) -> None:
    http = HttpClient(base_url='https://api.openparldata.ch/v1/', timeout_seconds=10)
    api = ParliamentApi(http=http)
    updater = Updater(api=api)
    storage = SQLStorage("C://Users//iblto//source//repos//blackrvn//PolitGraph//politgraph.db")

    try:
        docs = await updater.fetch_documents(concurrency=int(args.concurrency))
        print(f"Members fetched: {len(docs)}")

        storage.add_members(docs)
        # Ab hier würdest du an embed / storage / graph übergeben
        # z.B.:
        # embedder.embed(docs)
        # storage.upsert(docs)
        # graph.build()

        if docs:
            sample = docs[0]
            print("Sample document:")
            print(sample)

    finally:
        await http.aclose()
