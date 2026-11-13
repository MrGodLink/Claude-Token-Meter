# Claude Token Meter

[English](README.md) | **Italiano**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![Platform](https://img.shields.io/badge/platform-claude.ai%20%7C%20Claude%20Code-lightgrey)

**Scopri quanto contesto resta nella tua conversazione con Claude.**
Una barra colorata di 10 quadrati per claude.ai (come skill) e per Claude Code (come status line).

```
🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ ~70% · ~140k token rimasti     claude.ai (stima)
🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ 70% · 140k rimasti · Opus       Claude Code (dati reali)
```

---

## Panoramica

Claude Token Meter contiene due componenti indipendenti per due ambienti diversi:

| | Dove | Valori | Posizione |
|---|---|---|---|
| **Skill** (`skill/`) | claude.ai e app | stima di Claude (~4 caratteri = 1 token) | prima riga di ogni risposta |
| **Status line** (`claude-code/`) | Claude Code | dati reali forniti da Claude Code | barra fissa nel terminale |

La barra ha sempre 10 quadrati: quadrati pieni = percentuale rimasta ÷ 10, il resto sono vuoti.

| Rimasto | Colore |
|---------|--------|
| più del 60% | 🟩 |
| tra 30% e 60% | 🟨 |
| meno del 30% | 🟥 |

---

## Funzionalità

- **Due versioni, stesso aspetto** — la stessa barra su claude.ai (stima) e in Claude Code (numeri reali).
- **Dati reali in Claude Code** — legge `context_window` dal JSON che Claude Code passa su stdin.
- **Piano B automatico** — se la tua versione di Claude Code non fornisce quei campi, l'uso viene calcolato dall'ultimo `usage` del transcript; senza alcun dato mostra 100%.
- **Dimensione della finestra** — letta da Claude Code; se manca viene dedotta dal nome del modello (varianti 1M), altrimenti 200k.
- **Avviso contesto quasi pieno** — la skill suggerisce di aprire una nuova chat con un riassunto quando resta meno del 15%.
- **Bilingue** — la status line segue la lingua di sistema (italiano / inglese) oppure `TOKEN_METER_LANG`.
- **Disattivabile** — scrivi "nascondi la barra" e Claude smette di mostrarla.
- **Zero dipendenze** — lo script usa solo la libreria standard di Python.

---

## Requisiti

- **Skill:** un account claude.ai con le Skill abilitate (Impostazioni → Capacità).
- **Status line:** Claude Code e **Python 3.8+**. Nessun pacchetto esterno.

---

## Installazione

```bash
git clone https://github.com/MrGodLink/Claude-Token-Meter.git
cd Claude-Token-Meter
```

### 1. Skill per claude.ai

1. Carica [`releases/token-meter.skill`](releases/token-meter.skill) in Impostazioni → Capacità → Skill (oppure comprimi la cartella `skill/token-meter/` in `.zip` e carica quello).
2. Apri una nuova chat e chiedi "quanti token mi restano?".

**Per avere la barra in ogni risposta:** le skill vengono caricate da Claude solo quando le ritiene utili, quindi la barra può non comparire in ogni messaggio. Incolla questo testo in Impostazioni → Profilo → preferenze personali (vale solo per le chat nuove):

```
Inizia ogni risposta con una barra di 10 quadrati che stima i token di contesto rimasti nella conversazione (finestra di 200k, circa 4 caratteri = 1 token). Quadrati pieni = percentuale rimasta ÷ 10, il resto ⬜. Colore dei pieni: 🟩 se rimane più del 60%, 🟨 tra 30% e 60%, 🟥 sotto il 30%. Formato: 🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ ~70% · ~140k token rimasti. Solo quella riga, poi una riga vuota e la risposta. Se resta meno del 15%, suggerisci di aprire una nuova chat con un riassunto.
```

### 2. Status line per Claude Code

1. Copia `claude-code/token_meter_statusline.py` in `~/.claude/` (su macOS/Linux: `chmod +x`).
2. Aggiungi a `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/token_meter_statusline.py"
  }
}
```

3. Riavvia Claude Code. Su Windows usa `python` e il percorso completo.

---

## Utilizzo

Prova manuale della status line:

```bash
echo '{"model":{"display_name":"Opus"},"context_window":{"remaining_percentage":40,"context_window_size":200000}}' | python3 claude-code/token_meter_statusline.py
# 🟨🟨🟨🟨⬜⬜⬜⬜⬜⬜ 40% · 80k rimasti · Opus     (con lingua di sistema italiana)
```

### Personalizzazione

| Cosa | Skill | Status line |
|------|-------|-------------|
| Soglie dei colori | tabella in `SKILL.md` | `GREEN_ABOVE`, `YELLOW_ABOVE` |
| Finestra di default | sezione "Come stimare" | `DEFAULT_WINDOW` (200.000) |
| Lingua | modifica `SKILL.md` | `TOKEN_METER_LANG=en` oppure `it` |

---

## Architettura

```
Claude-Token-Meter/
├── skill/
│   └── token-meter/
│       └── SKILL.md                   # la skill (istruzioni per Claude)
├── claude-code/
│   └── token_meter_statusline.py      # script della status line
├── releases/
│   └── token-meter.skill              # pacchetto pronto da caricare
├── LICENSE
├── README.md
└── README.it.md
```

### `token_meter_statusline.py`

- `main()` — legge il JSON da stdin, sceglie la fonte dati migliore, disegna la barra.
- `usage_tokens(usage)` — token di input + creazione cache + lettura cache di una chiamata API.
- `used_from_transcript(path)` — piano B: ultimo `usage` del transcript JSONL.
- `detect_language()` — `TOKEN_METER_LANG`, poi la lingua di sistema.
- Lo script non scrive mai nulla e non usa mai la rete.

---

## Fonti dei dati

| Priorità | Fonte | Usata per |
|----------|-------|-----------|
| 1 | `context_window.remaining_percentage` / `used_percentage` (stdin) | percentuale rimasta |
| 2 | `context_window.current_usage` + `context_window_size` (stdin) | percentuale calcolata |
| 3 | ultimo `usage` nel file indicato da `transcript_path` | piano B |
| — | `model.display_name`, `model.id` | etichetta e rilevamento finestra 1M |

La skill non ha una fonte dati: Claude stima da solo la lunghezza della conversazione, per questo il valore è mostrato con `~`.

---

## Limiti

- Su claude.ai Claude non ha un contatore esatto: il valore è una stima e può scostarsi dalla realtà.
- La skill non è un widget fisso: la barra è testo e scorre con la chat.
- I campi passati alla status line possono cambiare tra le versioni di Claude Code.

---

## Privacy e uso responsabile

- La status line **non effettua richieste di rete**. Legge il JSON da stdin e, solo come piano B, il file di transcript il cui percorso è fornito da Claude Code (in sola lettura).
- La skill è fatta solo di istruzioni testuali: questo progetto non invia nulla da nessuna parte.
- È un progetto indipendente della community, non affiliato né approvato da Anthropic.

---

## Crediti

Creato da **Raffaele Catapano** — [github.com/MrGodLink](https://github.com/MrGodLink)

Se riutilizzi, modifichi o ridistribuisci questo progetto, mantieni la nota di copyright e cita l'autore originale, come richiesto dalla licenza MIT.

Segnalazioni di bug e idee sono benvenute nell'[issue tracker](https://github.com/MrGodLink/Claude-Token-Meter/issues).

## Licenza

Il codice sorgente è rilasciato con licenza MIT — vedi [LICENSE](LICENSE).
