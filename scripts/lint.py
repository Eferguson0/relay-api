#!/usr/bin/env python3
"""
Linting script for the SupaHealth project.
Runs ruff, black, and isort on the codebase.
"""

import subprocess
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd: str, description: str, check: bool = True) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️  {description} found issues")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"   Errors: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False


def main():
    """Main function to run all linting tools."""
    print("🔍 Starting linting process...")
    print("=" * 50)

    # Define the source directories to lint
    source_dirs = ["app", "scripts", "alembic"]

    # Run isort (import sorting)
    isort_cmd = f"uv run isort {' '.join(source_dirs)} --check-only --diff"
    isort_success = run_command(
        isort_cmd, "Checking import order with isort", check=False
    )

    # Run black (code formatting)
    black_cmd = f"uv run black {' '.join(source_dirs)} --check --diff"
    black_success = run_command(
        black_cmd, "Checking code formatting with black", check=False
    )

    # Run ruff (linting)
    ruff_cmd = f"uv run ruff check {' '.join(source_dirs)}"
    ruff_success = run_command(ruff_cmd, "Running linting with ruff", check=False)

    # Run pyright (type checking)
    pyright_cmd = f"uv run pyright {' '.join(source_dirs)}"
    pyright_success = run_command(
        pyright_cmd, "Running type checking with pyright", check=False
    )

    print("=" * 50)

    # Summary
    if isort_success and black_success and ruff_success and pyright_success:
        print("🎉 All linting checks passed!")
        return 0
    else:
        print("⚠️  Some linting checks failed. Run the following to fix:")
        print()
        if not isort_success:
            print("   uv run isort app scripts alembic")
        if not black_success:
            print("   uv run black app scripts alembic")
        if not ruff_success:
            print("   uv run ruff check --fix app scripts alembic")
        if not pyright_success:
            print("   uv run pyright app scripts alembic")
        print()
        print("Or run: uv run lint-fix")
        return 1


def fix():
    """Fix all linting issues automatically."""
    print("🔧 Fixing linting issues...")
    print("=" * 50)

    # Define the source directories to lint
    source_dirs = ["app", "scripts", "alembic"]

    # Run isort (import sorting)
    isort_cmd = f"uv run isort {' '.join(source_dirs)}"
    run_command(isort_cmd, "Fixing import order with isort")

    # Run black (code formatting)
    black_cmd = f"uv run black {' '.join(source_dirs)}"
    run_command(black_cmd, "Fixing code formatting with black")

    # Run ruff (linting)
    ruff_cmd = f"uv run ruff check --fix {' '.join(source_dirs)}"
    run_command(ruff_cmd, "Fixing linting issues with ruff")

    print("=" * 50)
    print("🎉 All linting issues have been fixed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
