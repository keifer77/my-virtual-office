#!/usr/bin/env python3
"""Report a short git status summary for a repo."""

import os
import subprocess
import sys


def git_output(args, cwd):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def count_lines(text):
    if not text:
        return 0
    return len([l for l in text.splitlines() if l.strip()])


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    repo_path = os.path.abspath(repo_path)

    print(f"Repo path: {repo_path}")
    print(
        f"Git repo: {'yes' if os.path.isdir(os.path.join(repo_path, '.git')) else 'no'}"
    )

    branch = git_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_path)
    print(f"Branch: {branch if branch else 'unavailable'}")

    status = git_output(["git", "status", "--porcelain"], repo_path)
    if status is None:
        print("Git status: unavailable (git not found or not a repo)")
        sys.exit(0)

    modified = 0
    untracked = 0
    staged = 0
    for line in status.splitlines():
        if not line.strip():
            continue
        if line.startswith("??"):
            untracked += 1
        elif line[0] in ("M", "A", "D", "R"):
            staged += 1
        elif line[1] in ("M", "D"):
            modified += 1

    print(f"Modified (tracked): {modified}")
    print(f"Staged: {staged}")
    print(f"Untracked: {untracked}")

    log_line = git_output(["git", "log", "--oneline", "-1"], repo_path)
    if log_line:
        print(f"Latest commit: {log_line}")
    else:
        print("Latest commit: none")


if __name__ == "__main__":
    main()
