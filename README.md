# Claude Token Meter

**English** | [Italiano](README.it.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![Platform](https://img.shields.io/badge/platform-claude.ai%20%7C%20Claude%20Code-lightgrey)

**See how much context is left in your Claude conversation.**
A colored 10-square bar for claude.ai (as a skill) and for Claude Code (as a status line).

```
🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ ~70% · ~140k tokens left     claude.ai (estimate)
🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ 70% · 140k left · Opus        Claude Code (real data)
```

---

## Overview

Claude Token Meter ships two independent components for two different environments:

| | Where | Values | Position |
|---|---|---|---|
| **Skill** (`skill/`) | claude.ai and the apps | estimate made by Claude (~4 characters = 1 token) | first line of every reply |
| **Status line** (`claude-code/`) | Claude Code | real data provided by Claude Code | fixed bar in the terminal |

The bar always has 10 squares: filled squares = percentage left ÷ 10, the rest are empty.

| Left | Color |
|------|-------|
| more than 60% | 🟩 |
| between 30% and 60% | 🟨 |
| less than 30% | 🟥 |

---

## Features

- **Two versions, one look** — the same bar on claude.ai (estimate) and in Claude Code (real numbers).
- **Real data in Claude Code** — reads `context_window` from the JSON that Claude Code passes on stdin.
- **Automatic fallback** — if your Claude Code version does not provide those fields, the usage is computed from the last `usage` entry of the transcript; with no data at all it shows 100%.
- **Window size aware** — the size is read from Claude Code; if missing it is deduced from the model name (1M variants) and otherwise defaults to 200k.
- **Low-context warning** — the skill suggests starting a new chat with a summary when less than 15% is left.
- **Bilingual** — the status line follows the system locale (Italian / English) or `TOKEN_METER_LANG`.
- **Switch it off** — tell Claude "hide the bar" (or "nascondi la barra") and it stops showing it.
- **No dependencies** — the script uses the Python standard library only.

---

## Requirements

- **Skill:** a claude.ai account with Skills enabled (Settings → Capabilities).
- **Status line:** Claude Code and **Python 3.8+**. No external packages.

---

## Installation

```bash
git clone https://github.com/MrGodLink/Claude-Token-Meter.git
cd Claude-Token-Meter
```

### 1. Skill for claude.ai

1. Upload [`releases/token-meter.skill`](releases/token-meter.skill) in Settings → Capabilities → Skills (or zip the `skill/token-meter/` folder and upload the `.zip`).
2. Open a new chat and ask "how many tokens do I have left?".

**To get the bar on every reply**, skills are loaded by Claude only when it considers them useful, so the bar may not appear in every message. Paste this text in Settings → Profile → personal preferences (it applies to new chats only):

```
Start every reply with a bar of 10 squares estimating the context tokens left in the conversation (200k window, about 4 characters = 1 token). Filled squares = percentage left ÷ 10, the rest ⬜. Color of the filled ones: 🟩 if more than 60% is left, 🟨 between 30% and 60%, 🟥 below 30%. Format: 🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ ~70% · ~140k tokens left. That line only, then a blank line and the reply. If less than 15% is left, suggest opening a new chat with a summary.
```

> The skill text is written in Italian, so its bar reads "token rimasti". To change the wording, edit `SKILL.md` before uploading, or use the preferences text above.

### 2. Status line for Claude Code

1. Copy `claude-code/token_meter_statusline.py` to `~/.claude/` (on macOS/Linux: `chmod +x`).
2. Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/token_meter_statusline.py"
  }
}
```

3. Restart Claude Code. On Windows use `python` and the full path.

---

## Usage

Manual test of the status line:

```bash
echo '{"model":{"display_name":"Opus"},"context_window":{"remaining_percentage":40,"context_window_size":200000}}' | python3 claude-code/token_meter_statusline.py
# 🟨🟨🟨🟨⬜⬜⬜⬜⬜⬜ 40% · 80k left · Opus
```

### Customization

| What | Skill | Status line |
|------|-------|-------------|
| Color thresholds | table in `SKILL.md` | `GREEN_ABOVE`, `YELLOW_ABOVE` |
| Default window | "Come stimare" section | `DEFAULT_WINDOW` (200,000) |
| Language | edit `SKILL.md` | `TOKEN_METER_LANG=en` or `it` |

---

## Architecture

```
Claude-Token-Meter/
├── skill/
│   └── token-meter/
│       └── SKILL.md                   # the skill (instructions for Claude)
├── claude-code/
│   └── token_meter_statusline.py      # status line script
├── releases/
│   └── token-meter.skill              # ready-to-upload package
├── LICENSE
├── README.md
└── README.it.md
```

### `token_meter_statusline.py`

- `main()` — reads the JSON from stdin, picks the best data source, draws the bar.
- `usage_tokens(usage)` — input + cache creation + cache read tokens of one API call.
- `used_from_transcript(path)` — fallback: last `usage` entry of the JSONL transcript.
- `detect_language()` — `TOKEN_METER_LANG`, then the system locale.
- The script never writes anything and never touches the network.

---

## Data sources

| Priority | Source | Used for |
|----------|--------|----------|
| 1 | `context_window.remaining_percentage` / `used_percentage` (stdin) | percentage left |
| 2 | `context_window.current_usage` + `context_window_size` (stdin) | computed percentage |
| 3 | last `usage` entry in the file at `transcript_path` | fallback |
| — | `model.display_name`, `model.id` | label and 1M window detection |

The skill has no data source: Claude estimates the size of the conversation itself, which is why the value is shown with `~`.

---

## Limitations

- On claude.ai Claude has no exact counter: the value is an estimate and can drift from reality.
- The skill is not a fixed widget: the bar is text and scrolls with the chat.
- The fields passed to the status line may change between Claude Code versions.

---

## Privacy and responsible use

- The status line makes **no network requests**. It reads the JSON from stdin and, only as a fallback, the transcript file whose path Claude Code provides (read-only).
- The skill is plain text instructions: nothing is sent anywhere by this project.
- This is an independent community project, not affiliated with or endorsed by Anthropic.

---

## Credits

Created by **Raffaele Catapano** — [github.com/MrGodLink](https://github.com/MrGodLink)

If you reuse, modify or redistribute this project, please keep the copyright notice and credit the original author, as required by the MIT License.

Bug reports and ideas are welcome in the [issue tracker](https://github.com/MrGodLink/Claude-Token-Meter/issues).

## License

The source code is released under the MIT License — see [LICENSE](LICENSE).
