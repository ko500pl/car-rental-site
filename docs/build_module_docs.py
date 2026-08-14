from pathlib import Path
from html import escape
import markdown

ROOT = Path(__file__).resolve().parent
FILES = [p for p in ROOT.glob("*.md") if p.name not in {"LOCAL_IMPLEMENTATION_STATUS.md", "REQUIREMENTS_MATRIX.md"}]
STYLE = """body{font:15px/1.65 system-ui;max-width:940px;margin:36px auto;padding:0 22px;color:#172033}a{color:#087ea4}h1,h2{line-height:1.2}h1{font-size:30px}h2{margin-top:30px;border-top:1px solid #dce2ea;padding-top:18px}code{background:#eef2f6;padding:2px 5px;border-radius:4px}li{margin:5px 0}.back{display:inline-block;margin-bottom:18px}.meta{color:#64748b;font-size:13px}"""

for source in FILES:
    body = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
    title = source.stem.replace("-", " ")
    html = ("<!doctype html><html lang=\"ka\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\">"
            f"<title>{escape(title)}</title><style>{STYLE}</style></head><body>"
            '<a class="back" href="00-DOCUMENTATION-INDEX.html">← დოკუმენტაციის ინდექსი</a>'
            f'<div class="meta">ლოკალური დოკუმენტაცია · 2026-08-14</div>{body}</body></html>')
    source.with_suffix(".html").write_text(html, encoding="utf-8")

print(f"Generated {len(FILES)} module documentation pages")
