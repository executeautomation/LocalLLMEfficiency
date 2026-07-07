#!/usr/bin/env bash
# rtk_check.sh — verify RTK binary and Pi extension are set up correctly.
# Uses the RTK Pi extension (agent/extensions/rtk.ts) — NOT shell wrappers.

set -e

echo "=== RTK Setup Check for Pi (extension mode) ==="
echo ""

# 1. Check RTK binary
if ! command -v rtk &>/dev/null; then
  echo "❌ RTK not found in PATH."
  echo "   Install with: brew install rtk"
  echo "   Or: curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"
  exit 1
fi

# 2. Verify it's Rust Token Killer (rtk rewrite must exist), not Adobe Type Kit
rtk rewrite "ls" &>/dev/null
REWRITE_EXIT=$?
if [ $REWRITE_EXIT -le 1 ]; then
  echo "✅ RTK (Rust Token Killer) with 'rtk rewrite' is available."
else
  echo "❌ 'rtk rewrite' failed — may be Adobe Type Kit or RTK < 0.23.0."
  echo "   Uninstall the wrong one and install from: https://github.com/rtk-ai/rtk"
  exit 1
fi

# 3. Show version
VERSION=$(rtk --version 2>/dev/null || echo 'unknown')
echo "   Version: $VERSION"
echo ""

# 4. Check minimum version (need >= 0.23.0 for rtk rewrite)
MINOR=$(echo "$VERSION" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 | cut -d. -f2 || echo "0")
if [ "${MINOR:-0}" -lt 23 ] 2>/dev/null; then
  echo "⚠️  RTK version may be too old (need >= 0.23.0 for 'rtk rewrite')"
else
  echo "✅ RTK version is sufficient for Pi extension."
fi
echo ""

# 5. Check Pi extension file exists
EXTENSION_PATH="$HOME/.pi/agent/extensions/rtk.ts"
if [ -f "$EXTENSION_PATH" ]; then
  echo "✅ Pi RTK extension found: $EXTENSION_PATH"
else
  echo "❌ Pi RTK extension NOT found at: $EXTENSION_PATH"
  echo "   The extension auto-rewrites bash commands — no shell wrappers needed."
fi
echo ""

# 6. Confirm no shell wrappers needed
echo "ℹ️  Shell wrappers (git/ls/grep in ~/.zshrc) are NOT needed."
echo "   The Pi extension (rtk.ts) rewrites commands automatically via 'rtk rewrite'."
echo ""

# 7. Show current savings
echo "=== Token savings so far ==="
rtk gain 2>/dev/null || echo "  (No data yet — run some commands first)"
echo ""

echo "=== Done. RTK extension is ready for Pi sessions. ==="
