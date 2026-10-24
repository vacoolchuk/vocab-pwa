#!/usr/bin/env python3
"""For each news item, read the article's own preview image (og:image) and write vocab-pwa/news-images.json.

The app shows that image straight from the publisher's server, with a credit and a link to the article,
the way messaging apps show link previews. Nothing is copied or re-hosted.
"""
import json, os, re, sys, urllib.request, html

ROOT = os.path.join(os.path.dirname(__file__), "..", "vocab-pwa")
NEWS = os.path.join(ROOT, "news.json")
OUT = os.path.join(ROOT, "news-images.json")
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

def og_image(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=20) as r:
        page = r.read(400_000).decode("utf-8", "ignore")
    for pat in (r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image(?::secure_url)?["\']',
                r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)'):
        m = re.search(pat, page, re.I)
        if m:
            return html.unescape(m.group(1))
    return None

def main():
    if not os.path.exists(NEWS):
        return
    with open(NEWS, encoding="utf-8") as f:
        news = json.load(f)
    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f)
    out = {}
    for it in news.get("items", []):
        if it["id"] in old and old[it["id"]].get("url") == it["url"]:
            out[it["id"]] = old[it["id"]]; continue
        try:
            img = og_image(it["url"])
        except Exception as e:
            print(f"no image for {it['id']}: {e}", file=sys.stderr); img = None
        out[it["id"]] = {"url": it["url"], "image": img, "source": it.get("source", "")}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("news images:", sum(1 for v in out.values() if v.get("image")), "of", len(out))

main()
