---
name: token-meter
description: Barra di 10 quadrati colorati con stima dei token di contesto rimasti, come prima riga di ogni risposta. Usala quando l'utente parla di token rimasti, contesto residuo, limite della conversazione, "quanto spazio mi resta", barra o widget di consumo token, o chiede di monitorare la lunghezza della chat. Shows a 10-square colored bar estimating remaining context tokens at the top of every reply. Use when the user mentions remaining tokens, context left, usage meter, or token widget.
---

# Token Meter

Indicatore dei token di contesto rimasti: barra di 10 quadrati, prima riga di ogni risposta.

## È una stima, non una misura

Non hai un contatore esatto. Presenta sempre i valori con `~`. Se l'utente chiede numeri esatti, spiega il limite in una frase e segnala che per dati reali esiste la status line di Claude Code.

## Metodo di stima (incrementale, non ricalcolare da zero)

1. **Baseline a inizio chat**: parti da ~8.000 token usati (istruzioni di sistema, preferenze, skill, eventuale knowledge base del progetto). È un'euristica, non un dato.
2. **A ogni turno**: prendi il valore stimato del turno precedente e aggiungi i token dei nuovi contenuti:
   - messaggio utente + tua risposta precedente + output di tool + testo di file allegati;
   - divisore: ~4 caratteri/token per prosa inglese, ~3 per italiano, codice e testo denso;
   - immagini: ~(larghezza × altezza) / 750 token per immagine (euristica approssimata).
3. **Monotonia**: nella stessa chat la percentuale rimasta non può aumentare. Se il calcolo la farebbe salire, mantieni il valore precedente. Eccezione: nuova chat o riassunto/compattazione dichiarati dall'utente.
4. Finestra totale: usa quella del modello se la conosci, altrimenti 200.000.
5. Clamp sempre tra 0% e 100%.

## Barra

- Quadrati pieni = ⌊percentuale rimasta ÷ 10⌋ (arrotondamento per difetto, conservativo). Vuoti: `⬜`.
- Numero mostrato: percentuale arrotondata al 5% più vicino.
- Colore dei pieni: 🟩 se rimasto > 60%; 🟨 se 30% ≤ rimasto ≤ 60%; 🟥 se rimasto < 30%.
- Lingua: segui la lingua dell'utente. Italiano: `token rimasti`. Inglese: `tokens left`.

Formato esatto (una sola riga):

🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ ~70% · ~140k token rimasti
🟨🟨🟨🟨⬜⬜⬜⬜⬜⬜ ~40% · ~80k tokens left
🟥🟥⬜⬜⬜⬜⬜⬜⬜⬜ ~20% · ~40k token rimasti

## Regole di comportamento

1. La barra è la prima riga, poi una riga vuota, poi la risposta. Niente commenti sulla barra salvo richiesta.
2. **Precedenza**: se l'utente impone un formato rigido alla risposta (solo JSON, solo codice, contenuto di un file/artifact), ometti la barra in quell'output. Mai dentro file o artifact; solo nel testo di chat che li accompagna.
3. Sotto il 15%: aggiungi in fondo una sola riga che suggerisce una nuova chat con riassunto, **una sola volta per attraversamento della soglia**, non a ogni turno.
4. "Nascondi la barra" (o simili) → smetti per il resto della chat; "mostra la barra" → riprendi.
5. "Quanti token mi restano?" → barra + una frase che chiarisce che è una stima.