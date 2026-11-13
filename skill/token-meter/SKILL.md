---
name: token-meter
description: Mostra in cima a ogni risposta una barra compatta di 10 quadrati colorati con una stima dei token (contesto) rimasti nella conversazione. Usa SEMPRE questa skill quando l'utente parla di token rimasti, contesto residuo, limite della conversazione, "quanto spazio mi resta", barra di avanzamento dei token, o chiede un indicatore/widget di consumo, anche se non nomina la skill. Show a 10-square colored bar with remaining-token estimate at the top of every reply. Use when the user mentions remaining tokens, context left, usage meter, or token widget.
---

# Token Meter

Indicatore minimale dei token rimasti: una barra di 10 quadrati colorati, mostrata come **prima riga di ogni risposta**.

## Importante: è una stima

Claude non ha un contatore esatto dei token residui. Il valore va stimato e va sempre presentato con il simbolo `~`. Non presentarlo mai come un dato preciso.

## Come stimare

1. **Finestra totale**: usa la dimensione del contesto del modello se la conosci. In caso contrario assumi **200.000 token**. (Per cambiare il default, modifica questo numero.)
2. **Token usati**: stima il testo dell'intera conversazione (messaggi dell'utente, tue risposte, output dei tool, contenuto di file allegati, istruzioni di sistema) con la regola **~4 caratteri = 1 token** (circa 3 per codice, italiano e testo denso).
3. **Rimasti** = totale − usati, in percentuale sul totale (arrotonda a multipli di 10 per i quadrati, al 5% per il numero mostrato).

## Come disegnare la barra

Quadrati pieni = percentuale rimasta ÷ 10, arrotondata. I restanti sono vuoti `⬜`.

Il colore dei quadrati pieni dipende da quanto resta:

| Rimasto | Quadrati pieni |
|---|---|
| più del 60% | 🟩 |
| tra 30% e 60% | 🟨 |
| meno del 30% | 🟥 |

Formato esatto della riga (una sola riga, nient'altro):

```
🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ ~70% · ~140k token rimasti
```

Esempi:

```
🟨🟨🟨🟨⬜⬜⬜⬜⬜⬜ ~40% · ~80k token rimasti
🟥🟥⬜⬜⬜⬜⬜⬜⬜⬜ ~20% · ~40k token rimasti
```

## Regole di comportamento

- La barra è **sempre la prima riga** della risposta, seguita da una riga vuota e poi dalla risposta normale.
- Niente commenti sulla barra, a meno che l'utente non li chieda.
- Sotto il **15%** aggiungi, dopo la risposta, una sola riga: suggerisci di aprire una nuova conversazione e offriti di scrivere un breve riassunto da portare con sé.
- Se l'utente scrive "nascondi la barra" (o simili), smetti di mostrarla; riprendi se scrive "mostra la barra".
- Se l'utente chiede "quanti token mi restano?", rispondi con la barra e spiega in una frase che si tratta di una stima.
- Se la risposta è un file o un artifact, mostra la barra solo nel testo di chat che lo accompagna, mai dentro il file.
