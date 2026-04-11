#!/usr/bin/env python3
"""Smoke test: verify Hermes action flow end-to-end from the backend."""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8090"


def get(path, params=None):
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.URLError as e:
        return None, str(e)


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        BASE_URL + path, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body_text)
        except json.JSONDecodeError:
            return e.code, body_text
    except urllib.error.URLError as e:
        return None, str(e)


def check(label, condition, detail=""):
    tag = "PASS" if condition else "FAIL"
    msg = f"  [{tag}] {label}"
    if detail and not condition:
        msg += f" -- {detail}"
    print(msg)
    return condition


def main():
    print(f"Smoke test against {BASE_URL}\n")

    # 1. Server is reachable
    status, _ = get("/")
    if not check("server reachable", status is not None, _):
        print("\nAborting: server not running.")
        sys.exit(1)

    # 2. /agents-list includes hermes-main with both actions
    status, data = get("/agents-list")
    if not check("agents-list responds 200", status == 200, f"got {status}"):
        print("\nAborting: cannot fetch agents.")
        sys.exit(1)

    agents = data.get("agents", [])
    hermes = next(
        (
            a
            for a in agents
            if a.get("key") == "hermes-main" or a.get("agentId") == "hermes-main"
        ),
        None,
    )
    check("hermes-main found in agents", hermes is not None)

    if hermes:
        action_ids = [act.get("id") for act in hermes.get("actions", [])]
        check("repo-analysis action listed", "repo-analysis" in action_ids)
        check("git-status action listed", "git-status" in action_ids)

    # 3. Launch repo-analysis
    status, resp = post(
        "/api/agent/action", {"agent": "hermes-main", "action_id": "repo-analysis"}
    )
    repo_ok = status == 200 and resp.get("ok") is True
    repo_conflict = status == 409
    if repo_conflict:
        pid = resp.get("pid")
        log_path = resp.get("log_path", "")
        check("repo-analysis launch (already running)", True, f"pid={pid}")
    else:
        pid = resp.get("pid")
        log_path = resp.get("log_path", "")
        check("repo-analysis launch ok", repo_ok, f"status={status} body={resp}")
        check("repo-analysis returns pid", pid is not None)
        check("repo-analysis returns log_path", bool(log_path))

    # 4. Fetch repo-analysis log
    time.sleep(1)
    status, log_resp = get(
        "/api/agent/action-log", {"agent": "hermes-main", "action_id": "repo-analysis"}
    )
    log_ok = status == 200 and log_resp.get("ok") is True
    check("repo-analysis log fetched", log_ok, f"status={status}")
    if log_ok:
        check("repo-analysis log non-empty", bool(log_resp.get("content", "").strip()))

    # 5. Launch git-status
    time.sleep(1)
    status, resp = post(
        "/api/agent/action", {"agent": "hermes-main", "action_id": "git-status"}
    )
    git_ok = status == 200 and resp.get("ok") is True
    git_conflict = status == 409
    if git_conflict:
        pid = resp.get("pid")
        log_path = resp.get("log_path", "")
        check("git-status launch (already running)", True, f"pid={pid}")
    else:
        pid = resp.get("pid")
        log_path = resp.get("log_path", "")
        check("git-status launch ok", git_ok, f"status={status} body={resp}")
        check("git-status returns pid", pid is not None)
        check("git-status returns log_path", bool(log_path))

    # 6. Fetch git-status log
    time.sleep(1)
    status, log_resp = get(
        "/api/agent/action-log", {"agent": "hermes-main", "action_id": "git-status"}
    )
    log_ok = status == 200 and log_resp.get("ok") is True
    check("git-status log fetched", log_ok, f"status={status}")
    if log_ok:
        check("git-status log non-empty", bool(log_resp.get("content", "").strip()))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
