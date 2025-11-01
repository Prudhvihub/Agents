"""Utilities to compare chunked retrieval vs. full-context agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from .chunked_rag import ChunkedRAGAgent
from .full_context import FullContextAgent


@dataclass
class AgentComparison:
    """Result bundle highlighting the contrast between two strategies."""

    query: str
    chunked_response: str
    full_context_response: str

    def format(self) -> str:
        header = f"Query: {self.query}\n{'=' * (7 + len(self.query))}\n"
        return (
            header
            + "\n-- Chunked Retrieval --\n"
            + self.chunked_response
            + "\n\n-- Full Context --\n"
            + self.full_context_response
        )


def compare_agents(
    repo_root: Path,
    query: str,
    *,
    chunk_size: int = 80,
    chunk_overlap: int = 10,
    top_k: int = 4,
) -> AgentComparison:
    """Run both agents and return a formatted comparison object."""

    chunked = ChunkedRAGAgent(
        repo_root,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k,
    )
    full = FullContextAgent(repo_root)

    chunked_response = chunked.answer(query)
    full_context_response = full.answer(query)

    return AgentComparison(
        query=query,
        chunked_response=chunked_response,
        full_context_response=full_context_response,
    )

