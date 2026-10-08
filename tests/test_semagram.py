import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semagram.lang import Dictionary, tokenize, sentences, segment, gloss_text, lint, encode_sentence  # noqa: E402

D = Dictionary.load(["attention"])


def words(text):
    return [w.text for w in segment(sentences(tokenize(text))[0], D).words]


def render(text, lang="en"):
    return gloss_text(text, D, lang, show_words=False).split("→ ")[1].strip()


def test_tokenizer_keeps_variation_selectors_together():
    assert tokenize("🏷️Transformer👁️") == ["🏷️Transformer", "👁️"]


def test_word_break_is_ignored():
    assert tokenize("👁️🔹🐟🔹🐦🔷") == tokenize("👁️🐟🐦🔷")


def test_one_glyph_one_word():
    assert words("👁️🐟🐦🔷") == ["👁️", "🐟", "🐦"]


def test_modifier_attaches_left():
    assert words("📥💧🌑📍⬆️🔷") == ["📥", "💧🌑", "📍⬆️"]


def test_modifier_sentence_initial_is_predicate():
    assert words("⬆️🐦🌊🔷") == ["⬆️", "🐦", "🌊"]
    assert render("⬆️🐦🌊🔷") == "above(bird, sea)"


def test_modifier_after_linker_is_predicate():
    assert render("∧📉‼️🕐🧠📈🔷") == "and less-very(time, learn)"


def test_reduplication_is_plural():
    assert words("🔨🙋🙋🤖🔷") == ["🔨", "🙋🙋", "🤖"]
    assert render("🔨🙋🙋🤖🔷") == "make(we, Transformer)"


def test_speaker_label():
    assert render("🐟💬🎯🙋📍⬆️🔷") == "fish-says: want(I, place-above)"


def test_speaker_label_absorbs_mental_root():
    # grammar §4: a mental root may sit before 💬, and the label is one word
    assert words("🙋🙋🧠💬💤🐭🔷") == ["🙋🙋🧠💬", "💤", "🐭"]
    assert render("🙋🙋🧠💬💤🐭🔷") == "we-know-says: sleep(mouse)"
    assert render("🐟💭💬🎯🙋📍⬆️🔷") == "fish-think-says: want(I, place-above)"


def test_speaker_label_negation_scope():
    # §4: "we don't know whether P" vs "we know not-P"
    assert render("🙋🙋🧠❌💬💤🐭🔷") == "we-know-not-says: sleep(mouse)"
    assert render("🙋🙋🧠💬💤❌🐭🔷") == "we-know-says: sleep-not(mouse)"


def test_speaker_label_is_not_an_undeclared_compound():
    assert lint("🙋🙋🧠💬💤🐭🔷", D) == []
    # the 3-root cap still applies to the label itself
    assert any("roots" in p for p in lint("🐟🐭🧠💭💬💤🐭🔷", D))


def test_speaker_label_after_opener():
    assert words("🔀🐟💬💤🐭🔷") == ["🔀", "🐟💬", "💤", "🐭"]


def test_says_as_root_in_declared_compound_is_untouched():
    # 💬 is first in the compound 💬🦋, so it never reads as a label closer
    assert words("🔨🙋🙋💬🦋🔷") == ["🔨", "🙋🙋", "💬🦋"]


def test_declared_compound_is_one_word():
    assert words("🔧🤖👀🔷") == ["🔧", "🤖", "👀"]
    assert words("🧠📈🐭🔷")[0] == "🧠📈"


def test_infix_glues_one_argument():
    assert words("🔧🤖👀∧👈🌑🔷") == ["🔧", "🤖", "👀∧👈🌑"]
    assert words("👉>🏆⏪+2🔷") == ["👉>🏆⏪+2"]


def test_negation_scope():
    assert render("💤🐭🌕❌🔷") == "sleep(mouse-all-not)"
    assert render("💤❌🐭🌕🔷") == "sleep-not(mouse-all)"


def test_tense_frame():
    assert render("⏪🔷") == "[before]"
    assert render("🕐👉🔷").startswith("[now")


def test_turkish_gloss():
    assert render("👁️🐟🐦🔷", "tr") == "görmek(balık, kuş)"


def test_examples_lint_clean():
    for name in ("fish-and-bird", "attention-abstract"):
        text = (Path(__file__).parents[1] / "examples" / f"{name}.sem").read_text(encoding="utf-8")
        import re
        text = re.sub(r"^#.*$", "", text, flags=re.M)
        assert lint(text, D) == [], name


def test_lint_catches_banned_and_unterminated():
    probs = lint("➕🐭", D)
    assert any("➕" in p for p in probs) and any("🔷" in p for p in probs)


def test_encoder_postfix_negation():
    enc, unk = encode_sentence("see fish bird", D, D.reverse_index())
    assert enc == "👁️🐟🐦🔷" and unk == []
    enc, _ = encode_sentence("no water", D, D.reverse_index())
    assert enc == "💧❌🔷"


def test_names_and_bindings():
    from semagram.lang import apply_bindings
    d = Dictionary.load([])
    body = apply_bindings("👦 ≔ 👤🏷️Mehmet\n👁️👦👤🏷️Ali🔷", d)
    assert render.__globals__["gloss_text"](body, d, "en", show_words=False).split("→ ")[1].strip() == "see(Mehmet (person), Ali(person))"
    assert lint(body, d) == []
    assert any("bind" in p for p in lint("👁️👤🏷️Ali👤🏷️Ali🔷👁️👤🏷️Ali🔷", d))


def test_dictionary_shape():
    """Enforce dictionary/schema.json without taking a dependency on a validator."""
    import json
    from collections import Counter
    from semagram.lang import _norm

    root = Path(__file__).parents[1] / "dictionary"
    files = [root / "core.json"] + sorted((root / "packs").glob("*.json"))
    ENTRY_REQ = {"glyph", "class", "en", "tr", "layer", "transparency"}
    ENTRY_OK = ENTRY_REQ | {"notes", "nsm"}
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data["entries"]
        for e in entries:
            missing = ENTRY_REQ - e.keys()
            assert not missing, f"{path.name} {e.get('glyph')}: missing {missing}"
            assert not e.keys() - ENTRY_OK, f"{path.name} {e['glyph']}: unknown {e.keys() - ENTRY_OK}"
            assert e["class"] in ("root", "particle", "linker", "modifier"), e
            assert e["layer"] in (0, 1, 2), e
            assert e["transparency"] in ("transparent", "translucent", "opaque"), e
        for c in data.get("compounds", []):
            assert {"glyphs", "en"} <= c.keys(), f"{path.name}: {c}"
            assert not c.keys() - {"glyphs", "en", "tr", "layer"}, c
        dups = [g for g, n in Counter(_norm(e["glyph"]) for e in entries).items() if n > 1]
        assert not dups, f"{path.name}: duplicate glyphs {dups}"


def test_pack_glyphs_do_not_shadow_core():
    """Design rule: core beats pack. A pack reusing a core glyph is the bug
    that forced 📥📤 (encoder/decoder) to rebind to 📖⚙️ ✍️⚙️."""
    import json
    from semagram.lang import _norm
    root = Path(__file__).parents[1] / "dictionary"
    core = {_norm(e["glyph"]) for e in json.loads((root / "core.json").read_text(encoding="utf-8"))["entries"]}
    for path in sorted((root / "packs").glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8"))["entries"]:
            assert _norm(e["glyph"]) not in core, f"{path.name}: {e['glyph']} shadows a core glyph"
