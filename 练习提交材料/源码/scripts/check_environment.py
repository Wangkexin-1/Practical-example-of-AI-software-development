"""Check development prerequisites; this is not an application test."""

import importlib
import shutil
import subprocess
import sys


def main():
    print(f"Python: {sys.version.split()[0]}")
    print(f"Executable: {sys.executable}")
    failures = []
    if sys.version_info < (3, 11):
        failures.append("Python 3.11 or later is required")
    for name in ("csv", "pathlib", "dataclasses", "unittest", "tkinter"):
        try:
            module = importlib.import_module(name)
            print(f"{name}: OK")
            if name == "tkinter":
                print(f"Tk: {module.TkVersion}")
        except ImportError as exc:
            failures.append(f"{name}: {exc}")
    git = shutil.which("git")
    if git:
        result = subprocess.run(
            [git, "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode:
            failures.append("Git version check failed")
        else:
            print(result.stdout.strip())
    else:
        failures.append("Git is not available on PATH")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("Environment check passed. Application behavior: NOT_RUN.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
