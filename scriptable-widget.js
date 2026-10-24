// Vocabulary widget for the Scriptable app (free, App Store).
// Shows a random word from your Netlify words.json: word, IPA, one meaning, one example.
// Setup: Scriptable -> + -> paste this -> name it "Vocabulary".
// Then: home screen, long press -> + -> Scriptable -> pick a size -> Edit Widget -> Script: Vocabulary.
// Tap the widget to open the full app.

const SITE = "https://vacoolchuk.github.io/vocab-pwa";
// Optional: in Edit Widget -> Parameter, type words to skip, e.g.  frail,petal,dense
const skip = (args.widgetParameter || "").split(",").map(s => s.trim().toLowerCase()).filter(Boolean);

let words = [];
const cacheFile = FileManager.local().joinPath(FileManager.local().documentsDirectory(), "vocab-words.json");
try {
  words = await new Request(SITE + "/words.json").loadJSON();
  FileManager.local().writeString(cacheFile, JSON.stringify(words));
} catch (e) {
  try { words = JSON.parse(FileManager.local().readString(cacheFile)); } catch (_) {}
}

const pool = words.filter(w => !skip.includes(w.word.toLowerCase()));
const w = (pool.length ? pool : words)[Math.floor(Math.random() * Math.max((pool.length ? pool : words).length, 1))];

const widget = new ListWidget();
const grad = new LinearGradient();
grad.colors = [new Color("#5C6BC0"), new Color("#7E57C2")];
grad.locations = [0, 1];
widget.backgroundGradient = grad;
widget.url = SITE;
widget.setPadding(14, 16, 14, 16);

if (!w) {
  const t = widget.addText("Open the app once to load words.");
  t.textColor = Color.white();
} else {
  const family = config.widgetFamily || "medium";
  const d = w.definitions[Math.floor(Math.random() * w.definitions.length)];
  const ex = d.examples[Math.floor(Math.random() * d.examples.length)];

  const title = widget.addText(w.word);
  title.textColor = Color.white();
  title.font = Font.boldSystemFont(family === "small" ? 22 : 28);
  title.minimumScaleFactor = 0.6;

  const ipa = widget.addText("/" + w.pronunciation + "/");
  ipa.textColor = new Color("#ffffff", 0.75);
  ipa.font = Font.systemFont(12);
  widget.addSpacer(6);

  const def = widget.addText(d.def);
  def.textColor = Color.white();
  def.font = Font.mediumSystemFont(family === "small" ? 11 : 13);
  def.lineLimit = family === "small" ? 3 : 2;

  if (family !== "small") {
    widget.addSpacer(6);
    const e = widget.addText(ex);
    e.textColor = new Color("#ffffff", 0.8);
    e.font = Font.italicSystemFont(12);
    e.lineLimit = family === "large" ? 5 : 3;
  }
  widget.addSpacer();
}

// ask iOS to refresh roughly every 30 minutes (iOS decides the real timing)
widget.refreshAfterDate = new Date(Date.now() + 30 * 60 * 1000);

if (config.runsInWidget) Script.setWidget(widget);
else await widget.presentMedium();
Script.complete();
