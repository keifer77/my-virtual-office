#!/usr/bin/env python3
"""Static validator for hermes-agents.json and action allowlist integrity."""

import json
import re
import sys

AGENTS_PATH = "app/hermes-agents.json"
SERVER_PATH = "app/server.py"


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  [FAIL] file not found: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"  [FAIL] malformed JSON in {path}: {e}")
        return None


def parse_wrapped_allowlist(text):
    entries = []
    in_list = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "_ACTION_WRAPPED_TASK_ALLOWLIST = [":
            in_list = True
            continue
        if in_list:
            if stripped.startswith("]"):
                break
            m = re.match(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', stripped)
            if m:
                entries.append((m.group(1), m.group(2)))
    return entries


def main():
    failures = 0

    agents_data = load_json(AGENTS_PATH)
    if agents_data is None:
        sys.exit(1)

    with open(SERVER_PATH) as f:
        server_text = f.read()

    wrapped_allowlist = parse_wrapped_allowlist(server_text)

    # agents array exists
    agents = agents_data.get("agents")
    if not check("agents array exists", isinstance(agents, list) and len(agents) > 0):
        sys.exit(1)

    seen_ids = {}
    for agent in agents:
        aid = agent.get("id", "")
        prefix = f"agent '{aid}'" if aid else "agent (missing id)"

        # unique id
        if aid in seen_ids:
            check(f"{prefix} has unique id", False, f"duplicate of '{seen_ids[aid]}'")
        else:
            seen_ids[aid] = aid
            check(f"agent '{aid}' has unique id", True)
            check(f"agent '{aid}' has id", bool(aid))

        # statusKey matches id
        sk = agent.get("statusKey", "")
        check(f"{prefix} statusKey matches id", sk == aid, f"statusKey='{sk}'")

        actions = agent.get("actions", [])
        if not actions:
            continue

        seen_action_ids = set()
        for action in actions:
            act_prefix = f"{prefix} action '{action.get('id', '')}'"

            # has id
            has_id = bool(action.get("id"))
            check(f"{act_prefix} has id", has_id)
            if not has_id:
                continue

            # unique per agent
            aid_act = action["id"]
            if aid_act in seen_action_ids:
                check(f"{act_prefix} unique within agent", False, "duplicate action id")
            else:
                seen_action_ids.add(aid_act)
                check(f"{act_prefix} unique within agent", True)

            # has label
            check(f"{act_prefix} has label", bool(action.get("label")))

            # has command
            cmd = action.get("command", "")
            check(f"{act_prefix} has command", bool(cmd))

            # command uses run_with_hermes_state.py wrapper
            uses_wrapper = "run_with_hermes_state.py" in cmd
            check(f"{act_prefix} command uses run_with_hermes_state.py", uses_wrapper)

            # wrapped task script is in the allowlist
            if uses_wrapper:
                sep = cmd.find(" -- ")
                if sep >= 0:
                    after_sep = cmd[sep + 4 :].strip()
                    parts = after_sep.split()
                    if len(parts) >= 2:
                        task_script = parts[1]
                        if "/" in task_script:
                            task_script = task_script.rsplit("/", 1)[1]
                        allowed = any(
                            parts[0] == ta and task_script == tf
                            for ta, tf in wrapped_allowlist
                        )
                        check(
                            f"{act_prefix} task '{task_script}' in wrapped-task allowlist",
                            allowed,
                            f"not in allowlist: {wrapped_allowlist}",
                        )
                    else:
                        check(f"{act_prefix} has wrapped subcommand", False)
                else:
                    check(f"{act_prefix} has '--' separator in command", False)

    if failures > 0:
        print(f"\n{failures} check(s) failed.")
        sys.exit(1)
    print("\nAll checks passed.")


def check(label, condition, detail=""):
    global failures
    tag = "PASS" if condition else "FAIL"
    msg = f"  [{tag}] {label}"
    if detail and not condition:
        msg += f" -- {detail}"
    print(msg)
    if not condition:
        failures += 1
    return condition


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
