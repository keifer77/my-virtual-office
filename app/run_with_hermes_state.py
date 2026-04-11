#!/usr/bin/env python3
"""Run a command with Hermes agent state set to working/idle around it."""

import argparse
import subprocess
import sys
import os


def set_state(
    agent,
    state,
    task,
    last_input=None,
    last_input_from=None,
    last_output=None,
    clear_task=False,
):
    script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "set_hermes_state.py"
    )
    cmd = [sys.executable, script, "--agent", agent, "--state", state]
    if clear_task:
        cmd.append("--clear-task")
    else:
        cmd.extend(["--task", task])
    if last_input is not None:
        cmd.extend(["--last-input", last_input])
    if last_input_from is not None:
        cmd.extend(["--last-input-from", last_input_from])
    if last_output is not None:
        cmd.extend(["--last-output", last_output])
    subprocess.run(cmd, check=False)


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

    set_state(
        args.agent,
        "working",
        args.task,
        last_input=args.task,
        last_input_from="Wrapper",
    )

    exit_code = 1
    try:
        result = subprocess.run(command)
        exit_code = result.returncode
    except Exception:
        exit_code = 1
    finally:
        if exit_code == 0:
            summary = "Command completed successfully."
        else:
            summary = f"Command failed with exit code {exit_code}."
        set_state(args.agent, "idle", "", clear_task=True, last_output=summary)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
