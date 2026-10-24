#!/usr/bin/env python3
"""Generate British neural-voice audio for stories and news with edge-tts.

Writes vocab-pwa/audio/<kind>-<id>.mp3 and vocab-pwa/audio/index.json.
Only items whose text changed (or that have no file yet) are generated.
"""
import asyncio, hashlib, json, os, re, sys
import edge_tts

ROOT = os.path.join(os.path.dirname(__file__), "..", "vocab-pwa")
OUT = os.path.join(ROOT, "audio")
VOICES = {"story": "en-GB-RyanNeural", "news": "en-GB-SoniaNeural", "word": "en-GB-RyanNeural"}
RATE = "-8%"

def clean(text):
    text = re.sub(r"\{\{([^|]+)\|[^}]+\}\}", r"\1", text)
    text = text.replace("\n", ". ").replace("..", ".")
    return re.sub(r"\s+", " ", text).strip()

def slug(word):
    return re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-")

def items():
    with open(os.path.join(ROOT, "words.json"), encoding="utf-8") as f:
        for w in json.load(f):
            yield "word", slug(w["word"]), w["word"]
    with open(os.path.join(ROOT, "stories.json"), encoding="utf-8") as f:
        for s in json.load(f):
            yield "story", s["id"], s.get("title", "") + ". " + s["text"]
    p = os.path.join(ROOT, "news.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for n in json.load(f).get("items", []):
                yield "news", n["id"], n.get("title", "") + ". " + n["text"]

async def main():
    os.makedirs(OUT, exist_ok=True)
    idx_path = os.path.join(OUT, "index.json")
    index = {}
    if os.path.exists(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            index = json.load(f)
    made = kept = failed = 0
    new_index = {}
    for kind, id_, raw in items():
        text = clean(raw)
        rate = "-2%" if kind == "word" else RATE
        h = hashlib.sha1((VOICES[kind] + rate + text).encode("utf-8")).hexdigest()[:10]
        fname = f"{kind}-{id_}.mp3"
        key = f"{kind}:{id_}"
        path = os.path.join(OUT, fname)
        if index.get(key, {}).get("hash") == h and os.path.exists(path):
            new_index[key] = index[key]; kept += 1; continue
        try:
            await edge_tts.Communicate(text, VOICES[kind], rate=rate).save(path)
            new_index[key] = {"file": fname, "hash": h, "voice": VOICES[kind]}
            made += 1
        except Exception as e:  # keep going: a missing file just falls back to the phone voice
            print(f"FAILED {key}: {e}", file=sys.stderr); failed += 1
            if key in index and os.path.exists(path):
                new_index[key] = index[key]
    wanted = {v["file"] for v in new_index.values()}
    for f in os.listdir(OUT):
        if f.endswith(".mp3") and f not in wanted:
            os.remove(os.path.join(OUT, f))
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(new_index, f, indent=1)
    print(f"audio: {made} generated, {kept} kept, {failed} failed")

asyncio.run(main())
