#!/usr/bin/env python3
"""
check_loop.py — Loop detection helper for Pi coding agent.

Pi can call this script from a shell step to track whether it's
repeating the same actions.

Usage:
    # Record an action
    python check_loop.py record "edit src/auth.py add_login_function"

    # Check if the last N actions show a loop
    python check_loop.py check

    # Reset the session log (call at task start)
    python check_loop.py reset

    # Show full history
    python check_loop.py history
"""

import sys
import json
import hashlib
import os
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.pi/loop-guard-session.json")
MAX_HISTORY = 50
LOOP_WINDOW = 5
LOOP_THRESHOLD = 3


def load_log():
    if not os.path.exists(LOG_FILE):
        return {"actions": [], "started": datetime.now().isoformat()}
    with open(LOG_FILE) as f:
        return json.load(f)


def save_log(data):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record(action: str):
    data = load_log()
    h = hashlib.md5(action.strip().lower().encode()).hexdigest()
    entry = {
        "action": action.strip(),
        "hash": h,
        "time": datetime.now().isoformat(),
    }
    data["actions"].append(entry)
    # Keep log bounded
    if len(data["actions"]) > MAX_HISTORY:
        data["actions"] = data["actions"][-MAX_HISTORY:]
    save_log(data)
    print(f"[loop-guard] Recorded: {action.strip()[:80]}")


def check():
    data = load_log()
    actions = data.get("actions", [])
    if len(actions) < LOOP_WINDOW:
        print("[loop-guard] STATUS: ok (not enough history yet)")
        return

    recent = actions[-LOOP_WINDOW:]
    hashes = [a["hash"] for a in recent]
    unique = len(set(hashes))
    dupes = LOOP_WINDOW - unique

    if dupes >= LOOP_THRESHOLD:
        print(f"[loop-guard] STATUS: LOOP_DETECTED")
        print(f"[loop-guard] {dupes}/{LOOP_WINDOW} recent actions are duplicates")
        print(f"[loop-guard] Repeated action: {recent[-1]['action'][:80]}")
        sys.exit(1)  # Non-zero exit so Pi knows to trigger recovery
    else:
        print(f"[loop-guard] STATUS: ok ({dupes}/{LOOP_WINDOW} dupes, threshold={LOOP_THRESHOLD})")


def reset():
    data = {"actions": [], "started": datetime.now().isoformat()}
    save_log(data)
    print("[loop-guard] Session log reset.")


def history():
    data = load_log()
    actions = data.get("actions", [])
    if not actions:
        print("[loop-guard] No history yet.")
        return
    print(f"[loop-guard] Session history ({len(actions)} actions):")
    for i, a in enumerate(actions, 1):
        print(f"  {i:>3}. {a['time'][11:19]}  {a['action'][:70]}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "record":
        if len(sys.argv) < 3:
            print("Usage: check_loop.py record <action description>")
            sys.exit(1)
        record(" ".join(sys.argv[2:]))

    elif cmd == "check":
        check()

    elif cmd == "reset":
        reset()

    elif cmd == "history":
        history()

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: record | check | reset | history")
        sys.exit(1)


if __name__ == "__main__":
    main()
