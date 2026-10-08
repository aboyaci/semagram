"""
Prompt construction. The system prompt is built from the repository itself:
docs/grammar.md, the generated dictionary, and the two example texts. Change
the grammar or dictionary and the prompt changes with them. Nothing here is
hand-maintained except the task instructions.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from semagram.lang import (  # noqa: E402
    Dictionary, dictionary_markdown, tokenize, _norm,
    LATIN_RE, NAME, NUM_RE, MATH,
)


def _examples() -> str:
    out = []
    for name in ("fish-and-bird", "attention-abstract"):
        sem = (ROOT / "examples" / f"{name}.sem").read_text(encoding="utf-8")
        gloss = (ROOT / "examples" / f"{name}.gloss.md").read_text(encoding="utf-8")
        # keep only the "→ render" lines of the gloss, aligned with the Semagram lines
        renders = [l.split("→", 1)[1].strip() for l in gloss.splitlines() if "→" in l]
        sems = [l for l in sem.splitlines() if "🔷" in l]
        pairs = "\n".join(f"{o}    {r}" for o, r in zip(sems, renders))
        out.append(f"### {name}\n{pairs}")
    return "\n\n".join(out)


def grammar_text() -> str:
    return (ROOT / "docs" / "grammar.md").read_text(encoding="utf-8")


def base_system(d: Dictionary) -> str:
    return "\n\n".join([
        "You are a translator for Semagram, a small emoji-based written language. Its complete grammar and dictionary follow. "
        "Use ONLY the glyphs in the dictionary. The language has no inflection, no articles, no brackets, no spaces, "
        "and every sentence is `[opener] [speaker💬] predicate agent patient 🔷`, one per line.",
        "# GRAMMAR\n" + grammar_text(),
        "# DICTIONARY\n" + dictionary_markdown(d),
        "# WORKED EXAMPLES (Semagram    predicate(agent, patient) gloss)\n" + _examples(),
    ])


TO_SEMAGRAM = """# TASK: translate the English below into Semagram.

Rules of engagement:
1. Output Semagram only: one sentence per line, each ending in 🔷. No English, no explanations, no code fences.
2. Names: first use is a cartouche with a category glyph (👤 person, 📍 place, 👥 group/company, 📦 thing/product, 🐾 animal), e.g. 👤🏷️Vaswani. Anything used more than once is bound ONCE at the top of the output as `glyph ≔ 👤🏷️Name` and the glyph is used after that. Faces and person emoji are allowed as bound glyphs.
3. Pronouns: 👉 is he/she/it/this. When two referents compete, use a category glyph: 👤👉 the person, 📦👉 the thing.
4. Split, don't nest. One English sentence usually becomes two to five Semagram sentences chained with 👉 or openers (➡️ so, ⬅️ because, 🔀 but, ∧ and, 🔺 if). Never more than three arguments.
5. Negation is postfix on the word it negates: 💤🐭🌕❌ = not all mice sleep; 💤❌🐭🌕 = all mice don't sleep. Get scope right; it is the one thing that must not be lost.
6. Tense: set once with ⏪🔷 or ⏩🔷 as its own line; reset with 🕐👉🔷. Leave present unmarked. Hedge only when the source hedges: 🟡 (we think), 🔴 (speculation).
7. Keep every number and every claim. Drop emphasis, rhythm and politeness.
8. Compounds must be dictionary words. If a needed word has no glyph and no honest compound of at most 3 roots, write it as a cartouche 📦🏷️word and, after the Semagram, add one line `# gaps: word1, word2` listing such words. That line is how the dictionary grows.
9. If the input is a procedure, write commands as a predicate with an empty agent slot, and put warnings in a separate sentence before the step, opened with ⚠️.

{feedback}
# ENGLISH
{text}
"""

FEEDBACK = """# PREVIOUS ATTEMPT WAS REJECTED BY THE LINTER
{attempt}

# LINT ERRORS (fix every one; keep everything else)
{errors}
"""

FROM_SEMAGRAM = """# TASK: translate the Semagram below into fluent, natural {lang}.

The gloss after each line is mechanical (predicate(agent, patient)); use it to be sure of the roles, then write real {lang}.
- Merge chained sentences into normal sentences where {lang} would; resolve every 👉 to what it refers to.
- Agent-less commands are imperatives. ⚠️ opens a warning.
- Unmarked sentences are assertions. 🟡 = "we think / it appears"; 🔴 = "possibly / we speculate". {evidential}
- Keep every number and claim. Do not add information that is not in the Semagram. Do not mention Semagram or emoji.
- Output only the {lang} text.

# SEMAGRAM
{text}

# GLOSS
{gloss}
"""

EVIDENTIAL_TR = "Türkçeye çevirirken: işaretsiz cümleler -dı/-di ile (tanıklı), 🟡 ve 🔴 ile açılanlar -mış/-miş ile çevrilir."

JUDGE = """Compare an ORIGINAL text with a ROUND-TRIP version that went through a lossy intermediate language.

List every factual claim in the ORIGINAL (a claim = something that could be true or false: who did what, numbers, comparisons, conditions, negations). For each, say whether the ROUND-TRIP preserves it, loses it, or contradicts it. A changed negation scope, a changed number, or a swapped agent/patient is a contradiction.

Answer in JSON only:
{{"claims": [{{"claim": "...", "status": "kept|lost|contradicted"}}], "style_lost": "one sentence on what non-factual content was lost", "verdict": "keep|drop"}}
verdict is "drop" if anything is contradicted or more than a third of the claims are lost.

# ORIGINAL
{original}

# ROUND-TRIP
{roundtrip}
"""


def strip_fences(s: str) -> str:
    s = re.sub(r"^```[a-z]*\n?", "", s.strip(), flags=re.M)
    return s.replace("```", "").strip()


def looks_like_semagram(line: str) -> bool:
    """True if the line is plausibly Semagram rather than English commentary.

    Reuses the tokenizer, so it applies the language's own rule: Latin letters
    are legal only inside a 🏷️ cartouche. A codepoint threshold does not work
    here — an em-dash or a curly apostrophe is above any emoji floor you pick,
    so "Here's the translation —" would pass as a sentence and then fail lint.
    """
    glyphs = 0
    for t in tokenize(line):
        if LATIN_RE.fullmatch(t) and not _norm(t).startswith(_norm(NAME)):
            return False                      # bare prose word outside a cartouche
        if not NUM_RE.fullmatch(t) and _norm(t) not in MATH:
            glyphs += 1
    return glyphs > 0


def extract_oku(s: str) -> tuple[str, list[str]]:
    """Keep binding and sentence lines; collect the `# gaps:` list."""
    keep, gaps = [], []
    for line in strip_fences(s).splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"#\s*gaps?\s*:\s*(.*)", line, re.I)
        if m:
            gaps += [g.strip() for g in m.group(1).split(",") if g.strip()]
        elif line.startswith("#") or looks_like_semagram(line):
            keep.append(line)          # the linter judges what survives this
    return "\n".join(keep), gaps
