# Hermes MVO Checkpoint

## Branch
feature/external-agent-config

## Current pushed state
This branch now contains the clean Hermes integration checkpoint and it is pushed to GitHub.

Included commits now cover:
- frontend/config integration
- server-side fallback support
- live Hermes state file bridge

## What is now actually committed and durable
The repo now includes these committed changes:

- `app/hermes-agents.json`
  - Hermes roster and branch config source

- `app/game.js`
  - `_fetchRoster()` loads from `hermes-agents.json`
  - Hermes branches are loaded before agent initialization
  - roster no longer depends on `/api/agents` for office rendering

- `app/index.html`
  - model apply degrades cleanly with:
    `Model switching not configured`
  - avoids misleading OpenClaw config-write errors when no model switching is available

- `app/server.py`
  - `_load_hermes_agents()` helper added
  - `GET /api/agents` now reads Hermes roster
  - `GET /agents-list` now reads Hermes roster and resolves Hermes branch names
  - `start_http_server()` initializes presence state from Hermes agents
  - `_read_agent_bio()` now recognizes Hermes agents even when they are not in `AGENT_WORKSPACES`
  - `_get_models()` now degrades cleanly when OpenClaw config is missing
  - `_get_models()` now adds Hermes agents into `agentModels`
  - `/status` now also syncs Hermes live state from `hermes-state.json`

- `app/gateway_presence.py`
  - `_sync_hermes_state_from_file(filepath)` added
  - Hermes state file entries now flow into the existing `_state` map with source:
    `hermes-file`

## What was re-tested successfully after a real server restart
These behaviors were verified again using the on-disk code after restarting the server:

- `http://localhost:8090/status`
  returned:
  - `hermes-main`
  - `research-agent`
  - both with default idle state before live state file injection

- `http://localhost:8090/agents-list`
  returned Hermes agents correctly
  - correct names
  - correct roles
  - correct branch display names: `OPS` and `R&D`

- `http://localhost:8090/agent-bio/hermes-main`
  returned empty-string fallback content instead of `Unknown agent`

- `http://localhost:8090/models`
  returned a valid empty-but-safe response:
  - empty `models`
  - Hermes entries in `agentModels`
  - empty `defaultModel`
  - no hard failure

## What was re-tested successfully for live Hermes state
A test `hermes-state.json` file was written and verified end to end.

Verified flow:

1. `hermes-state.json` written with:
   - `hermes-main` = `working`
   - task = `Testing Hermes live state`

2. `/status` returned:
   - `source: "hermes-file"`
   - correct live `state`
   - correct live `task`

3. The office UI and agent modal updated correctly:
   - STATUS showed `WORKING`
   - task text showed `Testing Hermes live state`

This means the first real Hermes live-state bridge is now committed and durable.

## What is working now
The current branch now has a durable first vertical slice:

- Hermes agents render in the office from config
- Hermes names, roles, emoji, branches, and appearances render correctly
- clicking Hermes agents opens the modal
- STATUS can resolve Hermes agents from:
  - server fallback state
  - Hermes live state file input
- BRANCH display works correctly
- AGENTS.md and other bio tabs load cleanly with empty fallback content
- SKILLS degrade cleanly
- MODEL read path degrades cleanly
- MODEL apply no longer shows the misleading config-write failure when no switching is configured

## What is still not done
This branch is still using partial compatibility behavior, not full Hermes-native integration.

Still missing:

1. Real Hermes request/response history
   - LAST REQUEST and RESPONSE are still not backed by real Hermes history

2. Real Hermes bio/workspace mapping
   - bio tabs currently degrade cleanly, but are not yet wired to actual Hermes workspace files

3. Real Hermes model switching
   - read path is safe
   - write path is intentionally not implemented for Hermes yet

4. Any true Hermes chat/session bridge
   - current work is roster/fallback/live-state stabilization, not full chat/session integration

5. Automatic Hermes state production
   - the live-state bridge works
   - but Hermes still needs a real producer that writes `hermes-state.json` automatically

## Important implementation note
The successful `server.py` and `gateway_presence.py` work was done safely by using small terminal patch commands against exact code blocks, not by letting AI broadly rewrite the file.

That method worked.
Broad AI rewrite attempts on large Python files were the main source of wasted time and noisy diffs.

## Rule for future large Python edits
For future `app/server.py` or `app/gateway_presence.py` work:

- use exact surgical patching only
- verify after every edit with:
  - `git diff --stat -- <file>`
- stop immediately if the diff suddenly becomes huge

## Best next target
The next meaningful project step is:

### Build an automatic Hermes state producer
Create the first real process, script, or hook that writes `hermes-state.json` automatically from Hermes activity so the office reflects real agent work without manual test files.