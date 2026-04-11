#!/usr/bin/env python3
"""Analyze the current repo and print a short summary."""

import os
import subprocess
import sys


JUNK_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}

TODO_MARKERS = ("TODO", "FIXME")
MAX_TODO = 10


def git_branch(repo_path):
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def scan_repo(repo_path):
    ext_counts = {".py": 0, ".js": 0, ".md": 0, ".json": 0}
    total = 0
    todos = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in JUNK_DIRS]
        for fname in files:
            fpath = os.path.join(root, fname)
            total += 1
            _, ext = os.path.splitext(fname)
            if ext in ext_counts:
                ext_counts[ext] += 1
            if len(todos) < MAX_TODO and ext in (
                ".py",
                ".js",
                ".md",
                ".json",
                ".html",
                ".css",
                ".ts",
                ".tsx",
                ".yaml",
                ".yml",
                ".toml",
                ".cfg",
                ".sh",
            ):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            for marker in TODO_MARKERS:
                                if marker in line:
                                    todos.append(
                                        f"{os.path.relpath(fpath, repo_path)}:{i}: {line.strip()}"
                                    )
                                    break
                except Exception:
                    pass

    return ext_counts, total, todos


def top_dirs(repo_path):
    try:
        return sorted(
            [
                d
                for d in os.listdir(repo_path)
                if os.path.isdir(os.path.join(repo_path, d)) and d not in JUNK_DIRS
            ]
        )
    except Exception:
        return []


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = os.path.abspath(repo_path)

    print(f"Repo path: {repo_path}")
    print(
        f"Git repo: {'yes' if os.path.isdir(os.path.join(repo_path, '.git')) else 'no'}"
    )

    branch = git_branch(repo_path)
    print(f"Branch: {branch if branch else 'unavailable'}")

    ext_counts, total, todos = scan_repo(repo_path)

    for ext in (".py", ".js", ".md", ".json"):
        print(f"{ext} files: {ext_counts[ext]}")
    print(f"Total files scanned: {total}")

    if todos:
        print(f"TODO/FIXME (first {len(todos)}):")
        for t in todos:
            print(f"  {t}")
    else:
        print("TODO/FIXME: none found")

    dirs = top_dirs(repo_path)
    print(f"Top-level dirs: {', '.join(dirs) if dirs else 'none'}")


if __name__ == "__main__":
    main()
