#!/usr/bin/env python3
"""Invoke Hermes CLI for a short repo summary with local repo context."""

import os
import shutil
import subprocess
import sys


HERMES_BIN = shutil.which("hermes") or "/Users/keithmaschak/.local/bin/hermes"
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

SUMMARY_INSTRUCTION = (
    "Give a short summary of this repository in 3 to 5 lines. "
    "Cover what it does, the main tech stack, and the current state. "
    "Do not write more than 5 lines."
)


def gather_context(repo_path):
    lines = []
    lines.append(f"Repository path: {repo_path}")
    lines.append("")

    if os.path.isdir(os.path.join(repo_path, ".git")):
        lines.append("Git info:")
        for args in [
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            ["git", "log", "--oneline", "-1"],
            ["git", "status", "--short"],
        ]:
            try:
                r = subprocess.run(
                    args, cwd=repo_path, capture_output=True, text=True, timeout=5
                )
                if r.returncode == 0 and r.stdout.strip():
                    lines.append(r.stdout.strip()[:300])
            except Exception:
                pass
        lines.append("")

    ext_counts = {}
    total = 0
    top_dirs = sorted(
        d
        for d in os.listdir(repo_path)
        if os.path.isdir(os.path.join(repo_path, d)) and d not in SKIP_DIRS
    )
    lines.append(f"Top-level dirs: {', '.join(top_dirs[:12])}")

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            total += 1
            _, ext = os.path.splitext(fname)
            if ext in (
                ".py",
                ".js",
                ".html",
                ".css",
                ".json",
                ".md",
                ".ts",
                ".tsx",
                ".yaml",
                ".yml",
            ):
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

    parts = [f"{ext}: {count}" for ext, count in sorted(ext_counts.items())]
    lines.append(f"Files ({total} total): {', '.join(parts[:10])}")
    lines.append("")

    return "\n".join(lines)


def main():
    print("=== Hermes Repo Summary ===")
    print()

    if not shutil.which(HERMES_BIN):
        print(f"Result: FAILED - hermes binary not found at {HERMES_BIN}")
        sys.exit(1)

    context = gather_context(REPO_PATH)
    prompt = context + "\n" + SUMMARY_INSTRUCTION

    cmd = [HERMES_BIN, "chat", "-q", prompt, "--quiet"]
    print(f"Command: hermes chat -q <prompt> --quiet")
    print(f"Repo:    {REPO_PATH}")
    print()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except FileNotFoundError:
        print(f"Result: FAILED - hermes binary not found at {HERMES_BIN}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Result: FAILED - hermes chat timed out (90s)")
        sys.exit(1)

    exit_code = result.returncode
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    print(f"Exit code:    {exit_code}")
    stdout_tail = stdout[-500:] if len(stdout) > 500 else stdout
    print(f"Stdout:       {stdout_tail if stdout_tail else '(empty)'}")
    if stderr:
        stderr_tail = stderr[-300:] if len(stderr) > 300 else stderr
        print(f"Stderr:       {stderr_tail}")
    print()

    if exit_code == 0 and stdout:
        print("Result: OK - Hermes repo summary received")
    else:
        print(f"Result: FAILED - exit code {exit_code}")


if __name__ == "__main__":
    main()
