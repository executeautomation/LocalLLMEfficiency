---
name: task-boundaries
description: Define clear task boundaries, success criteria, and hard stopping conditions for every coding task in Pi agent. Always use this skill when starting any implementation task, bug fix, refactor, or feature addition. Prevents Pi from over-engineering, scope-creeping, or continuing after a task is complete. Trigger at the start of every task and whenever Pi seems to be expanding scope or working beyond what was asked.
---

# Task Boundaries & Stopping Conditions for Pi Agent

This skill prevents Pi from going beyond what was asked, re-doing completed work, or running indefinitely because it has no clear "done" definition.

## Core Principle

**Every task must have:**
1. A precise scope (what is IN and what is OUT)
2. A set of success criteria (how do we know it's done)
3. Hard stopping conditions (when to stop regardless of perceived incompleteness)
4. An explicit done signal (see `done-signal-reset` SKILL)

---

## Phase 1: Task Intake — Define the Boundary

Before writing a single line of code or calling a single tool, answer these three questions in order.

### Q1: What is the exact deliverable?

State the output in one sentence. Examples:
- "Write a function `parseTestResults()` that reads a JSON file and returns a typed array of TestResult"
- "Fix the failing test in `login.spec.ts` at line 42 — assertion mismatch on status code"
- "Refactor `AgentRunner` class to extract the `runLoop()` method into a separate file"

**If the deliverable cannot be stated in one sentence, the task is too large. Split it.**

### Q2: What is explicitly OUT of scope?

List what Pi must NOT do, even if it seems helpful. Examples:
- Do NOT refactor other functions in the file
- Do NOT add error handling beyond what is asked
- Do NOT install new packages
- Do NOT change the test file — only fix the implementation
- Do NOT update types unless the task explicitly requires it

### Q3: What are the success criteria?

Define 2–5 concrete, checkable conditions. Examples:
- `npm test` passes with 0 failures
- The function returns the correct type (verified by TypeScript compiler)
- The file exists at the expected path
- No new lint errors introduced (`npm run lint` exits with 0)

**Write these out explicitly at the start of the task.** Pi will check against these before declaring done.

---

## Phase 2: Execution Boundaries

### File Scope Rule
Only touch files that are **directly required** by the task deliverable.

Before editing any file, ask:
> "Is editing this file required to achieve the stated deliverable?"

If the answer is "it would be nice" or "it's related" — **do not edit it.**

### Tool Call Limit
Set a soft cap of **10 tool calls** per task. If reaching 10 tool calls:
1. Stop
2. Report current progress against success criteria
3. Ask the user whether to continue or adjust scope

This prevents silent runaway loops.

### No Speculative Work
Do not:
- Add features "while I'm in here"
- Fix unrelated issues noticed while working
- Add logging or debug output not requested
- Upgrade dependencies found to be outdated

If something unrelated is noticed that needs attention, note it in a comment or a brief message to the user — **do not act on it.**

---

## Phase 3: Boundary Check Before Each Tool Call

Before every tool call, run this mental check:

```
1. Does this tool call directly contribute to the stated deliverable? → YES: proceed / NO: stop
2. Am I still within the defined file scope? → YES: proceed / NO: stop
3. Have I already done this exact operation in this session? → YES: STOP (loop detected)
4. Have I exceeded 10 tool calls? → YES: report and pause
```

If any check fails, **stop and report to the user before continuing.**

---

## Phase 4: Stopping Conditions

Pi must stop (not pause, but fully stop) when any of these are true:

| Condition | Action |
|---|---|
| All success criteria are met | Emit DONE signal, stop |
| Tool call limit (10) reached | Report progress, await user decision |
| Same tool call repeated 2× with same args | LOOP DETECTED — stop and report |
| Error not resolved after 2 attempts | Stop, report error, await user |
| Any out-of-scope file is about to be edited | Stop, report, await explicit permission |
| User says "stop", "enough", "done" | Stop immediately, no further actions |

### Hard Stop on Loop Detection

If the same file is read twice in a row with no intervening write, or the same error appears twice in tool results:

```
⚠️ LOOP DETECTED
I have already [read X / attempted Y / seen error Z].
Stopping to avoid repeating work.

Completed so far:
- [bullet list of what is done]

Blocked on:
- [what caused the loop]

Awaiting your instruction before continuing.
```

---

## Phase 5: Scope Creep Detection

Pi must detect and refuse scope creep in real-time.

**Signals that scope is creeping:**
- A new file is being considered that wasn't in the original plan
- A new dependency is being evaluated
- The task description is mentally being "extended" to cover related cases
- Time spent on the task exceeds 2× the original estimate

**When scope creep is detected:**
1. Stop current work
2. Report what was originally asked vs what is now being considered
3. Ask the user explicitly: "Do you want me to extend scope to include X?"
4. Wait for a yes/no before continuing

---

## Template: Task Kickoff Block

Use this at the start of every task:

```
TASK BOUNDARY DEFINITION
========================
Deliverable: [one sentence]

In scope:
- [file/function/behaviour 1]
- [file/function/behaviour 2]

Out of scope:
- [explicit exclusion 1]
- [explicit exclusion 2]

Success criteria:
1. [checkable condition 1]
2. [checkable condition 2]
3. [checkable condition 3]

Tool call limit: 10
Loop detection: active
Stopping conditions: active
========================
```

Fill this in before starting. Do not proceed until it is filled.

---

## Phase 6: Compiler Error Diagnosis Protocol

**When a compiler (tsc, cargo, pytest, eslint, etc.) reports errors, follow this exact sequence. Do not deviate.**

### Rule 1: Read the compiler output first — always

RTK saves the full unfiltered compiler output to a tee log when a command fails:

```
TypeScript: 6 errors in 1 files
[full output: ~/Library/Application Support/rtk/tee/1234567890_tsc.log]
```

**The first action after any compiler failure is to read that tee log:**

```bash
cat "~/Library/Application Support/rtk/tee/<timestamp>_<command>.log"
```

This gives the exact file, line number, and error message. Do NOT start reading source files until this step is done.

### Rule 2: Trust the compiler's line numbers

The compiler tells you exactly where the problem is. Go directly to that location:

```bash
# TypeScript says: Header.tsx(579,3): error TS1109
# → Read lines 560–610 ONLY. Not the whole file.
awk 'NR>=560 && NR<=610 {print NR": "$0}' src/components/layout/Header.tsx
```

Do not read the file from line 1. Do not read it in multiple chunks. Read the specific range the compiler cited, plus ~20 lines of context above.

### Rule 3: Use tools to count — never count manually

Never mentally trace JSX/HTML tag nesting across multiple file reads. Use a single command instead:

```bash
# Find mismatched JSX tags — one command, one result
grep -n "<header\|</header" src/components/layout/Header.tsx

# Count all div opens vs closes in a range
awk 'NR>=100 && NR<=610' src/components/layout/Header.tsx | grep -c "<div"
awk 'NR>=100 && NR<=610' src/components/layout/Header.tsx | grep -c "</div"

# Find the exact line where nesting breaks — trace open/close counts
awk 'NR>=100 && NR<=610 {
  opens += gsub(/<div/, "")
  closes += gsub(/<\/div>/, "")
  print NR": open="opens" close="closes" "$0
}' src/components/layout/Header.tsx | grep -A2 -B2 "mismatch"
```

One grep command reveals what 8 manual file reads cannot.

### Rule 4: Max 3 reads per error diagnosis

If the problem is not identified after 3 targeted file reads, stop and report:

```
⚠️ DIAGNOSIS LIMIT REACHED
Error: [compiler error message]
Location: [file:line]

Reads attempted:
1. [what was read, what was found]
2. [what was read, what was found]
3. [what was read, what was found]

Could not isolate root cause.
Suggest: [specific next step for user to try]
Awaiting your instruction.
```

Do not continue reading more sections of the file. Ask the user.

### Rule 5: RTK sourceCodeFiltering must be disabled for precise edits

Before making a `str_replace` edit on any source file, disable RTK source filtering:

```bash
# Disable filtering to get exact unfiltered content
rtk_configure sourceCodeFiltering false

# Read the file — now you get exact original text
cat src/components/layout/Header.tsx | sed -n '570,610p'

# Make the edit using the exact original content
# ... str_replace with exact match ...

# Re-enable filtering
rtk_configure sourceCodeFiltering true
```

Attempting `str_replace` on RTK-filtered content causes text-match failures and loops.

---

## Compiler Error Quick Reference

| Compiler | Tee log location | Read command |
|---|---|---|
| TypeScript (tsc) | `~/Library/Application Support/rtk/tee/*_tsc.log` | `cat <path>` |
| Cargo (Rust) | `~/Library/Application Support/rtk/tee/*_cargo*.log` | `cat <path>` |
| Pytest | `~/Library/Application Support/rtk/tee/*_pytest.log` | `cat <path>` |
| ESLint | `~/Library/Application Support/rtk/tee/*_lint.log` | `cat <path>` |
| Any command | `ls -t ~/Library/Application\ Support/rtk/tee/ | head -5` | Most recent logs |

---

## Notes for Pi Agent

- Boundaries are not limitations — they are what makes fast, reliable work possible
- A task completed within scope in 5 tool calls is always better than a task "improved" in 25
- When unsure whether something is in scope: it is NOT in scope
- The user can always expand scope — Pi should never expand it unilaterally
- **Reading the same file section twice with no edit in between = loop. Stop immediately.**
- **Compiler errors tell you where to look. Trust them. Go directly there.**
