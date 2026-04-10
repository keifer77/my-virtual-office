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
    data[args.agent] = {"state": args.state, "task": task}

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Updated {args.agent}: state={args.state}, task={task!r}")
    print(f"File: {filepath}")


if __name__ == "__main__":
    main()
