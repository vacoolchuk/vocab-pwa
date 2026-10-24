#!/usr/bin/env python3
"""Build vocab-pwa/dict.json: a small offline English dictionary for the Catch tab.

Source: Princeton WordNet 3.0 (free licence, https://wordnet.princeton.edu/license-and-commercial-use),
words picked by frequency with the wordfreq package. Run it by hand when you want to rebuild:
    python scripts/build_dict.py /path/to/wordnet   (the folder that holds data.noun, index.noun, ...)
"""
import json, os, re, sys
from wordfreq import top_n_list

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "vocab-pwa", "dict.json")
TOP, SENSES, MAXLEN = 45000, 3, 110
POS = {"noun": "n", "verb": "v", "adj": "a", "adv": "r"}

def read_data(name):
    out = {}
    with open(os.path.join(SRC, "data." + name), encoding="utf-8") as f:
        for line in f:
            if line.startswith("  "): continue
            head, _, gloss = line.partition("|")
            off = head.split()[0]
            d = gloss.split(";")[0].strip()
            d = re.sub(r"\s+", " ", d)
            out[off] = d
    return out

def read_index(name):
    out = {}
    with open(os.path.join(SRC, "index." + name), encoding="utf-8") as f:
        for line in f:
            if line.startswith("  "): continue
            p = line.split()
            lemma, cnt, pc = p[0], int(p[2]), int(p[3])
            offs = p[6 + pc:]
            out[lemma] = offs[:cnt]
    return out

data = {n: read_data(n) for n in POS}
index = {n: read_index(n) for n in POS}
words = [w for w in top_n_list("en", 90000) if re.fullmatch(r"[a-z]+", w)]
res = {}
for w in words:
    senses = []
    for n in ("noun", "verb", "adj", "adv"):
        for off in index[n].get(w, [])[:SENSES]:
            d = data[n].get(off, "")
            if not d: continue
            if len(d) > MAXLEN: d = d[:MAXLEN].rsplit(" ", 1)[0] + "..."
            senses.append([POS[n], d])
    if senses:
        res[w] = senses[:SENSES + 1]
    if len(res) >= TOP: break
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, separators=(",", ":"))
print(len(res), "words,", os.path.getsize(OUT) // 1024, "KB")
