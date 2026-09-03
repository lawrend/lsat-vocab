# LawrenceLSAT Vocabulary — flashcards

A one-page spaced-repetition drill. No accounts, no server, no build step. Four files:

| File | What it is |
| --- | --- |
| `index.html` | The whole app: landing page, drill, styles, scheduler. |
| `cards.js` | The deck: `window.VOCAB_CARDS = [{word, definition, partOfSpeech}]`. |
| `context.js` | One example sentence per word: `window.VOCAB_CONTEXT = {word: sentence}`. |
| `make_cards.py` | Turns the tutoring app's `vocab.json` into `cards.js`. Stdlib only. |

`cards.js` in this repo was generated from the tutoring app's `vocab.json`; regenerate it whenever
that file gains words. `context.js` is written by hand and no script ever overwrites it.

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

It also reads `context.js` — without writing it — and names any word that has no example sentence
yet, so a word added to `vocab.json` doesn't quietly ship without one.

## Test it

Double-click `index.html`. It works from `file://` — `cards.js` is a script tag, not a fetch, so
there is nothing to serve.

## Publish it (GitHub Pages)

1. New repository, public, e.g. `lsat-vocab`.
2. Upload `index.html`, `cards.js` and `context.js`. (`make_cards.py` and this README can come
   along or not.)
3. Settings → Pages → Source: *Deploy from a branch* → `main` / root → Save.
4. A minute later it is at `https://<you>.github.io/lsat-vocab/`. Send students the link.

Free tier requires the repo be public. That's fine here — words and your own definitions, no
licensed material. A custom domain (`vocab.yourdomain.com`) is free under Settings → Pages.

## Update it

Re-run `make_cards.py`, write a sentence into `context.js` for anything it lists as missing, and
commit both. Students get the new words on their next visit.
**Their progress survives** — it is keyed by the word itself, not by position in the file. Removing
a word from the deck leaves a harmless orphan entry in their browser storage.

## What students should know

- Progress lives in that browser on that device. Different phone, different progress. No accounts,
  no sync, nothing leaves the device.
- Clearing site data erases it, as does Safari's automatic 7-day purge for sites they don't revisit
  — the fix is to visit it, which is the behavior you want anyway.
- Adding it to the home screen makes it look and open like an app.

## The landing page

The app opens on a landing page rather than straight into a card. It shows where you
are — *2 due today*, *All caught up*, or the deck size on a first visit — a **Start**
button, and three tabs:

| Tab | What is on it |
| --- | --- |
| **Progress** | The counts, new-words-per-day, erase progress, and Share. |
| **How it works** | Spaced repetition in plain words, how to grade honestly, what the context sentence costs, and how to add the app to a phone's home screen. |
| **About** | Douglas Lawrence, Lawrence LSAT Preparation, and how to get in touch. |

**Home** in the drill's top bar goes back. The queue survives the round trip, so
stepping out to check your numbers mid-session and pressing **Start** again puts you
back on the card you left — it only rebuilds when there is nothing left over.

The Progress tab and the drill's **Settings** button show the same element: there is one
`#panel` in the document and the view switcher moves it between them. The stats and the
controls are therefore written once, and Share is in both places without being built
twice.

## Share

**Share** hands the page to `navigator.share` where the browser has it — the native sheet
on a phone, with the recipient's own apps in it. Where it does not, it opens a small row
with the link, a **Copy link** button and **Email** / **Text** links.

The link is taken from the address bar, so a custom domain shares itself correctly with
no change here. Opened from a `file://` path there is no address to take, and it falls
back to the published GitHub Pages URL — the one constant in `index.html` that needs
editing if the site ever moves.

## Used in context

Every card has a **Used in context** button (keyboard: `c`) that shows the word in a sentence, with
the word itself marked. The sentences are original, written for this deck. Nothing in `context.js`
is quoted from an LSAT question, and the file carries no citation, question id or PrepTest label —
the same rule `make_cards.py` follows for `cards.js`.

## The scheduler

SM-2, the algorithm Anki used before FSRS. Ease starts at 2.5 and moves ±0.1–0.2 by grade, clamped
to [1.3, 2.7]. A new word answered *Good* comes back in 2 days, then at multiples of its ease.
*Again* resets the interval and puts the card back four positions later in the same session, so you
can't leave a word you just missed.

Daily new-word intake defaults to 10 and is adjustable under Settings. That cap is what stops 230
words from arriving in one evening and coming due together forever after.

### What the sentence costs

**When** the sentence is read is what matters, not whether it was read.

| | Interval | Ease |
| --- | --- | --- |
| Sentence read **before** the definition | capped at *Hard* | frozen |
| Sentence read **after** the definition | unaffected | unaffected |
| *Again*, either way | full lapse | −0.2 as usual |

A definition recalled with help is not the same observation as one recalled cold. The grade it
produces overstates how well the word is known, and a scheduler that can't tell the two apart keeps
pushing the next review further out on the strength of answers the student didn't really give —
confidently wrong in the direction of forgetting. So a helped answer is capped at the *Hard*
interval: the card still advances, because partial retrieval is still retrieval, but it can't claim
the ease multiplier that an unaided *Good* earns. The grade buttons show the capped numbers, so all
of *Hard*, *Good* and *Easy* read the same, and a line under them says why.

Ease is left alone rather than penalized. It's a long-run estimate of how hard this word is for this
student, built out of clean observations, and one contaminated observation shouldn't move it in
either direction. Only *Again* — which means the same thing with or without help — pulls it down.

Capping rather than forcing *Again* is the whole point. If the sentence cost a card its history,
students would stop opening it, and the alternative to opening it isn't better recall — it's
guessing, grading yourself generously, and moving on. Help that improves encoding should be cheap;
only the claim about memory that it contaminates gets priced. Reading the sentence after the
definition is already showing costs nothing at all, because by then the retrieval attempt is over.

Settings counts how many words have ever needed the sentence, which is a fair list of what to go
over in a session.
