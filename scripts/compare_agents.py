"""Command line interface to compare chunked vs. full-context agents."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repository root is on the import path when running as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.evaluation import compare_agents


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare chunked RAG and full-context agents on a repository query.",
    )
    parser.add_argument(
        "query",
        help="Natural language description of what you want to inspect.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Path to the repository to analyse (defaults to current working directory).",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=80,
        help="Number of lines per chunk for the chunked agent (default: 80).",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=10,
        help="Number of overlapping lines between chunks (default: 10).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=4,
        help="How many chunks to surface for the comparison (default: 4).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    comparison = compare_agents(
        args.repo,
        args.query,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        top_k=args.top_k,
    )
    print(comparison.format())


if __name__ == "__main__":  # pragma: no cover
    main()

