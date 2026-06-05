from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"

index_path = WEB_DIR / "index.html"
styles_path = WEB_DIR / "styles.css"
script_path = WEB_DIR / "script.js"
out_path = WEB_DIR / "nyangnyang-chur-landing-standalone.html"

html = index_path.read_text(encoding="utf-8")
styles = styles_path.read_text(encoding="utf-8")
script = script_path.read_text(encoding="utf-8")

html = html.replace(
    '<link rel="stylesheet" href="./styles.css" />',
    f"<style>\n{styles}\n</style>",
)
html = html.replace(
    '<script src="./script.js"></script>',
    f"<script>\n{script}\n</script>",
)

out_path.write_text(html, encoding="utf-8")

print(
    {
        "output": str(out_path),
        "characters": len(html),
        "has_inline_css": "<style>" in html,
        "has_inline_js": "<script>" in html and "const parts" in html,
    }
)
