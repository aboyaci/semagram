# Decision log

What was tried, in order, what broke, and what replaced it. Most rules in the grammar exist because a specific sentence failed.

## 0. The sticker translation

First attempt: translate *Attention Is All You Need* by replacing nouns with emoji and keeping all maths. About 70% survived, for a boring reason: the paper is mostly equations, hyperparameters and a complexity table, none of which was English to begin with. What died, in order: hedging (*we suspect that…*), the learnability argument (abstract claims have no picture), related work (proper nouns plus contrastive clauses), and the ablation discussion (counterfactuals). **Finding: emoji encodes what was built and what happened; it does not encode why or how it relates to anything else.**

## 1. Not Esperanto

Esperanto works through affixes, and emoji are atomic. The right models are isolating languages: Toki Pona (~130 words, particles), Mandarin (picture-descended script, zero inflection, carries all of science), and Blissymbols (someone built this idea in 1949). Rule adopted: **pictures are content, shapes are grammar.**

## 2. Vocabulary from NSM

"Minimum set of words" has a serious empirical answer: the ~65 semantic primes of Natural Semantic Metalanguage. Adopted as Layer 0. Realised that *minimum roots* and *minimum things to memorise* are different numbers, and only the second matters to a learner; hence the three layers.

## 3. The 🟰 objection (the first real correction)

`❌🟰` was proposed for *other*. It says *not same*, i.e. *different*. The other mouse can be identical. 👈 became a prime. This produced Test A (compositional honesty) and caught `🗣️❌✅` for *lie* and `🌗` for *some* on the same audit.

## 4. Guessability audit

Requirement: understandable without training, or at least decipherable. Adopted the transparent / translucent / opaque tiers. Casualties: 🎬 *do* (English film pun), 🔘 *there is* (arbitrary), 🆚 🆔 (contain Latin), 🧲 *near*. The ⬆️⬇️ vs 📈📉 split, the dimension+🐘/🐜 pattern, and reduplication-as-plural came out of this round.

## 5. Open problems round

*touch* → `📏🌑` (zero distance). *side* → ↔️, which moved *or* to ∨. *many* → `🧮🐘`, which separated counts from proportions. Layer 1 drafted at ~50 roots; stability test killed every expression face, 🌙, "head", 🆕, 🙏 🔫 🍑.

## 6. ❌ unified, spaces questioned

*no / not / false* became one symbol; *no* as quantity stayed 🌑. Spaces were justified by decipherability (Linear B's word dividers helped Ventris) and then flagged as fragile. Rule 7 (damaged text must produce garbage) was introduced here and later lost.

## 7. Postfix negation, scope by order

❌ moved to postfix: it was the one exception to "modifiers follow the head". A fixed order freed the particles, briefly, to mark scope ("whatever comes first has wider scope"). This was later given up when order was spent on roles instead.

## 8. Verb-first

Predicate-first adopted: it is how logic writes things and favours neither English (SVO) nor Turkish (SOV). ▶️ and ⏺️, the two most frequent opaque glyphs, were deleted. Scope-by-order was lost; scope survives as vocabulary (`🐱🟰` the same cat).

## 9. The BNF detour, and Lojban

The grammar was written as twelve BNF productions. It exposed that confidence markers were also sentence delimiters and that linkers could become predicates over bracketed groups. It also revealed the destination: **Lojban** with pictures, a language with a handful of fluent speakers after decades because humans cannot run a parser in real time. Reversed.

## 10. Natural, not programming

Pidgins as the model: tiny vocabulary, fixed order, **no embedding**, chained short sentences, 👉 pointing at the previous sentence. Egyptian turned out to be a better ancestor than expected: verb-first (Middle Egyptian is VSO) and the determinative (📜). The warning from Egypt and China: every pictographic script that survived went phonetic, because pictures run out at abstractions. That exit is closed to a language with no spoken form, which is why Bliss is the real ancestor and why domain packs exist.

## 11. Tense and confidence simplified

Past/present/future only, no aspect, **sticky tense** set once per passage. Evidentiality (-dı/-mış) dropped as mandatory; "fact unless said otherwise" with optional 🟡 🔴. Acknowledged cost: mandatory hedging was the one feature that made this better than English for science.

## 12. First full abstract

31 sentences for 7. Predictions wrong: *than* and the instrument role never broke. ➕ collided with arithmetic plus (→ ∧). The 3-root cap bit three times and was solved each time by setting a topic sentence. The patient slot was observed to be a junk drawer (standard of comparison, comparison class, domain). *task* and *result* became the first evidence-backed Layer 1 candidates.

## 13. The fish and the bird

An original beginner story (Seuss's own texts are not translatable: rhyme, meter and invented words are all sound). Discovered the language has a visual poetry: predicate-first gives free anaphora, paired opposites give rhyme for the eye, like Chinese *duilian*. Density was 1:1, so the picture book is the native genre. Location words were found to be two-place predicates (no role markers needed). Quotation was the first legitimate use of brackets.

## 14. No brackets

Brackets are a writing invention no spoken language has. Replaced by the **speaker label** (`🐟💬`), which also handles claims about claims and fixes the problem that `👉`-attribution asserted things before attributing them. ❌ simplified to "negates the whole word to its left". The grammar stopped being recursive; that is the real exit from Lojban.

## 15. Emoji only

No ASCII punctuation. 🔹 word break, 🔷 sentence end, 💬 closes a speaker label. Numbers and maths kept as an embedded foreign script, as every writing system does with numerals.

## 16. No word break

🔹 dropped. One glyph is one word; modifiers attach left; compounds must be declared. Lost: rule 7 and the lost-space detector. Gained: the cleanest text so far, and a choice of the story over the paper. The Japanese precedent noted: adult text has no spaces but children's kana books add them, and our whole readership is beginners. The cold-reader test now has to settle this rather than taste.

## 17. Repository

Dictionary as data with generated Markdown, a glosser/linter that encodes the segmentation rules, and this log. Writing the segmenter forced four small rulings that the prose grammar had left implicit: connectives and math operators glue neighbours into one word; a modifier after an opener is a predicate; ⏪⏩ may trail a word (`🏆⏪` previous best); numbers do not count toward the three-argument cap.

## 18. Names and pronouns

🏷️ gained category determinatives (👤 📍 👥 📦 🐾), the half of the Egyptian idea we had dropped; any script is allowed inside the cartouche; recurring names are bound once with `≔` (canonical form `glyph ≔ 👤🏷️Name`) and the rejected face emoji became the name pool. 👉 was confirmed as the single third-person pronoun, as Turkish *o*, with optional category prefixes; gender was refused on IR grounds (translating from an ungendered language would have to invent it). The linter now flags a cartouche used three or more times without a binding, and bare letters outside a cartouche.

## 19. The LLM pipeline

`tools/`: a dependency-free LLM client (Anthropic, any OpenAI-compatible local server, or an offline stub), a prompt built from the repository itself (grammar.md + generated dictionary + the two examples, about 4.7k tokens), and a pipeline: English → Semagram with the linter in the loop → back-translation → an LLM judge that lists each claim as kept, lost or contradicted. Kept pairs become training data for a small model; every `# gaps:` word the model asks for and every lint error are counted, which is the frequency evidence the vocabulary was always supposed to grow from. `vocab` exports every glyph as an added token so a byte-level tokenizer does not have to re-learn that 🐭 is one unit.
