#!/usr/bin/env python3
#
# =============================================================================
#  Project      : Claude Token Meter
#  Description  : Colored 10-square bar showing the context tokens left in a
#                 Claude Code session (status line, Linux / Windows / macOS)
#  Author       : Raffaele Catapano
#  License      : MIT (see LICENSE)
#  Created on   : 13/11/2026
#  Updated on   : 13/11/2026
#  Version      : 1.0.0 - Claude Code Status Line
#
#  Copyright (c) 2026 Raffaele Catapano
#  Released under the MIT License - see the LICENSE file for details.
#  SPDX-License-Identifier: MIT
# =============================================================================
"""
Claude Token Meter - status line for Claude Code.
Reads the session JSON from stdin and prints one line, e.g.:

    🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ 70% · 140k left · Opus

Language: set TOKEN_METER_LANG=en|it, otherwise it follows the system locale
(Italian if the locale starts with "it", English otherwise).
"""
import json
import os
import sys

DEFAULT_WINDOW = 200_000      # used only if Claude Code does not report the size
GREEN_ABOVE = 60              # % left above which the bar is green
YELLOW_ABOVE = 30             # % left above which the bar is yellow (below: red)

LABELS = {"en": "left", "it": "rimasti"}


def detect_language():
    """Return 'it' or 'en' from TOKEN_METER_LANG or the system locale."""
    forced = (os.environ.get("TOKEN_METER_LANG") or "").lower()[:2]
    if forced in LABELS:
        return forced
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = (os.environ.get(var) or "").lower()
        if value:
            return "it" if value.startswith("it") else "en"
    return "en"


def usage_tokens(usage):
    """Tokens actually in the context for one API call."""
    return (
        (usage.get("input_tokens") or 0)
        + (usage.get("cache_creation_input_tokens") or 0)
        + (usage.get("cache_read_input_tokens") or 0)
    )


def used_from_transcript(path):
    """Fallback: read the last 'usage' entry from the JSONL transcript."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, TypeError):
        return None
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = (entry.get("message") or {}).get("usage")
        if usage:
            return usage_tokens(usage)
    return None


def fmt_tokens(n):
    return f"{n / 1000:.0f}k" if n >= 1000 else str(int(n))


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}

    model = data.get("model") or {}
    cw = data.get("context_window") or {}

    size = cw.get("context_window_size")
    if not size:
        size = 1_000_000 if "[1m]" in (model.get("id") or "").lower() else DEFAULT_WINDOW

    # 1) percentage provided directly by Claude Code
    remaining_pct = cw.get("remaining_percentage")
    if remaining_pct is None and cw.get("used_percentage") is not None:
        remaining_pct = 100 - cw["used_percentage"]

    # 2) computed from the last real usage
    if remaining_pct is None and cw.get("current_usage"):
        used = usage_tokens(cw["current_usage"])
        remaining_pct = 100 - used / size * 100

    # 3) fallback: transcript
    if remaining_pct is None:
        used = used_from_transcript(data.get("transcript_path"))
        if used is not None:
            remaining_pct = 100 - used / size * 100

    if remaining_pct is None:        # no data yet (session just started)
        remaining_pct = 100

    remaining_pct = max(0, min(100, remaining_pct))
    remaining_tokens = size * remaining_pct / 100

    filled = round(remaining_pct / 10)
    if remaining_pct > GREEN_ABOVE:
        square = "🟩"
    elif remaining_pct > YELLOW_ABOVE:
        square = "🟨"
    else:
        square = "🟥"

    bar = square * filled + "⬜" * (10 - filled)
    label = LABELS[detect_language()]
    name = model.get("display_name") or ""
    parts = [f"{bar} {remaining_pct:.0f}%", f"{fmt_tokens(remaining_tokens)} {label}"]
    if name:
        parts.append(name)
    print(" · ".join(parts))


if __name__ == "__main__":
    main()
