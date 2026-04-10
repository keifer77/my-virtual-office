#!/usr/bin/env python3
"""Run a command with Hermes agent state set to working/idle around it."""

import argparse
import subprocess
import sys
import os


def set_state(agent, state, task):
    script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "set_hermes_state.py"
    )
    subprocess.run(
        [sys.executable, script, "--agent", agent, "--state", state, "--task", task],
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run a command with Hermes agent state"
    )
    parser.add_argument("--agent", required=True, help="Agent ID")
    parser.add_argument("--task", required=True, help="Task description while working")
    args, remaining = parser.parse_known_args()

    if not remaining or remaining[0] != "--":
        print(
            "Usage: run_with_hermes_state.py --agent ID --task DESC -- COMMAND [ARGS...]",
            file=sys.stderr,
        )
        sys.exit(1)

    command = remaining[1:]
    if not command:
        print("Error: no command provided after --", file=sys.stderr)
        sys.exit(1)

    set_state(args.agent, "working", args.task)
    try:
        result = subprocess.run(command)
    finally:
        set_state(args.agent, "idle", "")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
