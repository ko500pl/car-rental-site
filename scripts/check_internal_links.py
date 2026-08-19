"""Check generated HTML references without making network requests."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKIP_SCHEMES = {"data", "http", "https", "javascript", "mailto", "tel"}


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value and name in {"href", "src"}:
                self.values.append(value)


def resolve(output: Path, page: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme.lower() in SKIP_SCHEMES or parsed.netloc or not parsed.path:
        return None
    path = unquote(parsed.path)
    candidate = output / path.lstrip("/") if path.startswith("/") else page.parent / path
    if path.endswith("/"):
        candidate /= "index.html"
    elif not candidate.suffix and not candidate.exists():
        candidate /= "index.html"
    return candidate.resolve()


def main() -> int:
    output = (ROOT / (sys.argv[1] if len(sys.argv) > 1 else "dist")).resolve()
    if not output.is_dir():
        print(f"ERROR: generated output does not exist: {output}")
        return 1

    broken: list[tuple[str, str]] = []
    pages = sorted(output.rglob("*.html"))
    for page in pages:
        parser = References()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        for reference in parser.values:
            target = resolve(output, page, reference)
            if target is None:
                continue
            try:
                target.relative_to(output)
            except ValueError:
                broken.append((page.relative_to(output).as_posix(), reference))
                continue
            if not target.exists():
                broken.append((page.relative_to(output).as_posix(), reference))

    if broken:
        print(f"FAILED: {len(broken)} broken internal reference(s).")
        for page, reference in broken[:50]:
            print(f" - {page}: {reference}")
        return 1
    print(f"OK: {len(pages)} HTML files have no broken local href/src references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
