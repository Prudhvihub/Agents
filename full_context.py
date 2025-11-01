"""Full-context agent that reads entire files before responding."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


def _is_text_file(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            handle.read(2048)
        return True
    except (UnicodeDecodeError, OSError):
        return False


class FullContextAgent:
    """Agent that reads whole files to preserve execution flow.

    Parameters
    ----------
    repo_root:
        Root directory of the repository to analyse.
    include_extensions:
        Optional iterable of file suffixes to consider while scanning files.
    """

    def __init__(
        self,
        repo_root: Path,
        *,
        include_extensions: Sequence[str] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
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

    def _iter_files(self) -> Iterable[Path]:
        for file_path in sorted(self.repo_root.rglob("*")):
            if not file_path.is_file():
                continue
            if any(part in {".git", "__pycache__"} for part in file_path.parts):
                continue
            if file_path.suffix and file_path.suffix not in self.include_extensions:
                continue
            if not _is_text_file(file_path):
                continue
            yield file_path

    @staticmethod
    def _tokenize(query: str) -> List[str]:
        return [token.lower() for token in query.split() if token.strip()]

    @staticmethod
    def _score_document(query_tokens: Sequence[str], text: str) -> int:
        lowered = text.lower()
        return sum(lowered.count(token) for token in query_tokens)

    def gather_context(self, query: str) -> Dict[Path, str]:
        """Return full documents sorted by relevance."""

        query_tokens = self._tokenize(query)
        scored: Dict[Path, int] = defaultdict(int)
        contents: Dict[Path, str] = {}

        for file_path in self._iter_files():
            text = file_path.read_text(encoding="utf-8")
            contents[file_path] = text
            scored[file_path] = self._score_document(query_tokens, text)

        sorted_paths = sorted(
            contents,
            key=lambda path: (scored[path], -len(contents[path])),
            reverse=True,
        )
        return {path.relative_to(self.repo_root): contents[path] for path in sorted_paths if scored[path] > 0}

    def answer(self, query: str) -> str:
        docs = self.gather_context(query)
        if not docs:
            return "No relevant files were found when reading entire documents."

        summaries = []
        for path, text in docs.items():
            lines = text.splitlines()
            preview = "\n".join(lines[: min(len(lines), 20)])
            summaries.append(
                f"- {path} (showing first 20 lines to preserve flow)\n{indent(preview, '  ')}"
            )

        return (
            "Full-context agent read the following files in their entirety before "
            "summarising the first 20 lines to illustrate coherent flow:\n"
            + "\n\n".join(summaries)
        )


def indent(text: str, prefix: str) -> str:
    return "\n".join(f"{prefix}{line}" if line else prefix for line in text.splitlines())
