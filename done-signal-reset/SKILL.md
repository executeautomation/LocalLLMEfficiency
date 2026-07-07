---
name: done-signal-reset
description: "Emit an explicit DONE signal when a task is complete and trigger a context reset to prepare Pi for the next task cleanly. Always use this skill when a task finishes, when the user says a task is complete, or when all success criteria from task-boundaries have been met. Prevents Pi from continuing to work after completion and ensures the next task starts with a clean context. Trigger at task completion, when user says done, next, move on, or when all success criteria are satisfied."
---

# Explicit DONE Signal & Context Reset for Pi Agent

This skill defines exactly how Pi declares a task complete and resets context for the next task — preventing post-completion drift, accidental continuation, and context bleed between tasks.

## Why This Matters

Without an explicit DONE signal:
- Pi continues making minor "improvements" after the task is done
- Context from Task A bleeds into Task B and causes wrong assumptions
- Pi second-guesses completed work and reopens already-closed decisions
- Loops begin at the *boundary* between tasks, not just within them

---

## The DONE Signal

When all success criteria from the Task Boundary Definition are met, Pi must emit this exact signal before taking any further action:

```
✅ DONE — [one-line summary of what was completed]

Completed:
- [success criterion 1] → PASSED
- [success criterion 2] → PASSED
- [success criterion 3] → PASSED

Files changed:
- [file 1] — [what changed]
- [file 2] — [what changed]

No further actions taken.
Awaiting your next instruction.
```

**After emitting the DONE signal, Pi must not:**
- Make any additional tool calls
- Edit any additional files
- Run any additional commands
- "Clean up" or "tidy" anything not in the original scope
- Offer unsolicited suggestions about what to do next

The DONE signal is a full stop. Not a pause.

---

## Conditions That Trigger the DONE Signal

Pi emits DONE when **any** of these are true:

| Condition | Trigger |
|---|---|
| All success criteria from task-boundaries are met | Emit DONE |
| User says "done", "that's it", "stop", "enough", "looks good", "ship it" | Emit DONE immediately |
| User says "next" or describes a new task | Emit DONE for current task, then start context reset |
| Tool call limit (10) reached | Emit PARTIAL DONE (see below) |
| User approves the output | Emit DONE |

---

## Partial DONE Signal

If the task is not fully complete but needs to pause (tool limit reached, error encountered, user interrupts):

```
⏸️ PARTIAL DONE — [current state summary]

Completed so far:
- [what is done]

Remaining:
- [what is not yet done]

Stopped because:
- [reason: tool limit / error / user interrupt]

Awaiting your instruction to continue or adjust.
```

After a PARTIAL DONE, Pi waits. It does not continue automatically.

---

## Context Reset Protocol

After emitting a DONE signal (full or partial), immediately run the context reset:

### Step 1: RTK Full Reset

```bash
rtk trim --full-reset --summarize-session
```

This drops all tool history and file contents from the completed task, keeping only a compact session summary.

### Step 2: Session Summary Injection

After the RTK reset, inject this compact summary into fresh context:

```
SESSION SUMMARY (previous task)
================================
Task: [one-line description]
Status: COMPLETE / PARTIAL
Files changed: [comma-separated list]
Key decisions made: [2-3 bullet points max]
Known issues for next task: [any relevant notes]
================================
```

This summary travels forward into the next task's context — without dragging along all the tool call noise.

### Step 3: Clean Slate Declaration

After the reset, emit this to signal readiness:

```
🔄 CONTEXT RESET COMPLETE
Ready for next task.
Previous session summary is available above.
```

---

## Inter-Task Hygiene Rules

Between tasks, Pi must:

1. **Not carry over open file handles** — Re-read files fresh in the new task if needed
2. **Not assume previous code is still valid** — The user may have edited files between tasks
3. **Not reference previous task errors** — Start fresh; old errors are irrelevant unless the user raises them
4. **Not continue a previous line of reasoning** — Each task is a new problem

---

## User-Triggered Resets

The user can trigger a context reset manually at any time with these phrases:

| User says | Pi does |
|---|---|
| "fresh start" | Full RTK reset + clean slate declaration |
| "reset context" | Full RTK reset + clean slate declaration |
| "start over" | Full RTK reset, discard session summary |
| "clean slate" | Full RTK reset, discard session summary |
| "forget what you did" | Full RTK reset, discard session summary |
| "next task" | DONE signal for current task + context reset |

---

## Anti-Patterns Pi Must Never Do After DONE

❌ **Do not** run one more `npm test` "just to confirm"
❌ **Do not** add a comment to a file explaining what was changed
❌ **Do not** open the next likely file "to get a head start"
❌ **Do not** offer to "also fix" a related issue noticed during the task
❌ **Do not** summarise the work in a long message — the DONE signal is the summary
❌ **Do not** ask "shall I continue?" — wait for an explicit new instruction

---

## Integration with Other Skills

This skill works as the exit layer for the full Pi anti-loop system:

```
[Task starts]
    ↓
rtk-default     → Trim context before starting
    ↓
task-boundaries → Define scope and success criteria
    ↓
[Work happens]
    ↓
done-signal-reset → Emit DONE, reset context
    ↓
[Next task starts — back to rtk-default]
```

The three skills form a loop-proof cycle. Each task is isolated, bounded, and cleanly handed off.

---

## Quick Reference

```
DONE Phrase:     ✅ DONE — [summary]
Partial Phrase:  ⏸️ PARTIAL DONE — [state]
Reset Phrase:    🔄 CONTEXT RESET COMPLETE
RTK Command:     rtk trim --full-reset --summarize-session
```

Never skip the DONE signal. Never skip the context reset. These are not optional steps — they are the mechanism that prevents the next task from being contaminated by the current one.
