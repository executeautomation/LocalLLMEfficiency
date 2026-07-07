# Local LLM Efficiency — Pi Agent Skills

A collection of VS Code agent skills designed to make AI coding agents (specifically **Pi**) more efficient, focused, and token-conscious when working on local projects.

## Featured In

These skills were demonstrated in an **ExecuteAutomation** YouTube video:

🎥 **[YouTube — ExecuteAutomation](https://youtu.be/OKldcw2pGtA)**

## Skills Overview

| Skill | Purpose |
|---|---|
| **[rtk-default](rtk-default/SKILL.md)** | Token compression via RTK (Rust Token Killer) CLI proxy — reduces shell command output by 60–90%. |
| **[loop-guard](loop-guard/SKILL.md)** | Prevents infinite loops, repeated failures, and runaway sessions with hard limits and automatic recovery. |
| **[task-boundaries](task-boundaries/SKILL.md)** | Defines clear scope, success criteria, and stopping conditions for every task to prevent over-engineering and scope creep. |
| **[done-signal-reset](done-signal-reset/SKILL.md)** | Emits an explicit DONE signal on completion and triggers a context reset so the next task starts clean. |

## How They Work Together

These skills form a complete lifecycle:

1. **task-boundaries** — Define what to build, what's out of scope, and how we know it's done.
2. **rtk-default** — Compress every shell command's output to save tokens during execution.
3. **loop-guard** — Detects when the agent gets stuck in repetitive patterns and forces a strategy change.
4. **done-signal-reset** — Declares completion explicitly and resets context for the next task.

## Setup

### RTK (Rust Token Killer)

```bash
brew install rtk
rtk init -g --agent pi
```

Verify:
```bash
rtk init --show    # confirms hook is active
rtk gain           # shows token savings stats
```

### Loop Guard Scripts

The loop-guard skills ships with two helper scripts:

- `loop-guard/scripts/check_loop.py` — Tracks actions and detects repetition loops.
- `loop-guard/scripts/rtk_check.sh` — Verifies RTK binary and Pi extension are configured correctly.

Run at session start:
```bash
python ~/.pi/agent/skills/loop-guard/scripts/check_loop.py reset
bash ~/.pi/agent/skills/loop-guard/scripts/rtk_check.sh
```

---

*Built for local-first AI coding workflows. Keep tokens low, keep scope tight.*
