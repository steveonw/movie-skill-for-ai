"""Story/script parsing for Narration Studio.

Turns a plain-text or Markdown story (or a filmkit script.json) into an ordered
list of items: speech segments and explicit pause requests.

Three text fields are kept per segment, and never merged:
  source_text   exact slice of the author's file (never modified)
  display_text  source_text with Markdown markers removed (for captions/labels)
  spoken_text   display_text after the pronunciation map (what the TTS hears)
"""
import json
import re
from pathlib import Path

SPEAKER_RE = re.compile(r"^\s*([A-Z][\w'\-]*(?: [A-Z][\w'\-]*){0,2})\s*:\s+(\S.*)$")
PAUSE_RE = re.compile(r"^\s*\[(pause|beat)(?:\s+([0-9]*\.?[0-9]+)\s*s?)?\]\s*$", re.I)
HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$")
RULE_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TERMINATOR_RE = re.compile(r"[.!?…]+[\"'”’)\]]*(?=\s+)")
ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "st", "vs", "etc", "prof", "sr", "jr",
                 "no", "fig", "e.g", "i.e", "approx", "dept", "mt", "lt", "col"}


def clean_markdown(text):
    """Strip inline Markdown markers that should be neither shown nor spoken."""
    text = BULLET_RE.sub("", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)      # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)       # links
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text)
    text = re.sub(r"(?<!\w)([*_])(?!\s)(.+?)(?<!\s)\1(?!\w)", r"\2", text)
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    """Return (start, end) character spans of sentences inside one paragraph."""
    spans, start = [], 0
    for m in TERMINATOR_RE.finditer(text):
        end = m.end()
        before = text[start:m.start()].split()
        last_word = before[-1].lower().rstrip(".") if before else ""
        if m.group(0) == "." and last_word in ABBREVIATIONS:
            continue
        nxt = text[end:].lstrip()
        if nxt and not (nxt[0].isupper() or nxt[0].isdigit() or nxt[0] in "\"'“‘([*_"):
            continue
        if text[start:end].strip():
            spans.append((start, end))
        start = end
    if text[start:].strip():
        spans.append((start, len(text)))
    trimmed = []
    for s, e in spans:
        while s < e and text[s].isspace():
            s += 1
        trimmed.append((s, e))
    return trimmed


def compile_pronunciations(entries):
    """entries: {"DOOM": "doom"} or [{"match": .., "say": .., "ignore_case": bool}]."""
    if isinstance(entries, dict):
        entries = [{"match": k, "say": v} for k, v in entries.items()]
    compiled = []
    for e in entries or []:
        flags = re.I if e.get("ignore_case") else 0
        pattern = re.compile(r"(?<!\w)" + re.escape(e["match"]) + r"(?!\w)", flags)
        compiled.append((e["match"], e["say"], pattern))
    # Longest match first so "0.000002 FPS" wins over "FPS".
    compiled.sort(key=lambda item: -len(item[0]))
    return compiled


def apply_pronunciations(text, compiled):
    subs = []
    for match, say, pattern in compiled:
        text, n = pattern.subn(say, text)
        if n:
            subs.append({"from": match, "to": say, "count": n})
    return text, subs


EDGE_PUNCT = "\"'“”‘’()[]{}.,!?;:…*_—–-"


def word_units(display, compiled, ids=None):
    """Split display text into words with stable IDs and their spoken form.

    Pronunciation matches are tracked by character span, so a replacement
    inside one word ("Dr." -> "Doctor") stays on that word, and a phrase
    spanning several words ("0.000002 FPS") is spoken on its first word with
    the rest marked as covered by it. Returns [{"id","text","spoken"}], one
    entry per word containing a letter or digit. `ids` (from script.json)
    replaces the generated w1..wn when the counts agree.
    """
    hits = []
    for _match, say, pattern in compiled:  # longest-first, non-overlapping
        for m in pattern.finditer(display):
            if all(m.end() <= a or m.start() >= b for a, b, _ in hits):
                hits.append((m.start(), m.end(), say))
    hits.sort()
    units = []
    for tok in re.finditer(r"\S+", display):
        a, b = tok.span()
        out, p, covered_by_previous = [], a, False
        while p < b:
            hit = next((h for h in hits if h[0] <= p < h[1]), None)
            if hit is None:
                out.append(display[p])
                p += 1
            elif hit[0] == p:
                out.append(hit[2])
                p = min(hit[1], b) if hit[1] <= b else b
            else:  # inside a phrase that started in an earlier word
                covered_by_previous = True
                p = min(hit[1], b)
        text = tok.group().strip(EDGE_PUNCT)
        if not any(ch.isalnum() for ch in text):
            continue
        spoken = "".join(out).strip(EDGE_PUNCT)
        unit = {"id": None, "text": text, "spoken": spoken}
        if covered_by_previous and not spoken:
            unit["spoken_with_previous"] = True
        units.append(unit)
    if ids and len(ids) == len(units):
        for unit, wid in zip(units, ids):
            unit["id"] = str(wid)
    else:
        for i, unit in enumerate(units, 1):
            unit["id"] = f"w{i}"
    return units


def _segment(index, paragraph, kind, speaker, source, compiled, word_ids=None):
    display = clean_markdown(source)
    spoken, subs = apply_pronunciations(display, compiled)
    return {"type": "segment", "index": index, "paragraph": paragraph, "kind": kind,
            "speaker": speaker, "source_text": source, "display_text": display,
            "spoken_text": spoken, "substitutions": subs,
            "words": word_units(display, compiled, word_ids)}


def parse_story(text, pronunciations=None, detect_speakers=True):
    """Parse plain text / Markdown into items.

    Paragraphs are separated by blank lines. A line "Name: words" (1-3
    capitalised words) assigns a speaker; "[pause]", "[pause 1.5s]" or
    "[beat]" on its own line requests a pause; a Markdown rule (---) is a
    scene break; "# Heading" lines become heading segments.
    """
    compiled = compile_pronunciations(pronunciations)
    items, paragraph, index = [], 0, 0
    blocks = re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n"))
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        paragraph += 1
        buffer, speaker = [], "narrator"

        def flush():
            nonlocal index, buffer
            joined = " ".join(ln.strip() for ln in buffer)
            for s, e in split_sentences(joined):
                index += 1
                seg = _segment(index, paragraph, "line", speaker, joined[s:e], compiled)
                if seg["spoken_text"].strip():
                    items.append(seg)
                else:
                    index -= 1
            buffer = []

        for line in lines:
            pause = PAUSE_RE.match(line)
            heading = HEADING_RE.match(line)
            sp = SPEAKER_RE.match(line) if detect_speakers else None
            if pause or heading or RULE_RE.match(line) or sp:
                flush()
                speaker = "narrator"
            if pause:
                kind = pause.group(1).lower()
                secs = float(pause.group(2)) if pause.group(2) else None
                items.append({"type": "pause", "kind": kind, "seconds": secs})
            elif RULE_RE.match(line):
                items.append({"type": "pause", "kind": "scene_break", "seconds": None})
            elif heading:
                index += 1
                items.append(_segment(index, paragraph, "heading", "narrator",
                                      heading.group(2), compiled))
            elif sp:
                speaker = sp.group(1)
                buffer.append(sp.group(2))
            else:
                buffer.append(line)
        flush()
    _assign_ids(items)
    return items


def parse_script_json(data, pronunciations=None):
    """Accept a filmkit/script@1.x file. Its segment IDs are kept as-is."""
    compiled = compile_pronunciations(pronunciations)
    items = []
    for i, seg in enumerate(data.get("segments", []), 1):
        word_ids = [w["id"] for w in seg.get("words", []) if "id" in w] or None
        item = _segment(i, seg.get("paragraph", i), seg.get("kind", "line"),
                        seg.get("speaker", "narrator"), seg["text"], compiled, word_ids)
        item["id"] = str(seg["id"])
        items.append(item)
        if seg.get("pause_after") is not None:
            items.append({"type": "pause", "kind": "pause", "seconds": float(seg["pause_after"])})
    return items


def _assign_ids(items):
    """Positional IDs for plain-text input. Opaque to consumers; supply a
    script.json when IDs must survive inserted or deleted lines."""
    for item in items:
        if item["type"] == "segment" and "id" not in item:
            item["id"] = f"s{item['index']:03d}"


def load_input(path, pronunciations=None, detect_speakers=True):
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
        if not str(data.get("schema", "")).startswith("filmkit/script@1"):
            raise ValueError(f"{path}: expected a filmkit/script@1.x file")
        return parse_script_json(data, pronunciations), raw
    return parse_story(raw, pronunciations, detect_speakers), raw
