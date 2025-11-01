"""Chunked retrieval-augmented generation agent for repository analysis.

This module implements a lightweight version of a RAG-style agent that mimics the
limitations of chunked retrieval. Instead of using embeddings, it performs a
simple keyword overlap scoring to surface chunks. The goal is to illustrate the
trade-offs described in the conversation rather than provide a production-ready
implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


@dataclass
class Chunk:
    """Representation of a chunked slice of a file."""

    file_path: Path
    start_line: int
    end_line: int
    text: str

    def format_header(self) -> str:
        return f"{self.file_path}:{self.start_line}-{self.end_line}"


def _is_text_file(path: Path) -> bool:
    """Best-effort check to ensure we only ingest text files."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            handle.read(2048)
        return True
    except (UnicodeDecodeError, OSError):
        return False


class ChunkedRAGAgent:
    """Naïve chunked retrieval agent.

    Parameters
    ----------
    repo_root:
        Root directory of the repository to index.
    chunk_size:
        Number of lines to include per chunk.
    chunk_overlap:
        Number of overlapping lines between consecutive chunks.
    top_k:
        Number of chunks to return for each query.
    include_extensions:
        Optional iterable of file suffixes to include when indexing.
    """

    def __init__(
        self,
        repo_root: Path,
        *,
        chunk_size: int = 80,
        chunk_overlap: int = 10,
        top_k: int = 4,
        include_extensions: Sequence[str] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.include_extensions = tuple(include_extensions or (
            ".py",
            ".md",
            ".rs",
            ".js",
            ".ts",
            ".tsx",
            ".json",
            ".yml",
            ".yaml",
            ".toml",
        ))
        self._chunks: List[Chunk] = []

    # ------------------------------------------------------------------
    # Index construction
    # ------------------------------------------------------------------
    def build_index(self) -> None:
        """Create chunk representations for the repository."""

        self._chunks = []
        for file_path in sorted(self.repo_root.rglob("*")):
            if not file_path.is_file():
                continue
            if any(part in {".git", "__pycache__"} for part in file_path.parts):
                continue
            if file_path.suffix and file_path.suffix not in self.include_extensions:
                continue
            if not _is_text_file(file_path):
                continue

            with file_path.open("r", encoding="utf-8") as handle:
                lines = handle.readlines()

            if not lines:
                continue

            start = 0
            step = max(1, self.chunk_size - self.chunk_overlap)
            while start < len(lines):
                end = min(len(lines), start + self.chunk_size)
                chunk_text = "".join(lines[start:end]).strip()
                if chunk_text:
                    chunk = Chunk(
                        file_path=file_path.relative_to(self.repo_root),
                        start_line=start + 1,
                        end_line=end,
                        text=chunk_text,
                    )
                    self._chunks.append(chunk)
                if end == len(lines):
                    break
                start += step

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------
    def _iter_chunks(self) -> Iterable[Chunk]:
        if not self._chunks:
            self.build_index()
        return list(self._chunks)

    @staticmethod
    def _tokenize(query: str) -> List[str]:
        return [token.lower() for token in query.split() if token.strip()]

    @staticmethod
    def _score_chunk(query_tokens: Sequence[str], chunk: Chunk) -> int:
        text = chunk.text.lower()
        return sum(text.count(token) for token in query_tokens)

    def retrieve(self, query: str) -> List[Chunk]:
        """Return the top-k chunks according to naive keyword overlap."""

        query_tokens = self._tokenize(query)
        scored_chunks = [
            (self._score_chunk(query_tokens, chunk), chunk)
            for chunk in self._iter_chunks()
        ]
        scored_chunks = [pair for pair in scored_chunks if pair[0] > 0]
        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[: self.top_k]]

    # ------------------------------------------------------------------
    # Answer generation
    # ------------------------------------------------------------------
    def answer(self, query: str) -> str:
        """Generate a deterministic explanation using retrieved chunks."""

        chunks = self.retrieve(query)
        if not chunks:
            return (
                "No matching chunks found. This mimics how retrieval can fail when "
                "critical context is split across embeddings."
            )

        descriptions = [
            f"- {chunk.format_header()}\n{indent(chunk.text, '  ')}"
            for chunk in chunks
        ]
        return (
            "Chunked retrieval agent fetched the following slices (showing how "
            "context can become fragmented):\n"
            + "\n\n".join(descriptions)
        )


def indent(text: str, prefix: str) -> str:
    """Indent helper that respects empty strings."""

    return "\n".join(f"{prefix}{line}" if line else prefix for line in text.splitlines())
