---
name: rtk-default
description: Use RTK (Rust Token Killer) CLI proxy commands to reduce token consumption by 60-90% on every shell command in Pi coding agent. RTK is already installed via Homebrew at version 0.37.2 and must be initialised for Pi with `rtk init -g --agent pi`. Always prefix shell commands with rtk equivalents. Trigger this skill for every bash/shell tool call — git, file reads, tests, builds, grep, docker, kubectl, aws, npm, cargo, and any command that produces output.
---

# RTK — Rust Token Killer for Pi Agent

RTK is a single Rust binary CLI proxy installed at `/opt/homebrew/Cellar/rtk/0.37.2/bin/rtk`.  
It intercepts shell commands, filters their output, and returns only what matters — reducing token consumption by 60–90% per command.

**You already have RTK installed. The only missing step is Pi-specific initialisation.**

---

## One-Time Setup for Pi

```bash
rtk init -g --agent pi
```

This installs RTK as a **TypeScript extension** into Pi via the `tool_call` hook — the same mechanism Pi uses for all extensions. After running this, Pi automatically rewrites bash commands to their `rtk` equivalents before execution. Restart Pi after running.

Verify it worked:
```bash
rtk init --show    # confirms hook is active
rtk gain           # shows token savings stats
```

---

## How It Works

RTK sits between Pi and the shell. When Pi runs `git status`, the hook rewrites it to `rtk git status` before execution. Pi receives ~200 tokens of compact output instead of ~2,000 tokens of raw output. The agent never needs to call `rtk` explicitly — it just happens.

**Scope note:** The hook only fires on Bash tool calls. Pi built-in tools like `Read`, `Grep`, and `Glob` bypass the hook. For those, call `rtk read`, `rtk grep`, `rtk find` explicitly.

---

## Command Reference

### Files
```bash
rtk ls .                        # token-optimised directory listing
rtk read file.ts                # smart file reading with noise removal
rtk read file.ts -l aggressive  # signatures only — strips function bodies
rtk smart file.rs               # 2-line heuristic code summary
rtk find "*.ts" .               # compact find results
rtk grep "pattern" .            # grouped search results by file
rtk diff file1 file2            # changed lines only
```

### Git (highest savings — 80–92%)
```bash
rtk git status                  # compact status
rtk git diff                    # condensed diff
rtk git log -n 10               # one-line commits
rtk git add .                   # → "ok"
rtk git commit -m "msg"         # → "ok abc1234"
rtk git push                    # → "ok main"
rtk git pull                    # → "ok 3 files +10 -2"
```

### Test Runners (90% savings — most impactful)
```bash
rtk jest                        # failures only
rtk vitest                      # failures only
rtk playwright test             # E2E failures only
rtk pytest                      # Python failures only
rtk cargo test                  # Rust failures only
rtk go test                     # Go failures only
rtk rspec                       # Ruby failures only
rtk test <any-test-cmd>         # generic wrapper — failures only
rtk err <any-cmd>               # errors/warnings only from any command
```

### Build & Lint
```bash
rtk tsc                         # TypeScript errors grouped by file
rtk lint                        # ESLint grouped by rule/file
rtk next build                  # Next.js compact build
rtk cargo build                 # Rust build compact
rtk cargo clippy                # Rust clippy compact
rtk ruff check                  # Python linting compact
rtk prettier --check .          # files needing formatting only
```

### Package Managers
```bash
rtk npm test                    # filtered test output
rtk pnpm list                   # compact dependency tree
rtk pip list                    # Python packages compact
rtk prisma generate             # no ASCII art
```

### Containers & Cloud
```bash
rtk docker ps                   # compact container list
rtk docker logs <container>     # deduplicated logs
rtk kubectl pods                # compact pod list
rtk kubectl logs <pod>          # deduplicated logs
rtk aws sts get-caller-identity # one-line identity
rtk aws ec2 describe-instances  # compact instance list
```

### Utilities
```bash
rtk curl <url>                  # auto JSON schema, truncated
rtk json config.json            # structure without values
rtk env -f AWS                  # filtered env vars, secrets masked
rtk log app.log                 # deduplicated log output
rtk deps                        # dependency summary
rtk summary <long-command>      # 2-line heuristic summary of any command
rtk proxy <command>             # raw passthrough but tracked
```

---

## Token Savings Reference

| Command type | Frequency per session | Without RTK | With RTK | Savings |
|---|---|---|---|---|
| `ls` / `tree` | 10x | 2,000 | 400 | -80% |
| `cat` / `read` | 20x | 40,000 | 12,000 | -70% |
| `grep` / `rg` | 8x | 16,000 | 3,200 | -80% |
| `git status` | 10x | 3,000 | 600 | -80% |
| `git diff` | 5x | 10,000 | 2,500 | -75% |
| `cargo/npm test` | 5x | 25,000 | 2,500 | -90% |
| `pytest` | 4x | 8,000 | 800 | -90% |
| **Total (30 min session)** | | **~118,000** | **~23,900** | **-80%** |

---

## On Failure: Full Output Recovery

When a command fails, RTK automatically saves the full unfiltered output:

```
FAILED: 2/15 tests
[full output: ~/.local/share/rtk/tee/1707753600_cargo_test.log]
```

Pi can read this file to get full details without re-running the command. Controlled via `~/.config/rtk/config.toml`:

```toml
[tee]
enabled = true
mode = "failures"    # "failures" | "always" | "never"
```

---

## Configuration

Global config at `~/Library/Application Support/rtk/config.toml` (macOS):

```toml
[hooks]
exclude_commands = ["curl", "playwright"]  # skip rewrite for specific commands
```

---

## Checking Savings

```bash
rtk gain                    # summary stats
rtk gain --graph            # ASCII graph of last 30 days
rtk gain --history          # recent command history
rtk gain --daily            # day-by-day breakdown
rtk discover                # find commands where RTK savings were missed
rtk session                 # RTK adoption across recent Pi sessions
```

---

## Global Flags

```bash
rtk --ultra-compact <cmd>   # ASCII icons, inline format — extra token savings
rtk -v <cmd>                # verbose mode for debugging
```

---

## What RTK Does NOT Do

- ❌ Trim or reset the existing conversation context
- ❌ Summarise previous assistant turns
- ❌ Drop old tool call results from history
- ❌ Replace task boundary discipline

RTK reduces the *size* of each individual tool result before it enters context.  
`task-boundaries` prevents *unnecessary* tool calls. `done-signal-reset` bounds sessions at completion.  
All three together are what keep Pi stable on large codebases with local LLMs.
