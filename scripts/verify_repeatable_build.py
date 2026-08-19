"""Build the site twice and compare every generated file by SHA-256."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def inventory(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rentup-repeatable-") as temp:
        base = Path(temp)
        outputs = (base / "first", base / "second")
        for output in outputs:
            subprocess.run(
                [sys.executable, "build.py", str(output)],
                cwd=ROOT, check=True,
            )
        first, second = (inventory(output) for output in outputs)

    if first == second:
        print(f"OK: two builds are identical ({len(first)} files).")
        return 0
    changed = sorted(
        name for name in set(first) | set(second)
        if first.get(name) != second.get(name)
    )
    print(f"FAILED: {len(changed)} generated file(s) differ.")
    for name in changed[:20]:
        print(f" - {name}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
