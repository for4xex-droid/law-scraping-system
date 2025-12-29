import os
from pathlib import Path

IGNORE_DIRS = {"__pycache__", ".git", ".venv", "venv", ".mypy_cache", ".pytest_cache"}
TARGET_EXTENSIONS = {".py", ".md", ".toml", ".yml", "Makefile"}


def dump_context() -> None:
    root = Path(".")
    print("# Project Context Dump\n")
    for r, d, f in os.walk(root):
        d[:] = [x for x in d if x not in IGNORE_DIRS]
        for file in f:
            path = Path(r) / file
            if path.suffix in TARGET_EXTENSIONS:
                print(f"\n## File: {path}\n```")
                try:
                    print(path.read_text(encoding="utf-8"))
                except Exception:
                    print("# Error reading file")
                print("```")


if __name__ == "__main__":
    dump_context()
