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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    comparison = compare_agents(args.repo, args.query)
    print(comparison.format())


if __name__ == "__main__":  # pragma: no cover
    main()

