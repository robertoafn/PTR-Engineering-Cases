"""Comprueba que los enlaces relativos entre documentos sigan resolviendo."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FENCED_CODE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))")
SKIPPED_PREFIXES = ("#", "http://", "https://", "mailto:", "doi:")


def test_relative_markdown_links_resolve_inside_repository() -> None:
    broken: list[str] = []
    escaped: list[str] = []

    for document in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in document.relative_to(ROOT).parts):
            continue
        text = FENCED_CODE.sub("", document.read_text(encoding="utf-8-sig"))
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = (match.group(1) or match.group(2)).strip()
            if raw_target.casefold().startswith(SKIPPED_PREFIXES):
                continue
            path_text = unquote(raw_target.split("#", 1)[0].split("?", 1)[0])
            if not path_text:
                continue

            candidate = (document.parent / path_text).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                escaped.append(f"{document.relative_to(ROOT)} -> {raw_target}")
                continue
            if not candidate.exists():
                broken.append(f"{document.relative_to(ROOT)} -> {raw_target}")

    assert not escaped, "Enlaces que escapan del repositorio:\n" + "\n".join(escaped)
    assert not broken, "Enlaces relativos rotos:\n" + "\n".join(broken)
