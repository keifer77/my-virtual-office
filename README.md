# Hermes-Compatible Fork of My Virtual Office

This repository is a Hermes integration fork of **My Virtual Office**.

The goal of this work was not to rebuild the original app from scratch or turn it into a polished production product. The goal was to make the office UI work credibly with Hermes agents by adding compatibility layers, fixing live state sync, and debugging the behavior needed to make agent activity visible in the office.

This fork is best understood as a **working reference integration** and portfolio project: functional, demoable, and useful for showing the integration work, but not presented as finished production software.

## What this fork adds

- Hermes agent roster loading from config
- Hermes live state bridge into the office UI
- improved working vs idle behavior for Hermes agents
- routing Hermes to real visible desks instead of invisible placeholder positions
- fixes for multiple frontend/backend state-fidelity issues that made the office display misleading behavior
- compatibility-oriented cleanup so Hermes activity is understandable and demonstrable in the office

## Current status

This fork is currently in a **workable reference state**.

### Working now

- Hermes agents render in the office
- live Hermes state can drive visible office behavior
- working and idle states reflect more truthfully in the UI
- Hermes routes to a real visible desk when working
- post-work idle behavior is substantially improved
- key compatibility issues like weather proxy behavior, score route handling, and Hermes state sync were fixed during the integration process

### What this is not

- not a polished production-ready office simulator
- not a full Hermes-native chat/session platform
- not a generalized plugin system
- not a claim that every office behavior is perfectly polished

## Why this exists

I built this as a practical integration project to prove that Hermes agents could be adapted into an existing visual office environment and to work through the real synchronization and behavior bugs required to make that believable in practice.

This project demonstrates:

- open-source adaptation
- agent integration work
- frontend/backend debugging
- state-fidelity repair
- behavior-level UI troubleshooting
- pragmatic engineering tradeoffs in a real codebase

## Quick start

This repo is easiest to run as a local demo/reference environment.

```bash
cd app
python3 server.py
```

Then open:

```text
http://localhost:8090
```

Notes:

- the office UI lives under `app/`
- Hermes-compatible state is driven through the local bridge files and endpoints used by this fork
- if you are adapting this to your own Hermes setup, expect some local configuration work rather than a one-command production install

## What was fixed in this fork

Highlights from the integration/debugging work:

- live Hermes state is reflected more truthfully in the office
- stale or misleading idle/working behavior was corrected
- Hermes now routes to visible desks instead of off-screen or placeholder positions
- manual UI states are less likely to be overwritten by misleading backend fallbacks
- post-work idle handling was cleaned up so the frontend policy is simpler and less fragile

## Known limitations

- this is still a compatibility fork, not a fully finished standalone product
- some movement and action positioning may still need tuning
- Hermes-native request/response history is not fully surfaced in the office UI
- full Hermes workspace, bio, and session integration is not complete
- some fixes are intentionally narrow compatibility fixes rather than final long-term architecture
- the repo currently contains active integration work beyond the README; treat it as a working fork, not a frozen release artifact

## Attribution

This project is based on the upstream **My Virtual Office** project.

- Upstream project: `eliautobot/my-virtual-office`
- This fork focuses on Hermes compatibility and reference integration work rather than upstream product parity

If you want the broader original product vision, features, and presentation, start by reviewing the upstream repository.

## Honest scope statement

If you are looking for a polished end-user product, this repo is not positioned as that.

If you are looking for:

- a Hermes-compatible visual office demo
- a reference fork showing real integration/debugging work
- a portfolio example of adapting an existing UI to an autonomous agent system

then this repository is in the right shape for that purpose.
