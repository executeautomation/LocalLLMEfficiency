---
name: loop-guard
description: >
  CRITICAL SKILL — ALWAYS ACTIVE. Load this skill at the start of every
  session and re-read it before every tool call. Activate when: repeating
  steps, same error twice, editing same file more than twice, more than 15
  steps taken, about to retry something that already failed. Also handles
  RTK setup for token compression. This skill MUST override default behaviour
  whenever any loop condition is met.
---

# Loop Guard + RTK — ALWAYS ACTIVE

> ⚠️ THIS SKILL IS ALWAYS ON. Re-read this before every tool call.

---

## ON SESSION START — run immediately

```bash
python ~/.pi/agent/skills/loop-guard/scripts/check_loop.py reset
bash ~/.pi/agent/skills/loop-guard/scripts/rtk_check.sh
```

Output this block after running:

```
[LOOP-GUARD] Active. Pre-tool checklist: ON. Hard limits: ON.
RTK: <paste rtk_check.sh result — installed/not installed>
```

---

## MANDATORY PRE-TOOL CHECKLIST

**Before EVERY single tool call, answer these three questions:**

```
□ 1. Have I run this exact command or edit before this session?
□ 2. Have I seen this exact error more than once?
□ 3. Have I edited this file more than 2 times without a passing test?
```

If ANY answer is YES → **STOP. Do not call the tool. Go to RECOVERY below.**

If ALL answers are NO → record the action, then proceed:

```bash
python ~/.pi/agent/skills/loop-guard/scripts/check_loop.py record "<action description>"
python ~/.pi/agent/skills/loop-guard/scripts/check_loop.py check
```

If `check` exits non-zero → **LOOP DETECTED → go to RECOVERY.**

---

## HARD LIMITS — NEVER EXCEED

| Limit | Value | Action when hit |
|---|---|---|
| Same command retried | 2× | STOP → change approach |
| Same file edited | 3× | STOP → read file fresh first |
| Same error seen | 2× | STOP → try different strategy |
| Total steps in session | 20 | STOP → compress + summarise |
| Messages in context | 30 | STOP → request context reset |

---

## RECOVERY — follow exactly in order

### Step 1 — Announce the loop immediately

Output this block, no exceptions:

```
[LOOP-GUARD ACTIVATED]
Trigger: <which limit was hit>
Step count: <N>
What I keep retrying: <exact description>
Last thing that worked: <exact description>
```

### Step 2 — Compress progress

Output this block immediately after:

```
[PROGRESS SUMMARY]
Original task: <restate it>
Completed:
  - <step>
  - <step>
Blocked on:
  - <exact failing step>
Root cause hypothesis:
  - <best guess why it is failing>
```

### Step 3 — Change strategy, never repeat

| Situation | New approach — pick one |
|---|---|
| Same shell error | Check cwd, PATH, permissions before retrying |
| Same file edit failing | Read the FULL file before touching it |
| Test keeps failing | Read the test file completely first |
| Import/dep error | Check package.json / pyproject.toml first |
| Truly stuck | Output [LOOP-GUARD] NEEDS HUMAN INPUT and stop |

### Step 4 — Announce new approach

```
[LOOP-GUARD] New strategy: <describe it in one line>
Skipping: <what I was retrying>
Next action: <exactly what I will do now>
```

---

## TASK COMPLETION — always output this when done

```bash
python ~/.pi/agent/skills/loop-guard/scripts/check_loop.py history
rtk gain
```

Then output:

```
[LOOP-GUARD] TASK_COMPLETE
Summary: <one line>
Steps taken: <N>
Files changed: <list>
RTK savings: <paste rtk gain output>
```

---

## RTK SETUP — using the Pi extension (no shell wrappers needed)

RTK is wired through the **Pi extension** (`~/.pi/agent/extensions/rtk.ts`).
It auto-rewrites bash commands via `rtk rewrite` — you do **not** need shell wrappers in `~/.zshrc`.

### Verify setup
```bash
bash ~/.pi/agent/skills/loop-guard/scripts/rtk_check.sh
```

### Install RTK binary (if missing)
```bash
brew install rtk
# or
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
```

Minimum required: `rtk >= 0.23.0` (for `rtk rewrite` support).

### Check savings
```bash
rtk gain
```

---

## Scripts

→ `scripts/check_loop.py` — hash-based loop tracker; call `record`, `check`, `reset`, `history`
→ `scripts/rtk_check.sh` — verifies RTK binary + Pi extension are ready
