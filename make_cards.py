#!/usr/bin/env python3
"""Build cards.js for the vocabulary flashcards from the tutoring app's vocab.json.

Stdlib only, same as server.py. Run it from anywhere:

    python3 make_cards.py ~/Desktop/TutoringApp/data/vocab.json

It writes cards.js next to this script. If it cannot work out which field holds
the definition, it prints every field it found with a sample value and stops,
so you can name the right one:

    python3 make_cards.py path/to/vocab.json --def-field meaning

Citations are never copied. Only the word, its part of speech, and its
definition reach the deck.

It never touches context.js -- the "Used in context" sentences are written by
hand -- but it does read it, and names any word that does not have one yet.
"""

import argparse
import json
import os
import sys

WORD_FIELDS = ["word", "term", "headword", "entry", "lemma", "vocab", "text", "w"]
DEF_FIELDS = [
    "definition", "def", "meaning", "gloss", "sense", "description",
    "definitionText", "definition_text", "shortDefinition", "body", "d",
]
POS_FIELDS = ["partOfSpeech", "part_of_speech", "pos", "speechPart", "type"]

# Fields we know are something else, so they never get mistaken for a definition.
NEVER = {"id", "createdAt", "created", "citations", "cites", "form", "snippet",
         "questionId", "label", "section", "optionKey", "tags", "notes"}


def entries_from(blob):
    """vocab.json may be a bare list or a dict wrapping one."""
    if isinstance(blob, list):
        return blob
    if isinstance(blob, dict):
        for key in ("vocab", "words", "entries", "items", "data"):
            if isinstance(blob.get(key), list):
                return blob[key]
        lists = [v for v in blob.values() if isinstance(v, list)]
        if len(lists) == 1:
            return lists[0]
    raise SystemExit("Could not find a list of words in that file.")


def pick(records, candidates, min_coverage=0.5):
    """Choose the first candidate field present on most records."""
    total = len(records)
    for name in candidates:
        filled = sum(
            1 for r in records
            if isinstance(r, dict) and isinstance(r.get(name), str) and r[name].strip()
        )
        if filled >= total * min_coverage:
            return name, filled
    return None, 0


def describe(records):
    keys = {}
    for r in records[:200]:
        if not isinstance(r, dict):
            continue
        for k, v in r.items():
            if k in keys:
                continue
            if isinstance(v, str):
                sample = v if len(v) <= 70 else v[:67] + "..."
                keys[k] = "str  " + repr(sample)
            elif isinstance(v, list):
                keys[k] = "list of %d" % len(v)
            else:
                keys[k] = type(v).__name__
    width = max(len(k) for k in keys) if keys else 0
    return "\n".join("  %-*s  %s" % (width, k, s) for k, s in sorted(keys.items()))


def context_words(path):
    """The words context.js already has a sentence for.

    Returns None when there is no context.js at all, which is a different fact
    from an empty one: no file means the button never appears in the app.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    try:
        return set(json.loads(text[text.index("{"):text.rindex("}") + 1]))
    except ValueError:
        print("Warning: could not read %s; skipping the sentence check." % path)
        return set()


def main():
    ap = argparse.ArgumentParser(description="Build cards.js from vocab.json")
    ap.add_argument("source", help="path to vocab.json")
    ap.add_argument("-o", "--out", default=None, help="output path (default: cards.js beside this script)")
    ap.add_argument("--word-field", default=None)
    ap.add_argument("--def-field", default=None)
    ap.add_argument("--pos-field", default=None)
    args = ap.parse_args()

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards.js")

    with open(args.source, "r", encoding="utf-8") as fh:
        records = entries_from(json.load(fh))
    records = [r for r in records if isinstance(r, dict)]
    if not records:
        raise SystemExit("That file has no word records in it.")

    print("Read %d entries from %s" % (len(records), args.source))

    word_field = args.word_field or pick(records, WORD_FIELDS, 0.9)[0]
    def_field = args.def_field
    if not def_field:
        candidates = DEF_FIELDS + [
            k for k in records[0].keys()
            if k not in NEVER and k != word_field and isinstance(records[0].get(k), str)
        ]
        def_field = pick(records, candidates, 0.5)[0]
    pos_field = args.pos_field or pick(records, POS_FIELDS, 0.5)[0]

    if not word_field or not def_field:
        print("\nCould not identify the %s field. Fields present:\n"
              % ("word" if not word_field else "definition"))
        print(describe(records))
        print("\nRe-run naming it, e.g.:  python3 %s %s --def-field meaning"
              % (os.path.basename(__file__), args.source))
        sys.exit(1)

    print("Using  word = %r,  definition = %r%s"
          % (word_field, def_field, ",  part of speech = %r" % pos_field if pos_field else ""))

    cards, skipped, seen = [], [], set()
    for r in records:
        word = (r.get(word_field) or "").strip()
        definition = (r.get(def_field) or "").strip()
        if not word:
            continue
        if not definition:
            skipped.append(word)
            continue
        key = word.lower()
        if key in seen:
            continue
        seen.add(key)
        card = {"word": word, "definition": definition}
        if pos_field and (r.get(pos_field) or "").strip():
            card["partOfSpeech"] = r[pos_field].strip()
        cards.append(card)

    cards.sort(key=lambda c: c["word"].lower())

    body = json.dumps(cards, ensure_ascii=False, indent=1)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("// Generated by make_cards.py from vocab.json. Do not edit by hand.\n")
        fh.write("window.VOCAB_CARDS = %s;\n" % body)

    print("Wrote %d cards to %s" % (len(cards), out))

    have = context_words(os.path.join(os.path.dirname(os.path.abspath(out)), "context.js"))
    if have is None:
        print("No context.js beside it, so the 'Used in context' button stays hidden.")
    else:
        gaps = [c["word"] for c in cards if c["word"] not in have]
        if gaps:
            shown = ", ".join(gaps[:8])
            print("No context sentence yet for %d word%s: %s%s\n"
                  "  Write them into context.js by hand; this script never edits it."
                  % (len(gaps), "" if len(gaps) == 1 else "s", shown,
                     ", ..." if len(gaps) > 8 else ""))
        else:
            print("Every word has a context sentence.")

    if skipped:
        shown = ", ".join(skipped[:8])
        print("Skipped %d word%s with no definition: %s%s"
              % (len(skipped), "" if len(skipped) == 1 else "s", shown,
                 ", ..." if len(skipped) > 8 else ""))


if __name__ == "__main__":
    main()
