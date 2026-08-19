#!/usr/bin/env python3
"""Verify the supported Python runtime and pinned build dependencies."""

from __future__ import annotations

import argparse
import importlib.metadata
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PYTHON = (3, 12)
PIN_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;]+)$")


def read_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-r "):
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError(f"{path.name}:{line_number}: dependency must use package==version")
        pins[match.group(1)] = match.group(2)
    return pins


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tools",
        action="store_true",
        help="also verify optional image and OG-generation dependencies",
    )
    args = parser.parse_args()

    errors: list[str] = []
    current_python = sys.version_info[:2]
    if current_python != EXPECTED_PYTHON:
        errors.append(
            "Python 3.12 is required "
            f"(current: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})"
        )

    files = [ROOT / "requirements.txt"]
    if args.tools:
        files.append(ROOT / "requirements-tools.txt")

    pins: dict[str, str] = {}
    try:
        for path in files:
            pins.update(read_pins(path))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    for package, expected in sorted(pins.items()):
        try:
            actual = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"missing dependency: {package}=={expected}")
            continue
        if actual != expected:
            errors.append(f"{package}: expected {expected}, found {actual}")

    if errors:
        print("Environment check: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    scope = "build + optional tools" if args.tools else "canonical build"
    print(
        "Environment check: PASS "
        f"({scope}; Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
