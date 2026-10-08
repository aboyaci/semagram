"""
Semagram — tokenizer, segmenter, glosser, encoder and linter for the emoji language.

Dependency-free. Python 3.9+.

    python3 -m semagram gloss  examples/fish-and-bird.sem
    python3 -m semagram gloss  --tr examples/fish-and-bird.sem
    python3 -m semagram encode "the fish sees the bird"
    python3 -m semagram lint   examples/attention-abstract.sem
    python3 -m semagram dict   > DICTIONARY.md

The "translator" is honest about what it is: a glosser. It segments text
into words under the v0.3 rules and labels each word from the dictionary,
then renders the sentence as predicate(agent, patient). It does not and
cannot produce fluent English; that is the reader's job, by design.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
DICT_DIR = HERE.parent / "dictionary"

# ---------------------------------------------------------------- constants

SENTENCE_END = "🔷"
WORD_BREAK = "🔹"          # optional, tolerated, ignored
SAYS = "💬"
NAME = "🏷️"
NEG = "❌"
CONFIDENCE = {"🟡", "🔴"}
LINKERS = {"➡️", "⬅️", "🔀", "∧", "∨", "🔺"}
TENSE = {"⏪", "⏩"}
# modifiers always attach to the word on their left (unless sentence-initial)
MODIFIERS = {NEG, "🌑", "🌘", "🌗", "🌔", "🌕", "🐘", "🐜",
             "📈", "📉", "⬆️", "⬇️", "👍", "👎", "‼️", "📜"}
BANNED = {"➕": "collides with arithmetic plus; use ∧",
          "❎": "renders green on some platforms; use ❌",
          "(": "no brackets in v0.3; split into sentences or use a speaker label",
          ")": "no brackets in v0.3"}

VS16 = "️"
VS15 = "︎"
ZWJ = "‍"
KEYCAP = "⃣"
SKIN = {chr(c) for c in range(0x1F3FB, 0x1F400)}
MATH = set("∃∧∨≔∥><=≤≥≠±×÷√∇|+-")
INFIX = {"∧", "∨", ">", "<", "=", "≤", "≥", "≠", "+", "-", "±", "×", "÷"}  # glue neighbours into one word
ATTACH = MODIFIERS | TENSE  # things that join the word to their left

NUM_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")
LATIN_RE = re.compile(r"[^\W\d_][\w.\-]*", re.UNICODE)   # any script: Mehmet, محمد, 北京
CATEGORY = {"👤", "📍", "👥", "📦", "🐾"}  # determinatives: person, place, group, thing, animal
BIND = "≔"


def _norm(g: str) -> str:
    """Strip variation selectors so 🏷 and 🏷️ are the same glyph."""
    return g.replace(VS16, "").replace(VS15, "")


# ---------------------------------------------------------------- dictionary

@dataclass
class Entry:
    glyph: str
    en: str
    tr: str
    cls: str = "root"
    layer: int = 1
    transparency: str = ""
    notes: str = ""
    nsm: str = ""
    source: str = "core"


class Dictionary:
    def bind(self, glyph: str, gloss: str, tr: str = "") -> None:
        """Document-local binding from a `X ≔ Y` line. The bound glyph is a word
        in this document only; it overrides nothing in core."""
        key = _norm(glyph)
        if key in self.entries and self.entries[key].source == "core":
            raise ValueError(f"{glyph} is a core glyph and cannot be rebound")
        self.entries[key] = Entry(glyph=glyph, en=gloss, tr=tr or gloss, cls="root", layer=2,
                                  transparency="bound", source="binding")

    def __init__(self) -> None:
        self.entries: dict[str, Entry] = {}        # normalized glyph -> entry
        self.compounds: dict[str, Entry] = {}      # normalized glyph string -> entry
        self.packs: list[str] = []

    @classmethod
    def load(cls, packs: Iterable[str] = ()) -> "Dictionary":
        d = cls()
        d._load_file(DICT_DIR / "core.json", "core")
        for p in packs:
            path = DICT_DIR / "packs" / f"{p}.json"
            if not path.exists():
                raise FileNotFoundError(f"no pack named {p!r} at {path}")
            d._load_file(path, p)
            d.packs.append(p)
        return d

    def _load_file(self, path: Path, source: str) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        for e in data.get("entries", []):
            ent = Entry(glyph=e["glyph"], en=e["en"], tr=e.get("tr", ""),
                        cls=e.get("class", "root"), layer=e.get("layer", 1),
                        transparency=e.get("transparency", ""),
                        notes=e.get("notes", ""), nsm=e.get("nsm", ""), source=source)
            self.entries[_norm(e["glyph"])] = ent
        for c in data.get("compounds", []):
            ent = Entry(glyph=c["glyphs"], en=c["en"], tr=c.get("tr", ""),
                        cls="compound", layer=c.get("layer", 1), source=source)
            self.compounds[_norm(c["glyphs"])] = ent

    def lookup(self, glyph: str) -> Entry | None:
        return self.entries.get(_norm(glyph))

    def lookup_compound(self, glyphs: str) -> Entry | None:
        return self.compounds.get(_norm(glyphs))

    def max_compound_len(self) -> int:
        return max((len(tokenize(k)) for k in self.compounds), default=1)

    def reverse_index(self) -> dict[str, str]:
        """english word -> glyphs, for the encoder. Core wins over packs,
        single glyphs win over compounds, first gloss wins over later ones."""
        idx: dict[str, str] = {}
        def add(key: str, glyph: str) -> None:
            key = key.strip().lower()
            if key and key not in idx:
                idx[key] = glyph
        for ent in list(self.entries.values()) + list(self.compounds.values()):
            if ent.en.startswith("["):
                continue
            for alt in ent.en.split("/"):
                alt = re.sub(r"\(.*?\)", "", alt)
                add(alt, ent.glyph)
                if ent.cls in ("root", "compound"):
                    for w in alt.split():
                        add(w, ent.glyph)
        return idx


# ---------------------------------------------------------------- tokenizer

def tokenize(text: str) -> list[str]:
    """Split text into glyph tokens.

    - an emoji plus its variation selector / skin tone / ZWJ tail is one token
    - 🏷️ swallows the Latin run after it: 🏷️Transformer is one token
    - a number literal (28.4) is one token; math symbols are one token each
    - whitespace and 🔹 are dropped; the reader never needed them
    """
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace() or ch == WORD_BREAK or ch in VS16 + VS15:
            i += 1
            continue
        m = NUM_RE.match(text, i)
        if m:
            out.append(m.group()); i = m.end(); continue
        m = LATIN_RE.match(text, i)
        if m:
            tok = m.group()
            if out and _norm(out[-1]) == _norm(NAME):
                out[-1] = out[-1] + tok
            else:
                out.append(tok)
            i = m.end(); continue
        # emoji / symbol: take base plus any combining tail
        j = i + 1
        while j < n and (text[j] in (VS16, VS15, KEYCAP) or text[j] in SKIN):
            j += 1
        while j + 1 < n and text[j] == ZWJ:
            j += 2
            while j < n and (text[j] in (VS16, VS15) or text[j] in SKIN):
                j += 1
        out.append(text[i:j]); i = j
    return out


def sentences(tokens: list[str]) -> list[list[str]]:
    sents, cur = [], []
    for t in tokens:
        if _norm(t) == _norm(SENTENCE_END):
            if cur:
                sents.append(cur); cur = []
        else:
            cur.append(t)
    if cur:
        sents.append(cur)   # unterminated: lint will complain
    return sents


# ---------------------------------------------------------------- segmenter

@dataclass
class Word:
    glyphs: list[str]
    role: str = ""              # confidence | linker | frame | speaker | predicate | agent | patient | extra
    entry: Entry | None = None  # compound entry if the whole word is a known compound

    @property
    def text(self) -> str:
        return "".join(self.glyphs)


@dataclass
class Sentence:
    words: list[Word] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(w.text for w in self.words) + SENTENCE_END


def segment(tokens: list[str], d: Dictionary) -> Sentence:
    """Group tokens into words under the no-break rules:

    1. one glyph is one word, by default
    2. a modifier attaches to the word on its left, unless there is nothing
       on its left, in which case it is the predicate
    3. a repeated glyph attaches (reduplication = plural: 🙋🙋)
    4. a declared compound (dictionary) is one word, longest match first
    5. a word ending in 💬 (not starting with it) is a speaker label
    """
    s = Sentence()
    maxlen = d.max_compound_len()
    i, n = 0, len(tokens)
    words: list[Word] = []
    attach = {_norm(m) for m in ATTACH}
    openers = {_norm(x) for x in LINKERS | CONFIDENCE}
    while i < n:
        # 4. longest declared compound first
        matched = None
        for L in range(min(maxlen, n - i), 1, -1):
            cand = tokens[i:i + L]
            ent = d.lookup_compound("".join(cand))
            if ent:
                matched = Word(list(cand), entry=ent); i += L; break
        if matched:
            words.append(matched); continue
        tok = tokens[i]
        prev = words[-1] if words else None
        # 5. 💬 closes a speaker label and absorbs every word to its left back
        # to the start of the sentence (grammar §4): 🐟💬, 🐟💭💬 the fish
        # thinks, 🙋🙋🧠❌💬 we do not know whether.
        if _norm(tok) == _norm(SAYS):
            b = 0
            while b < len(words) and _norm(words[b].text) in openers:
                b += 1
            if b < len(words):
                words[b:] = [Word([g for w in words[b:] for g in w.glyphs] + [tok])]
                i += 1
                continue
        prev_ok = (
            prev is not None
            and _norm(prev.text) not in openers
            and not (len(prev.glyphs) > 1 and _norm(prev.glyphs[-1]) == _norm(SAYS))
            and prev.entry is None
        ) or (
            prev is not None and prev.entry is not None
            and prev.entry.cls == "compound" and _norm(tok) in attach
        )
        is_name = _norm(tok).startswith(_norm(NAME)) and prev is not None and len(prev.glyphs) == 1 \
            and _norm(prev.glyphs[0]) in {_norm(c) for c in CATEGORY}
        is_cat_pron = _norm(tok) == "👉" and prev is not None and len(prev.glyphs) == 1 \
            and _norm(prev.glyphs[0]) in {_norm(c) for c in CATEGORY}
        is_mod = _norm(tok) in attach or is_name or is_cat_pron
        is_dup = prev is not None and _norm(prev.glyphs[-1]) == _norm(tok) and _norm(tok) != _norm(SAYS)
        if prev_ok and (is_mod or is_dup):
            prev.glyphs.append(tok)
        else:
            words.append(Word([tok]))
        i += 1
    # infix glue: X∧Y, a>b+2 become one word (one argument)
    infix = {_norm(x) for x in INFIX}
    glued: list[Word] = []
    k = 0
    while k < len(words):
        w = words[k]
        if glued and len(w.glyphs) == 1 and _norm(w.glyphs[0]) in infix and k + 1 < len(words) \
                and _norm(glued[-1].text) not in openers:
            glued[-1] = Word(glued[-1].glyphs + w.glyphs + words[k + 1].glyphs)
            k += 2; continue
        glued.append(w); k += 1
    words = glued

    # roles
    pos = 0
    for w in words:
        t = _norm(w.text)
        if pos == 0 and t in {_norm(c) for c in CONFIDENCE}:
            w.role = "confidence"; continue
        if pos == 0 and t in {_norm(l) for l in LINKERS}:
            w.role = "linker"; continue
        if len(w.glyphs) >= 2 and _norm(w.glyphs[-1]) == _norm(SAYS):
            w.role = "speaker"; continue
        if pos == 0 and len(words) == 1 and (t in {_norm(x) for x in TENSE} or t == _norm("🕐👉")):
            w.role = "frame"; pos += 1; continue
        w.role = ("predicate", "agent", "patient")[pos] if pos < 3 else "extra"
        pos += 1
    s.words = words
    return s


# ---------------------------------------------------------------- glosser

def gloss_word(w: Word, d: Dictionary, lang: str = "en") -> str:
    if w.entry:
        return getattr(w.entry, lang) or w.entry.en
    t = _norm(w.text)
    cats = {_norm(c) for c in CATEGORY}
    if len(w.glyphs) == 2 and _norm(w.glyphs[0]) in cats:
        cat = (d.lookup(w.glyphs[0]).en.split("/")[0].strip() if d.lookup(w.glyphs[0]) else "?")
        cat = {"someone": "person", "something": "thing", "people": "group"}.get(cat, cat)
        if _norm(w.glyphs[1]) == "👉":
            return f"the-{cat}"
        if _norm(w.glyphs[1]).startswith(_norm(NAME)):
            return f"{w.glyphs[1][len(NAME):].lstrip(VS16)}({cat})"
    if t.startswith(_norm(NAME)):
        return w.text[len(NAME.replace(VS16, "")):].lstrip(VS16) or "[name]"
    if NUM_RE.fullmatch(w.text):
        return w.text
    parts = []
    glyphs = list(w.glyphs)
    # reduplication
    if len(glyphs) >= 2 and all(_norm(g) == _norm(glyphs[0]) for g in glyphs[:2]) and _norm(glyphs[0]) != _norm(SAYS):
        ent = d.lookup(glyphs[0])
        base = (getattr(ent, lang) if ent else None) or (ent.en if ent else f"?{glyphs[0]}")
        plural = {"I": "we", "ben": "biz"}.get(base.split("/")[0].strip(), None)
        parts.append(plural or f"{base.split('/')[0].strip()}-PL")
        glyphs = glyphs[2:]
    for g in glyphs:
        if _norm(g) == _norm(SAYS) and g is w.glyphs[-1] and len(w.glyphs) > 1:
            parts.append("says"); continue
        ent = d.lookup(g)
        if ent:
            parts.append((getattr(ent, lang) or ent.en).split("/")[0].strip())
        elif NUM_RE.fullmatch(g) or _norm(g) in MATH or (_norm(g) == g and len(g) == 1 and not g.isalnum()):
            parts.append(g)
        else:
            parts.append(f"?{g}")
    out = ""
    for p_ in parts:
        if p_ in MATH or (out and out[-1] in MATH):
            out += p_
        else:
            out += ("-" if out else "") + p_
    return out or w.text


def render(s: Sentence, d: Dictionary, lang: str = "en") -> str:
    """predicate(agent, patient) form, with openers in front."""
    openers, pred, args, speaker = [], None, [], None
    for w in s.words:
        g = gloss_word(w, d, lang)
        if w.role in ("confidence", "linker"):
            openers.append(g)
        elif w.role == "speaker":
            speaker = g
        elif w.role == "frame":
            return f"[{g}]"
        elif w.role == "predicate":
            pred = g
        else:
            args.append(g)
    head = " ".join(openers)
    body = f"{pred}({', '.join(args)})" if pred else ""
    if speaker:
        body = f"{speaker}: {body}"
    return " ".join(x for x in (head, body) if x)


def gloss_text(text: str, d: Dictionary, lang: str = "en", show_words: bool = True) -> str:
    lines = []
    for toks in sentences(tokenize(text)):
        s = segment(toks, d)
        line = s.text
        if show_words:
            line += "\n    " + " · ".join(f"{w.text}={gloss_word(w, d, lang)}" for w in s.words)
        line += "\n    → " + render(s, d, lang)
        lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------- encoder

STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "it", "that", "this", "there"}
# words that are real grammar in Semagram but stopwords-looking in English
OVERRIDE = {"in": "📥", "this": "👉", "it": "👉", "there": "∃", "is": None, "not": NEG, "no": NEG}


def encode_sentence(english: str, d: Dictionary, idx: dict[str, str]) -> tuple[str, list[str]]:
    """Word-by-word lookup. It is a dictionary, not a translator: it will
    not reorder to predicate-first for you. Write predicate first yourself:
        encode("sees fish bird")  -> 👁️🐟🐦🔷
    """
    out, unknown = [], []
    pending_neg = False
    words = re.findall(r"[A-Za-z']+|[0-9.]+", english.lower())
    for w in words:
        if w in ("not", "no", "n't"):
            pending_neg = True; continue
        if w in OVERRIDE:
            g = OVERRIDE[w]
            if g: out.append(g)
            continue
        if w in STOPWORDS:
            continue
        g = idx.get(w) or idx.get(w.rstrip("s")) or idx.get(w.replace("ing", ""))
        if g:
            out.append(g + (NEG if pending_neg else "")); pending_neg = False
        elif NUM_RE.fullmatch(w):
            out.append(w)
        else:
            out.append(f"[?{w}]"); unknown.append(w)
    return "".join(out) + SENTENCE_END, unknown


# ---------------------------------------------------------------- linter

def lint(text: str, d: Dictionary) -> list[str]:
    problems: list[str] = []
    toks = tokenize(text)
    if not toks:
        return ["no sentences"]
    if _norm(toks[-1]) != _norm(SENTENCE_END):
        problems.append("text does not end with 🔷")
    for t in toks:
        if _norm(t) in BANNED:
            problems.append(f"banned glyph {t}: {BANNED[_norm(t)]}")
    from collections import Counter
    names = Counter(_norm(t) for t in toks if _norm(t).startswith(_norm(NAME)))
    for nm, c in names.items():
        if c >= 3:
            problems.append(f"name {nm} used {c} times: bind it once with ≔ and use the glyph")
    for t in toks:
        if LATIN_RE.fullmatch(t) and not _norm(t).startswith(_norm(NAME)):
            problems.append(f"bare text {t!r}: letters are allowed only inside a 🏷️ cartouche")
    for k, toks_s in enumerate(sentences(toks), 1):
        s = segment(toks_s, d)
        for w in s.words:
            skip = {_norm(m) for m in ATTACH} | {_norm(SAYS)}
            sides = re.split("|".join(map(re.escape, INFIX)), w.text)
            for side in sides:
                roots = [g for g in tokenize(side) if _norm(g) not in skip and not NUM_RE.fullmatch(g)]
                if len(roots) > 3:
                    problems.append(f"s{k}: word {side} has {len(roots)} roots (cap is 3)")
            roots = [g for g in w.glyphs if _norm(g) not in skip and _norm(g) not in {_norm(x) for x in INFIX}]
            has_infix = any(_norm(g) in {_norm(x) for x in INFIX} for g in w.glyphs)
            has_cat = _norm(w.glyphs[0]) in {_norm(c) for c in CATEGORY} and len(w.glyphs) == 2
            # a speaker label (§4) is a construction, not a compound to declare
            has_says = len(w.glyphs) > 1 and _norm(w.glyphs[-1]) == _norm(SAYS)
            if len(roots) >= 2 and not w.entry and not has_infix and not has_cat and not has_says \
                    and not _norm(w.text).startswith(_norm(NAME)) \
                    and len(set(_norm(g) for g in roots)) > 1:
                problems.append(f"s{k}: {w.text} is an undeclared compound (declare it in a pack with ≔)")
            for g in w.glyphs:
                if LATIN_RE.fullmatch(g):
                    continue
                if not d.lookup(g) and not NUM_RE.fullmatch(g) and _norm(g) not in MATH \
                        and not _norm(g).startswith(_norm(NAME)) and not _norm(g) in {_norm(x) for x in LINKERS | CONFIDENCE}:
                    problems.append(f"s{k}: unknown glyph {g}")
        if s.words and s.words[0].role == "predicate" and _norm(s.words[0].glyphs[0]) == _norm(NEG):
            problems.append(f"s{k}: ❌ is postfix; it cannot open a word")
        if sum(1 for w in s.words if w.role not in ("confidence", "linker", "speaker", "frame") and not NUM_RE.fullmatch(w.text)) > 3:
            problems.append(f"s{k}: more than 3 arguments; split the sentence")
    return problems


# ---------------------------------------------------------------- dictionary → markdown

def dictionary_markdown(d: Dictionary) -> str:
    lines = ["# Dictionary", "",
             f"Generated from `dictionary/core.json`" + (f" and packs: {', '.join(d.packs)}" if d.packs else "") + ". Do not edit by hand.", ""]
    def table(title, rows):
        if not rows: return
        lines.extend([f"## {title}", "", "| Glyph | English | Türkçe | Transparency | Notes |", "|---|---|---|---|---|"])
        for e in rows:
            notes = e.notes + (f" NSM: {e.nsm}." if e.nsm else "")
            lines.append(f"| {e.glyph} | {e.en} | {e.tr} | {e.transparency} | {notes} |")
        lines.append("")
    ents = list(d.entries.values())
    table("Grammar: particles and linkers", [e for e in ents if e.cls in ("particle", "linker")])
    table("Grammar: modifiers (attach to the left)", [e for e in ents if e.cls == "modifier"])
    table("Layer 0: semantic primes", [e for e in ents if e.cls == "root" and e.layer == 0])
    table("Layer 1: core roots", [e for e in ents if e.cls == "root" and e.layer == 1])
    table("Layer 2: domain packs", [e for e in ents if e.layer == 2])
    comps = list(d.compounds.values())
    if comps:
        lines.extend(["## Declared compounds", "", "Head first. Under the no-break rule a compound must be declared before it can be read.", "",
                      "| Glyphs | English | Türkçe | Source |", "|---|---|---|---|"])
        for c in comps:
            lines.append(f"| {c.glyph} | {c.en} | {c.tr} | {c.source} |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- CLI

def apply_bindings(text: str, d: Dictionary) -> str:
    """Strip `X ≔ Y` lines from a document and register them. X is one glyph
    (or a glyph run); Y is a cartouche, optionally with a category glyph, or
    any gloss text. Returns the text without those lines."""
    kept = []
    for line in text.splitlines():
        if BIND in line:
            left, right = line.split(BIND, 1)
            left, right = left.strip(), right.strip()
            if NAME.replace(VS16, "") in _norm(left) and NAME.replace(VS16, "") not in _norm(right):
                left, right = right, left   # tolerate `🏷️Name ≔ glyph`; canonical is `glyph ≔ 🏷️Name`
            toks = tokenize(right)
            name = next((t for t in toks if _norm(t).startswith(_norm(NAME))), None)
            gloss = name[len(NAME):].lstrip(VS16) if name else right
            cat = next((t for t in toks if _norm(t) in {_norm(c) for c in CATEGORY}), "")
            if cat and d.lookup(cat):
                c = d.lookup(cat).en.split("/")[0].strip()
                gloss = f"{gloss} ({ {'someone': 'person', 'something': 'thing', 'people': 'group'}.get(c, c) })"
            d.bind(left, gloss)
        else:
            kept.append(line)
    return "\n".join(kept)


def _read(arg: str) -> str:
    p = Path(arg)
    return p.read_text(encoding="utf-8") if p.exists() else arg


COMMANDS = ("gloss", "encode", "lint", "dict", "tokens")


def main(argv: list[str] | None = None) -> int:
    import argparse
    # Subparsers rather than two bare positionals: argparse cannot reliably
    # match `cmd input` when a flag sits between them, so the natural
    # `gloss --pack attention file.sem` fails on a flat parser.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("input", nargs="?", default="", help="text or a file path (default: stdin)")
    common.add_argument("--pack", action="append", default=[], help="load a Layer 2 pack (repeatable)")
    common.add_argument("--tr", action="store_true", help="gloss in Turkish")
    common.add_argument("--brief", action="store_true", help="skip per-word glosses")

    ap = argparse.ArgumentParser(prog="semagram", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", metavar="{" + ",".join(COMMANDS) + "}")
    for name in COMMANDS:
        sub.add_parser(name, parents=[common], help=None)
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_usage(sys.stderr)
        print(f"semagram: error: pick a command: {', '.join(COMMANDS)}", file=sys.stderr)
        return 2

    # `dict` renders the dictionary and takes no text, so it must not block
    # on stdin waiting for input nobody is going to type.
    if a.input:
        text = _read(a.input)
    elif a.cmd == "dict":
        text = ""
    else:
        text = sys.stdin.read()
    packs = list(a.pack)
    # a document may declare its pack in a comment line: # pack: attention
    for m in re.finditer(r"^#\s*pack:\s*(\w+)", text, re.M):
        packs.append(m.group(1))
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    try:
        d = Dictionary.load(packs)
        text = apply_bindings(text, d)
    except (FileNotFoundError, ValueError) as e:
        print(f"semagram: {e}", file=sys.stderr)
        return 2
    lang = "tr" if a.tr else "en"

    if a.cmd == "tokens":
        print(" | ".join(tokenize(text)))
    elif a.cmd == "gloss":
        print(gloss_text(text, d, lang, show_words=not a.brief))
    elif a.cmd == "encode":
        idx = d.reverse_index()
        for line in text.splitlines():
            if line.strip():
                enc, unk = encode_sentence(line, d, idx)
                print(enc + (f"    # unknown: {', '.join(unk)}" if unk else ""))
    elif a.cmd == "lint":
        probs = lint(text, d)
        print("\n".join(probs) if probs else "ok")
        return 1 if probs else 0
    elif a.cmd == "dict":
        print(dictionary_markdown(d), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
