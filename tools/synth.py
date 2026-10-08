"""
LLM translation pipeline for Semagram.

    python3 tools/synth.py translate --to sem  "Not all mice sleep."
    python3 tools/synth.py translate --to en   examples/fish-and-bird.sem
    python3 tools/synth.py translate --to tr   examples/fish-and-bird.sem
    python3 tools/synth.py roundtrip "The Transformer uses attention and nothing else."
    python3 tools/synth.py synth corpus.txt --out data/pairs.jsonl
    python3 tools/synth.py vocab > data/added_tokens.txt

Pipeline for `synth` (one record per paragraph of the input):
    English --LLM--> Semagram --lint--> (retry with errors, up to N) --LLM--> English' --LLM judge--> keep/drop
Kept pairs go to --out as JSONL {"en": ..., "sem": ..., "roundtrip": ..., "judge": {...}}.
Dropped ones go to <out>.rejects.jsonl with the reason. Every `# gaps:` word the model
asked for and every lint error are counted in <out>.gaps.json: that file is the
evidence the vocabulary grows from.

Provider selection: SEMAGRAM_PROVIDER=anthropic|openai|stub (see tools/llm.py).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from semagram.lang import Dictionary, apply_bindings, gloss_text, lint, tokenize  # noqa: E402
from tools.llm import LLM  # noqa: E402
from tools import prompt as P  # noqa: E402


# ---------------------------------------------------------------- provenance

def provenance(d: Dictionary) -> dict:
    """What language version a record was generated against.

    The system prompt is rebuilt from the repo on every call, so a dictionary
    or grammar edit silently changes what valid output looks like. Stamping
    each record is what lets you tell a stale pair from a current one instead
    of regenerating the whole corpus after every promotion.
    """
    core = json.loads((ROOT / "dictionary" / "core.json").read_text(encoding="utf-8"))
    grammar = (ROOT / "docs" / "grammar.md").read_bytes()
    dict_bytes = (ROOT / "dictionary" / "core.json").read_bytes()
    return {"dict_version": core.get("version", "?"),
            "dict_sha": hashlib.sha256(dict_bytes).hexdigest()[:12],
            "grammar_sha": hashlib.sha256(grammar).hexdigest()[:12],
            "packs": sorted(d.packs)}


# ---------------------------------------------------------------- core steps

def to_semagram(text: str, llm: LLM, d: Dictionary, retries: int = 3) -> dict:
    """English -> Semagram with the linter in the loop."""
    feedback, attempt, errors, gaps_all = "", "", [], []
    for i in range(retries + 1):
        raw = llm.complete(P.base_system(d), P.TO_SEMAGRAM.format(text=text, feedback=feedback))
        attempt, gaps = P.extract_oku(raw)
        gaps_all += gaps
        doc = Dictionary.load(d.packs)
        body = apply_bindings(re.sub(r"^#.*$", "", attempt, flags=re.M), doc)
        errors = lint(body, doc)
        if not errors:
            return {"sem": attempt, "errors": [], "gaps": gaps_all, "attempts": i + 1}
        feedback = P.FEEDBACK.format(attempt=attempt, errors="\n".join(errors))
    return {"sem": attempt, "errors": errors, "gaps": gaps_all, "attempts": retries + 1}


def from_semagram(sem: str, llm: LLM, d: Dictionary, lang: str = "en") -> str:
    doc = Dictionary.load(d.packs)
    body = apply_bindings(re.sub(r"^#.*$", "", sem, flags=re.M), doc)
    gloss = gloss_text(body, doc, "tr" if lang == "tr" else "en", show_words=False)
    name = {"en": "English", "tr": "Turkish"}.get(lang, lang)
    user = P.FROM_SEMAGRAM.format(lang=name, text=sem, gloss=gloss,
                             evidential=P.EVIDENTIAL_TR if lang == "tr" else "")
    return P.strip_fences(llm.complete(P.base_system(d), user))


def judge(original: str, roundtrip: str, llm: LLM) -> dict:
    raw = P.strip_fences(llm.complete("You are a strict, literal fact-checker. Answer in JSON only.",
                                      P.JUDGE.format(original=original, roundtrip=roundtrip)))
    try:
        return json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        return {"claims": [], "style_lost": "", "verdict": "drop", "error": f"unparseable judge output: {raw[:200]}"}


def roundtrip(text: str, llm: LLM, d: Dictionary, retries: int = 3) -> dict:
    enc = to_semagram(text, llm, d, retries)
    rt = from_semagram(enc["sem"], llm, d, "en") if not enc["errors"] else ""
    jd = judge(text, rt, llm) if rt else {"verdict": "drop", "claims": [], "error": "lint failed"}
    return {"en": text, **enc, "roundtrip": rt, "judge": jd}


# ---------------------------------------------------------------- batch

def paragraphs(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(l)["en"] for l in text.splitlines() if l.strip()]
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def synth(inp: Path, out: Path, llm: LLM, d: Dictionary, retries: int, limit: int | None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    rej = out.with_suffix(".rejects.jsonl")
    gaps: Counter = Counter()
    lint_errs: Counter = Counter()
    prov = provenance(d)
    kept = dropped = 0
    with out.open("a", encoding="utf-8") as fo, rej.open("a", encoding="utf-8") as fr:
        for k, para in enumerate(paragraphs(inp)):
            if limit and k >= limit:
                break
            r = roundtrip(para, llm, d, retries)
            gaps.update(g.lower() for g in r["gaps"])
            lint_errs.update(re.sub(r"s\d+: ", "", e) for e in r["errors"])
            if r["judge"].get("verdict") == "keep":
                kept += 1
                fo.write(json.dumps({"en": r["en"], "sem": r["sem"], "roundtrip": r["roundtrip"],
                                     "judge": r["judge"], "lang": prov}, ensure_ascii=False) + "\n")
            else:
                dropped += 1
                fr.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"[{k + 1}] {'keep' if r['judge'].get('verdict') == 'keep' else 'drop'}  "
                  f"attempts={r['attempts']} gaps={r['gaps']}", file=sys.stderr)
    stats = {"kept": kept, "dropped": dropped, "llm_calls": llm.calls,
             "lang": prov, "tokens": llm.usage,
             "gaps": gaps.most_common(), "lint_errors": lint_errs.most_common()}
    out.with_suffix(".gaps.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "lint_errors"}, ensure_ascii=False, indent=2))
    if llm.usage["cache_write"] and not llm.usage["cache_read"]:
        print("warning: the system prompt was written to cache but never read back — "
              "something is changing the prefix between calls", file=sys.stderr)


def vocab(d: Dictionary) -> list[str]:
    """Every glyph and declared compound as one token, for a tokenizer's added-tokens list.
    Without this a byte-level tokenizer spends capacity re-learning that 🐭 is one unit."""
    toks = set()
    for e in d.entries.values():
        toks.add(e.glyph)
    for c in d.compounds.values():
        toks.add(c.glyph)
    toks |= {"🔷", "🔹", "≔", "⚠️"}
    return sorted(toks, key=lambda t: (len(tokenize(t)), t))


# ---------------------------------------------------------------- CLI

def _read(arg: str) -> str:
    p = Path(arg)
    return p.read_text(encoding="utf-8") if p.exists() else arg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["translate", "roundtrip", "synth", "vocab"])
    ap.add_argument("input", nargs="?", default="")
    ap.add_argument("--to", choices=["sem", "en", "tr"], default="sem")
    ap.add_argument("--out", default="data/pairs.jsonl")
    ap.add_argument("--pack", action="append", default=[])
    ap.add_argument("--provider"); ap.add_argument("--model"); ap.add_argument("--base-url")
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args(argv)

    d = Dictionary.load(a.pack)
    if a.cmd == "vocab":
        print("\n".join(vocab(d))); return 0
    llm = LLM(a.provider, a.model, a.base_url)
    text = _read(a.input) if a.input else sys.stdin.read()

    if a.cmd == "translate":
        if a.to == "sem":
            r = to_semagram(text, llm, d, a.retries)
            print(r["sem"])
            if r["errors"]:
                print("# UNRESOLVED LINT ERRORS:\n# " + "\n# ".join(r["errors"]), file=sys.stderr)
            if r["gaps"]:
                print(f"# gaps: {', '.join(r['gaps'])}", file=sys.stderr)
            return 1 if r["errors"] else 0
        print(from_semagram(text, llm, d, a.to)); return 0
    if a.cmd == "roundtrip":
        r = roundtrip(text, llm, d, a.retries)
        print(json.dumps(r, ensure_ascii=False, indent=2)); return 0
    if a.cmd == "synth":
        synth(Path(a.input), Path(a.out), llm, d, a.retries, a.limit); return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
