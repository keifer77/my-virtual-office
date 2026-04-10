#!/usr/bin/env python3
"""Update a single agent entry in hermes-state.json."""

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Update Hermes agent state")
    parser.add_argument("--agent", required=True, help="Agent ID to update")
    parser.add_argument(
        "--state", required=True, help="State value (idle, working, meeting, break)"
    )
    parser.add_argument("--task", default="", help="Task description")
    parser.add_argument(
        "--clear-task", action="store_true", help="Force task to empty string"
    )
    parser.add_argument("--last-input", default=None, help="Last input text")
    parser.add_argument("--last-input-from", default=None, help="Sender/source label for last input")
    parser.add_argument("--last-output", default=None, help="Last output text")
    args = parser.parse_args()

    status_dir = os.environ.get("VO_STATUS_DIR", "/tmp/vo-data")
    filepath = os.path.join(status_dir, "hermes-state.json")

    os.makedirs(status_dir, exist_ok=True)

    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = {}
    if not isinstance(data, dict):
        data = {}

    task = "" if args.clear_task else args.task
    current = data.get(args.agent, {}) if isinstance(data.get(args.agent, {}), dict) else {}
    entry = {"state": args.state, "task": task}

    if args.last_input is not None:
        entry["lastInput"] = {"text": args.last_input}
        if args.last_input_from is not None:
            entry["lastInput"]["from"] = args.last_input_from
        elif isinstance(current.get("lastInput"), dict) and "from" in current["lastInput"]:
            entry["lastInput"]["from"] = current["lastInput"]["from"]
    elif "lastInput" in current:
        entry["lastInput"] = current["lastInput"]

    if args.last_output is not None:
        entry["lastOutput"] = {"text": args.last_output}
    elif "lastOutput" in current:
        entry["lastOutput"] = current["lastOutput"]

    data[args.agent] = entry

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Updated {args.agent}: state={args.state}, task={task!r}")
    print(f"File: {filepath}")


if __name__ == "__main__":
    main()
