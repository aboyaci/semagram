# Design rules

Every glyph and every compound has to pass these. They were not written up front; each one was forced by a specific failure (see [history.md](history.md)).

## Two tests

**Test A, compositional honesty.** A compound means exactly what its parts say. No idioms, no "close enough". `🌗` showed *half*, so it could not mean *some*. `🟰❌` says *not same*, which is *different*, so it could not mean *other*. `🗣️❌✅` says *say something untrue*, which covers honest mistakes, so it could not mean *lie*. Test A applies to meanings, not pictures: 🐘 means BIG, never elephant, so `🕐🐘` is honestly *time big*.

**Test B, guessability.** Applies to the pictures. Symbol research (the Blissymbols/AAC field) uses three tiers:

- **transparent**: guessable cold
- **translucent**: the link is obvious once told, and sticks
- **opaque**: arbitrary

Content roots must be translucent or better. Opaque is allowed only for a small, capped set of grammar particles. **Misleading is worse than opaque**: an opaque glyph sends the reader to the legend, a misleading one makes them confidently wrong. Reject far-miss readings (🤝 for *touch* reads as *agree*); tolerate near-miss (❤️ for *feel* reads as *love*).

## The seven rules

1. **Opposites get visually paired glyphs.** 👍👎 📈📉 ⬆️⬇️ ⏪⏩ ➡️⬅️ 👉👈 🐘🐜 🐇🐢. Decoding one half gives you the other.
2. **Scales are visible gradients.** Moon phases for proportion, traffic light for confidence.
3. **No glyph contains text.** 🆚 🆔 🆕 are out; so are keycap digits and flags. Letters are language-specific.
4. **Pictures are content, shapes are grammar.** Any pictorial emoji is a word; geometric and symbol emoji are reserved for particles. A closed list of eight reserved pictures (💬 🏷️ 📜 👉 👈 and the moons) bends this; a closed list is tolerable.
5. **Give a glyph the meaning people already read into it.** 💡 reads as *idea*, so it is idea and light became 🔦. 🤝 reads as *agree*, so it is.
6. **Glyph stability.** A glyph must render with the same meaning on every major platform. This killed every expression face (Miller et al. 2016: people disagree whether the *same* face is positive or negative across vendors), 🙏, 🔫, 🍑, and the ambiguous 🌙.
7. **No free compounding; a compound is a dictionary word.** Under the no-break rule the reader can only segment what they already know. A compound earns a dictionary slot when a translation needs it and the honest Layer 0 expression runs to 3+ roots or is ambiguous. The cap of 3 roots per word is absolute.

## Vocabulary layers

- **Layer 0**: the ~65 NSM semantic primes. Fixed. Everything else must ultimately be definable in them.
- **Layer 1**: core roots, 66 now, target ~120. A root gets in only if it is cross-linguistically basic (Swadesh list), frequent in the target genre, has a stable glyph, and its Layer 0 compound would be 3+ glyphs or ambiguous.
- **Layer 2**: domain packs, unbounded, declared per document with `≔`. Core beats pack: if a pack reuses a core glyph the pack loses (📥📤 as encoder/decoder had to rebind to `📖⚙️ ✍️⚙️`).

Growth is **evidence-driven**: no word enters Layer 1 from an armchair. The two texts translated so far produced exactly these promotions: 🏆 *best*, 🐣 *new*, 📏 *distance*, 🧮 *number*, 🐾 *animal*, 🌿 *plant*, `🗺️🐣` *new model*.

## The RISC analogy

A small fixed instruction set, a fixed instruction format, one way to do each thing. The price RISC pays is code density, and so do we: the *Attention* abstract went from 7 English sentences to 31. ARM's answer was Thumb, a short encoding for the most frequent sequences; ours is the Layer 1 promotion rule. The warning in the analogy: RISC won partly because compilers, not people, wrote the assembly. Nobody compiles for our readers, so the density cost lands on a human. Fine for abstracts and picture books, tiring for ten pages.
