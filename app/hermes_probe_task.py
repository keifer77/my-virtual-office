#!/usr/bin/env python3
"""Diagnostic probe: verify Hermes agent reachability via the local CLI."""

import shutil
import subprocess
import sys


HERMES_BIN = shutil.which("hermes") or "/Users/keithmaschak/.local/bin/hermes"
PROMPT = "Reply with exactly the word HERMES_OK and nothing else."


def main():
    print("=== Hermes Probe ===")
    print()

    cmd = [HERMES_BIN, "chat", "-q", PROMPT, "--quiet"]
    print(f"Command: {' '.join(cmd)}")
    print()

    if not shutil.which(HERMES_BIN):
        print(f"Result: PROBE FAILED - hermes binary not found at {HERMES_BIN}")
        sys.exit(1)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        print(f"Result: PROBE FAILED - hermes binary not found at {HERMES_BIN}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Result: PROBE FAILED - hermes chat timed out (60s)")
        sys.exit(1)

    exit_code = result.returncode
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    print(f"Exit code:    {exit_code}")
    stdout_tail = stdout[-300:] if len(stdout) > 300 else stdout
    print(f"Stdout:       {stdout_tail if stdout_tail else '(empty)'}")
    if stderr:
        stderr_tail = stderr[-300:] if len(stderr) > 300 else stderr
        print(f"Stderr:       {stderr_tail}")
    print()

    if "HERMES_OK" in stdout.upper():
        print("Result: PROBE PASSED - Hermes responded with HERMES_OK")
    elif exit_code == 0 and stdout:
        print(
            "Result: PROBE PASSED (partial) - Hermes reachable but did not return HERMES_OK"
        )
    else:
        print(f"Result: PROBE FAILED - exit code {exit_code}")


if __name__ == "__main__":
    main()
