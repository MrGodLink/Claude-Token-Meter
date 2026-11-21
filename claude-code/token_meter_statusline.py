#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
#  Project   : Claude Token Meter
#  Author    : Raffaele Catapano
#  License   : MIT (SPDX-License-Identifier: MIT)
#  Version   : 1.1.0 - Claude Code Status Line
#  Updated   : 21/11/2026
# =============================================================================
"""
Claude Token Meter - status line for Claude Code.
Reads session JSON from stdin, prints one line, e.g.:
🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ 70% · 140k left · Opus
Language: TOKEN_METER_LANG=en|it, else system locale. Stdlib only, Python 3.8+.
"""
import json
import math
import os
import re
import sys

DEFAULT_WINDOW = 200_000
GREEN_ABOVE = 60          # green if remaining > 60
YELLOW_ABOVE = 30         # yellow if remaining >= 30 (30 included), else red
TAIL_BYTES = 1_048_576    # transcript fallback: read only the last 1 MiB
LABELS = {"en": "left", "it": "rimasti"}
ONE_M_RE = re.compile(r"\[1m\]|\b1m\b", re.IGNORECASE)


def detect_language():
    forced = (os.environ.get("TOKEN_METER_LANG") or "").strip().lower()[:2]
    if forced in LABELS:
        return forced
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = (os.environ.get(var) or "").strip().lower()
        if value:
            return "it" if value.startswith("it") else "en"
    return "en"


def as_number(value):
    """Coerce to finite float; None on bool/str-garbage/NaN/Inf."""
    if isinstance(value, bool):
        return None
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def usage_tokens(usage):
    """Prompt tokens of one API call; accepts dict or plain number."""
    if not isinstance(usage, dict):
        return as_number(usage)
    total = 0.0
    for key in ("input_tokens", "cache_creation_input_tokens",
                "cache_read_input_tokens"):
        n = as_number(usage.get(key))
        if n is not None and n > 0:
            total += n
    return total if total > 0 else None


def used_from_transcript(path):
    """Fallback: last main-thread 'usage' from the JSONL transcript tail.
    Skips sidechain (subagent) entries; adds the last output_tokens because
    'usage' snapshots the prompt before that completion (approximation)."""
    if not isinstance(path, str) or not path:
        return None
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            length = f.tell()
            start = max(0, length - TAIL_BYTES)
            f.seek(start)
            chunk = f.read()
    except OSError:
        return None
    lines = chunk.decode("utf-8", errors="replace").splitlines()
    if start > 0 and lines:
        lines = lines[1:]  # first line may be truncated mid-JSON
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict) or entry.get("isSidechain"):
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        usage = message.get("usage")
        tokens = usage_tokens(usage)
        if tokens is not None:
            if isinstance(usage, dict):
                out = as_number(usage.get("output_tokens"))
                if out is not None and out > 0:
                    tokens += out
            return tokens
    return None


def fmt_tokens(n):
    if n >= 1_000_000 or round(n / 1000) >= 1000:
        v = f"{n / 1_000_000:.1f}"
        if v.endswith(".0"):
            v = v[:-2]
        return v + "M"
    if n >= 1000:
        return f"{round(n / 1000)}k"
    return str(int(n))


def compute_remaining(data):
    model = data.get("model")
    model = model if isinstance(model, dict) else {}
    cw = data.get("context_window")
    cw = cw if isinstance(cw, dict) else {}

    size = as_number(cw.get("context_window_size"))
    if size is None or size <= 0:
        ident = "{} {}".format(model.get("id") or "",
                               model.get("display_name") or "")
        size = 1_000_000 if ONE_M_RE.search(ident) else DEFAULT_WINDOW

    pct = as_number(cw.get("remaining_percentage"))
    if pct is None:
        used_pct = as_number(cw.get("used_percentage"))
        if used_pct is not None:
            pct = 100.0 - used_pct
    if pct is None:
        used = usage_tokens(cw.get("current_usage"))
        if used is not None:
            pct = 100.0 - used / size * 100.0
    if pct is None:
        used = used_from_transcript(data.get("transcript_path"))
        if used is not None:
            pct = 100.0 - used / size * 100.0
    if pct is None:
        pct = 100.0
    return max(0.0, min(100.0, pct)), size, model


def render(pct, size, model):
    filled = int(pct // 10)  # floor: conservative, no banker's rounding
    if pct > GREEN_ABOVE:
        square = "🟩"
    elif pct >= YELLOW_ABOVE:
        square = "🟨"
    else:
        square = "🟥"
    bar = square * filled + "⬜" * (10 - filled)
    parts = [f"{bar} {math.floor(pct)}%",
             f"{fmt_tokens(size * pct / 100.0)} {LABELS[detect_language()]}"]
    name = model.get("display_name") or ""
    if name:
        parts.append(str(name))
    return " · ".join(parts)


def main():
    # Force UTF-8 on piped stdout/stderr (Windows cp1252 would crash on emoji).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    raw = ""
    try:
        if not sys.stdin.isatty():  # manual run without pipe: don't block
            raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except (OSError, ValueError, AttributeError):
        raw = ""
    try:
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            data = {}
    except json.JSONDecodeError:
        data = {}
    try:
        pct, size, model = compute_remaining(data)
        line = render(pct, size, model)
    except Exception:
        line = "⬜" * 10 + " ?"  # degraded mode, never crash the status line
    try:
        print(line)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()