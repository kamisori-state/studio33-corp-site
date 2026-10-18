"""Show the newest YouTube short near the bottom of index.html.

    python tools/set-latest-short.py --id 2SAyePBC31k --title "題名"

Rewrites the block between the SHORT markers. Prints one JSON line;
"changed": false when that video is already shown.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CHANNEL = "https://www.youtube.com/channel/UCs3y4gp02RC7SV3Hr52Lw-Q"
ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def render(video_id: str, title: str) -> str:
    t = html.escape(title.strip(), quote=True)
    return f"""<section id="shorts" class="shorts">
  <div class="wrap shorts-inner">
    <div class="shorts-frame">
      <iframe src="https://www.youtube-nocookie.com/embed/{video_id}" title="{t}" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe>
    </div>
    <div class="shorts-text">
      <p class="eyebrow">毎朝7時に新作</p>
      <h2>ネットとパソコンの<br>ひとくちヒント動画</h2>
      <p class="shorts-title">{t}</p>
      <p class="shorts-links">
        <a class="btn" href="https://www.youtube.com/shorts/{video_id}" target="_blank" rel="noopener">ユーチューブで見る</a>
        <a class="btn btn-ghost" href="{CHANNEL}" target="_blank" rel="noopener">ほかの動画を見る</a>
      </p>
      <p id="app" class="shorts-note">動画は社内ツール「Short movie」で作成し、当社のYouTubeチャンネルへ投稿しています（<a href="privacy.html">プライバシーポリシー</a>・<a href="terms.html">利用規約</a>）。</p>
    </div>
  </div>
</section>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    args = ap.parse_args()
    if not ID_RE.match(args.id):
        print(json.dumps({"ok": False, "error": f"bad video id {args.id}"}))
        return 1
    home = SITE / "index.html"
    text = home.read_text(encoding="utf-8")
    block = f"<!-- SHORT -->\n{render(args.id, args.title)}\n<!-- /SHORT -->"
    new, n = re.subn(r"<!-- SHORT -->.*?<!-- /SHORT -->", lambda _: block, text, flags=re.S)
    if n != 1:
        print(json.dumps({"ok": False, "error": "index.html has no SHORT markers"}))
        return 1
    if new != text:
        home.write_text(new, encoding="utf-8")
    print(json.dumps({"ok": True, "changed": new != text, "id": args.id}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
