"""Verify the canonical source and generated-site layout without changing files."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SOURCE = (
    "build.py", "theme.py", "yaml_io.py", "content", "sitegen",
    "static", "admin", "mobile", "tests", "performance-budget.json",
    "scripts/audit_performance.py",
)
DEPLOY_RULES = {
    "render.yaml": ("python3 build.py dist", "staticPublishPath: ./dist"),
    "netlify.toml": ("python3 build.py dist", 'publish = "dist"'),
    ".github/workflows/pages.yml": ("run_quality_gate.py --output dist", "path: dist"),
}


def main() -> int:
    errors: list[str] = []

    def fail(message: str) -> None:
        errors.append(message)
        print(f"ERROR: {message}")

    print(f"Project root: {ROOT}")
    for relative in REQUIRED_SOURCE:
        if not (ROOT / relative).exists():
            fail(f"required source path is missing: {relative}")

    for relative, needles in DEPLOY_RULES.items():
        path = ROOT / relative
        if not path.is_file():
            fail(f"deploy configuration is missing: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in content:
                fail(f"{relative} does not contain canonical rule: {needle}")

    try:
        result = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, check=True,
            capture_output=True, text=True,
        )
        tracked = []
        for raw in result.stdout.splitlines():
            path = raw.replace("\\", "/")
            first = path.split("/", 1)[0]
            if first == "dist" or first.startswith("dist-"):
                tracked.append(path)
        if tracked:
            fail(f"generated output is tracked by Git: {', '.join(tracked[:5])}")
    except (OSError, subprocess.CalledProcessError):
        print("WARNING: Git is unavailable; tracked-output check was skipped.")

    legacy_dirs = sorted(
        path.name for path in ROOT.iterdir()
        if path.is_dir() and path.name.startswith("dist-")
    )
    archives = sorted(path.name for path in ROOT.glob("*.zip"))
    print("Canonical output: dist/")
    print(f"Legacy generated directories (ignored): {len(legacy_dirs)}")
    print(f"Local ZIP archives (ignored): {len(archives)}")
    print(f"Nested legacy project copy: {'present' if (ROOT / 'car-rental-site').exists() else 'absent'}")

    if errors:
        print(f"FAILED: {len(errors)} layout problem(s) found.")
        return 1
    print("OK: source tree and all deploy targets use the canonical dist/ output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
