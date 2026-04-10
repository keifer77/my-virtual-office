# Hermes Usage

## Purpose
These helpers make My Virtual Office reflect Hermes agent activity through `hermes-state.json`.

## Files
- `app/set_hermes_state.py`
- `app/run_with_hermes_state.py`

## Status file location
By default the state file is written to:

`/tmp/vo-data/hermes-state.json`

If `VO_STATUS_DIR` is set, the file is written to:

`$VO_STATUS_DIR/hermes-state.json`

## Manually set one agent state
Example:

```bash
python3 app/set_hermes_state.py --agent hermes-main --state working --task "Researching topic"
```