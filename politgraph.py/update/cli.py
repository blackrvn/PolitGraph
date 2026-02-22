import argparse
import asyncio

from update.app import run_app


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="update",
        description="Parliament update pipeline",
    )
    p.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Use to debug, skips the first n members"
        )
    p.add_argument(
        "--active",
        type=bool,
        default=True,
        help="If true, only active members will be retrieved"
        )
    p.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Concurrency for member fetching",
    )
    p.add_argument(
        "--evaluate", 
        action="store_true", 
        help="Doc2Vec-Configs evaluieren"
    )
    p.add_argument(
        "--rebuild-edges",
        action="store_true",
        help="Überspringt Fetch/Clean/Embed, lädt Members aus DB und berechnet nur Edges neu"
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Schwellenwert für Edge-Ähnlichkeit (default: 0.8)"
    )
    p.add_argument(
        "--n-neighbors",
        type=int,
        default=5,
        help="Anzahl Nachbarn pro Member (default: 5)"
    )

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run_app(args))
