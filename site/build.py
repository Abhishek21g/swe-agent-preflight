#!/usr/bin/env python3
"""Build self-contained index.html for CDN-safe deploy."""
from pathlib import Path

ROOT = Path(__file__).parent
template = (ROOT / "index.src.html").read_text()
css = (ROOT / "styles.css").read_text()
js = (ROOT / "app.js").read_text()

html = template.replace("  <!-- INLINE_STYLES -->", f"  <style>\n{css}\n  </style>")
html = html.replace("  <!-- INLINE_SCRIPT -->", f"  <script>\n{js}\n  </script>")
(ROOT / "index.html").write_text(html)
print(f"Built {ROOT / 'index.html'} ({len(html):,} bytes)")
