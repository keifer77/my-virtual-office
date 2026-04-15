#!/usr/bin/env python3
"""Regression guard for Hermes post-work idle policy cleanup.

The rule should be simple:
- arm the skip flag only on an explicit working -> idle transition
- consume it once in returnToDesk()
- do not infer post-work behavior from just being near the desk
- do not keep dead post-work settle timer branches around
"""

from pathlib import Path


GAME_JS = Path(__file__).resolve().parent.parent / "app" / "game.js"


def _src() -> str:
    return GAME_JS.read_text(encoding="utf-8")


def test_post_work_skip_flag_is_armed_only_by_transition_rule() -> None:
    src = _src()
    assert (
        "this._skipFirstDeskReturn = prevState === 'working' && state === 'idle';"
        in src
    )


def test_start_idle_action_does_not_rearm_skip_from_desk_proximity() -> None:
    src = _src()
    assert "Fallback: set _skipFirstDeskReturn - at desk" not in src
    assert "distSq < 900" not in src


def test_dead_post_work_settle_timer_branches_are_removed() -> None:
    src = _src()
    assert "_postWorkSettleTimer" not in src
