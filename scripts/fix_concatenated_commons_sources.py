#!/usr/bin/env python3
"""Split accidentally concatenated Commons URLs and refresh their local files."""
from __future__ import annotations

import json
import re
from pathlib import Path

from refresh_commons_media import ROOT, download, original_url, save_webp, title_from_source


URL = re.compile(r"https://commons\.wikimedia\.org/wiki/File:.*?\.(?:jpe?g|png|webp|tiff?)", re.I)


def main() -> None:
    rows = []
    for path in sorted((ROOT / "content" / "attractions").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        changed = False
        for line in text.splitlines():
            if "source:" not in line or line.count("https://commons.wikimedia.org/wiki/File:") < 2:
                continue
            urls = URL.findall(line)
            if not urls:
                continue
            clean = urls[0]
            prefix = line[: line.index("source:")]
            replacement = f'{prefix}source: "{clean}"'
            text = text.replace(line, replacement, 1)
            changed = True
            rows.append({"slug": path.stem, "source": clean})
        if changed:
            path.write_text(text, encoding="utf-8")
    output = ROOT / "reports" / "concatenated-commons-sources-fixed.json"
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"fixed": len(rows), "report": str(output)}))


if __name__ == "__main__":
    main()
