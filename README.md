# vocab-pwa

My English vocabulary app. GitHub Pages deploys the `vocab-pwa` folder on every push to `main` (see .github/workflows/pages.yml).

- `vocab-pwa/words.json` – words
- `vocab-pwa/stories.json` – stories
- `claude_english_instructions.md` – how Claude and I work on it
- `scriptable-widget.js` – iOS home screen widget

## Offline dictionary
`vocab-pwa/dict.json` is a trimmed copy of Princeton WordNet 3.0 (about 37,000 common words, up to 3 senses each), used by the Catch tab when there is no internet. WordNet licence: `vocab-pwa/WORDNET-LICENSE.txt`. Rebuild with `python scripts/build_dict.py <path to wordnet folder>` (needs `pip install wordfreq`). Online results are always preferred; the bundled dictionary is the last fallback.
