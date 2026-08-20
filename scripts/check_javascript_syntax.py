"""Check repository JavaScript syntax with Node.js."""
from __future__ import annotations
import argparse, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def javascript_files(paths: list[str]) -> list[Path]:
    files: set[Path] = set()
    for raw in paths:
        path = (ROOT / raw).resolve()
        if path.is_file() and path.suffix.lower() == ".js": files.add(path)
        elif path.is_dir(): files.update(path.rglob("*.js"))
    return sorted(files)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["static"])
    parser.add_argument("--node")
    args = parser.parse_args()
    node = args.node or shutil.which("node")
    if not node:
        print("ERROR: Node.js was not found. Install Node.js or pass --node PATH."); return 1
    files = javascript_files(args.paths)
    if not files:
        print("ERROR: no JavaScript files were found in the requested paths."); return 1
    failed = []
    for path in files:
        result = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            failed.append(path); print(f"ERROR: invalid JavaScript: {path.relative_to(ROOT)}")
            if (result.stderr or result.stdout).strip(): print((result.stderr or result.stdout).strip())
    if failed:
        print(f"FAILED: {len(failed)} of {len(files)} JavaScript files contain syntax errors."); return 1
    print(f"OK: {len(files)} JavaScript files passed Node.js syntax validation."); return 0

if __name__ == "__main__": raise SystemExit(main())
