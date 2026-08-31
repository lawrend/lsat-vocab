# LSAT Vocabulary — flashcards

A one-page spaced-repetition drill. No accounts, no server, no build step. Three files:

| File | What it is |
| --- | --- |
| `index.html` | The whole app: markup, styles, scheduler. |
| `cards.js` | The deck: `window.VOCAB_CARDS = [{word, definition, partOfSpeech}]`. |
| `make_cards.py` | Turns the tutoring app's `vocab.json` into `cards.js`. Stdlib only. |

`cards.js` in this repo was generated from the tutoring app's `vocab.json`; regenerate it whenever
that file gains words.

## Build the deck

```
python3 make_cards.py ~/Desktop/TutoringApp/data/vocab.json
```

It prints which fields it used, e.g. `Using word = 'word', definition = 'definition'`. **Read that
line** — it is the only place the field-name guess is visible. If it guesses wrong, or can't find
the definition field at all, it lists every field with a sample value and you name the right one:

```
python3 make_cards.py path/to/vocab.json --def-field blurb
```

Citations, snippets, question ids and PrepTest labels are never copied. Only the word, its part of
speech, and its definition reach `cards.js`. Words with an empty definition are skipped and named
in the output.

## Test it

Double-click `index.html`. It works from `file://` — `cards.js` is a script tag, not a fetch, so
there is nothing to serve.

## Publish it (GitHub Pages)

1. New repository, public, e.g. `lsat-vocab`.
2. Upload `index.html` and `cards.js`. (`make_cards.py` and this README can come along or not.)
3. Settings → Pages → Source: *Deploy from a branch* → `main` / root → Save.
4. A minute later it is at `https://<you>.github.io/lsat-vocab/`. Send students the link.

Free tier requires the repo be public. That's fine here — words and your own definitions, no
licensed material. A custom domain (`vocab.yourdomain.com`) is free under Settings → Pages.

## Update it

Re-run `make_cards.py`, commit the new `cards.js`. Students get the new words on their next visit.
**Their progress survives** — it is keyed by the word itself, not by position in the file. Removing
a word from the deck leaves a harmless orphan entry in their browser storage.

## What students should know

- Progress lives in that browser on that device. Different phone, different progress. No accounts,
  no sync, nothing leaves the device.
- Clearing site data erases it, as does Safari's automatic 7-day purge for sites they don't revisit
  — the fix is to visit it, which is the behavior you want anyway.
- Adding it to the home screen makes it look and open like an app.

## The scheduler

SM-2, the algorithm Anki used before FSRS. Ease starts at 2.5 and moves ±0.1–0.2 by grade, clamped
to [1.3, 2.7]. A new word answered *Good* comes back in 2 days, then at multiples of its ease.
*Again* resets the interval and puts the card back four positions later in the same session, so you
can't leave a word you just missed.

Daily new-word intake defaults to 10 and is adjustable under Settings. That cap is what stops 230
words from arriving in one evening and coming due together forever after.
