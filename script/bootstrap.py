#!/usr/bin/env python3
"""Prepare dev setup"""

import subprocess
import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent.resolve()


def _run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    """Setup development environment."""
    print("==> Setting up development environment")
    print(f"Project root: {PROJ_ROOT}")
    print()

    try:
        _run(["uv", "sync", "--all-extras"], PROJ_ROOT)
        _run(["uv", "run", "pre-commit", "install"], PROJ_ROOT)

        print("@@@ Dev env ready")
        print("@@@")
        print("@@@ uv run poe app        # Start app")
        print("@@@ uv run poe test       # Check tests")
        print("@@@ uv run poe lint_full  # Linter")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"@@@ Error, exit code of the command {e.returncode}", file=sys.stderr)
        return e.returncode
    except FileNotFoundError:
        print("@@@ Error: file or command missing. Ensure 'uv' is present.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
