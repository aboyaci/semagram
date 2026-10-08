# Grammar (v0.3)

The whole grammar fits on a page. That is the point.

## 1. Glyphs and words

- **One glyph is one word**, by default.
- There are no word separators. A sentence ends with **🔷** and nothing else. One sentence per line is house style, so a line wrap can never break anything.
- A glyph plus a run of **modifiers** is one word. Modifiers always attach to the word on their left: `❌ 🌑 🌘 🌗 🌔 🌕 🐘 🐜 📈 📉 ⬆️ ⬇️ 👍 👎 ‼️ 📜 ⏪ ⏩`. `🐭🔬🌕❌` is one word: *not all lab mice*.
- A modifier with nothing on its left is the **predicate** (`⬆️🐦🌊🔷` = the bird is above the sea).
- **Reduplication is plural**: `🙋🙋` we, `🐭🐭` mice.
- **Root + root compounds are dictionary words** (`💬🦋` translation, `🧠📈` learn). Head first. Under the no-break rule they must be declared, in the core dictionary or in the document's pack with `≔`, before a reader can be expected to segment them. Free compounding is dead.
- A word has at most **3 roots**, modifiers not counted.
- Connectives and math operators **glue** their neighbours into one word, so `👀∧👈🌑` (attention and nothing else) is a single argument.

## 2. Sentence

```
[opener] [speaker💬] predicate agent patient 🔷
```

Every slot but the predicate is optional. The predicate is **always the first content word**, which gives a cold reader one fixed anchor to parse from.

- `👁️🐟🐦🔷` see(fish, bird)
- `💤🐭🔷` sleep(mouse)
- `🐭👉🔷` mouse(this): *this is a mouse*. Zero copula, for free.
- `📥🐟🌊🔷` in(fish, sea). Location words are two-place predicates; no role marker is needed.
- `👍📈🤖👈🌕🔷` better(Transformer, all-others). A comparative is a two-place predicate; no "than".

Roles come from position, not markers. Anything beyond three arguments is a second sentence.

## 3. Openers

A sentence may start with one opener. It inherits the confidence of the previous sentence.

| | |
|---|---|
| ➡️ | so, therefore |
| ⬅️ | because |
| 🔀 | but |
| ∧ ∨ | and, or (inclusive) |
| 🔺 | if (the consequence is the next sentence) |
| 🟡 🔴 | we think / we guess (see §6) |

## 4. Speaker labels

`X💬` at the start of a sentence means *X says*, scoping to 🔷. It replaces quotation marks and brackets, and repeats for every sentence of a speech (repetition is the method in a beginner text; quotes are rare in a paper).

A mental root may sit before 💬: `🐟💭💬` the fish thinks, `🙋🙋🧠💬` we know, `🙋🙋🧠❌💬` we do not know whether. This is also how **claims about claims** are made: nothing is ever asserted by accident, because the label comes first.

- `🙋🙋🧠❌💬 P🔷` — we don't know whether P
- `🙋🙋🧠💬 P❌🔷` — we know not-P

## 5. Negation

**❌ is postfix. It ends a word and negates the whole word.** Think of a cancel stamp.

- `🐭❌` non-mouse · `🐭🔬❌` not a lab mouse · `💪❌` cannot
- `💤🐭🌕❌🔷` — not all mice sleep
- `💤❌🐭🌕🔷` — all mice don't sleep
- `❌` alone in the patient slot is *the false*: `🗣️🐟❌🔷` the fish says something false.

❌ also covers *no* and *false*, since "not P" and "P is false" are one statement. The one carve-out is *no* as a quantity, which is `🌑`: `💤🐭🌑🔷` zero mice slept. Never use ❎ (green on some platforms).

## 6. Time and confidence

- **Tense is optional and sticky.** Present is unmarked. `⏪🔷` as a one-word sentence sets the past frame for everything after it; `🕐👉🔷` (*now*) resets; `⏩🔷` sets the future. ⏪ and ⏩ may also trail a word: `🏆⏪` the previous best, `👍⏪` was good.
- There is no aspect, no mood, no voice. Passive does not exist; put the agent in the agent slot or leave it empty.
- **Fact unless said otherwise.** An unmarked sentence is asserted. `🟡` opens *we think*, `🔴` opens *a guess*. `🟡` is shorthand for `🙋💭💬`.

## 7. Quantity and degree

| proportion (moon scale) | count | degree |
|---|---|---|
| 🌑 none · 🌘 a small part · 🌗 half · 🌔 most · 🌕 all | 🧮🐘 many · 🧮🐜 few · numerals | 📈 more · 📉 less · ‼️ very |

*Some* = `🌑❌` (not none), the honest existential. Dimension + 🐘/🐜 is a pattern: `🕐🐘` long time, `📏🐘` far, `🧮🐘` many; decode one and you have all three. `📏🌑` (zero distance) is *touching*.

## 8. Reference

- `👉` *this / it* points at a thing or at the whole previous sentence. It is how a pidgin avoids nesting, and the most context-dependent glyph in the language.
- `👈` *other*. Not derivable from `🟰❌` (different): the other mouse can be identical. `👈🌕` all others; `X∧👈🌑` only X.
- `🏷️` is a cartouche: the Latin text after it is a proper name, read as one word.
- `📜` is a determinative, Egyptian style: `🧠📈📜` *learning*, the abstraction of *learn*.

## 9. Foreign scripts

Numbers and mathematics are an embedded foreign script with their own rules, exactly as Hindu-Arabic numerals are inside Japanese or Arabic text: `28.4`, `>`, `+`, `∃ ∧ ∨ ≔ ∥`. Latin letters appear only after 🏷️.

## 10. What context may do

Context may fill in what is omitted (number, tense, the standard of a comparison, who "it" is). Context may **not** choose between readings that contradict each other. Negation scope, quantifiers and the agent/patient distinction are never left to context.

## 11. Names

`🏷️` is a cartouche: the text after it, in any script, is a proper name read as one word. Put a **category glyph** in front so a reader who cannot read the script still knows what kind of thing it is (Egyptian determinatives did exactly this):

```
👤🏷️Mehmet      person        📍🏷️İstanbul    place
👥🏷️Anthropic   group         📦🏷️Transformer thing
🐾🏷️Karabaş     animal
```

A name used more than twice is **bound once** at the top of the document and the glyph is used after that. Faces and person emoji, banned from the dictionary because their expressions are unstable, are fine here: the binding defines them.

```
👦 ≔ 👤🏷️Mehmet
🐕 ≔ 🐾🏷️Karabaş
👁️👦🐕🔷        Mehmet sees Karabaş
```

Never translate a name. *Karabaş* means "black head" and is one dog; `🐕⬛` would be any black dog. The cartouche says: take this whole.

## 12. Pronouns

There is one third-person pronoun, `👉`, covering he, she, it, this and that, as Turkish *o* does. There is no gender and none will be added: if a text needs to say someone is a woman it says so as a statement, which is information, not grammar.

When two referents compete, the category glyph disambiguates: `👤👉` the person, `📦👉` the thing, `🐾👉` the animal. These are optional, like tense. For anything that recurs across sentences, bind a glyph (§11) and use no pronoun at all. In technical text, `👉1`, `👉2` may index the previous sentence or the one before it; this is banned in stories.
