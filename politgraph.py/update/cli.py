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
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run_app(args))
