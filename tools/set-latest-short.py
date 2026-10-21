"""Show the newest YouTube short near the bottom of index.html.

    python tools/set-latest-short.py --id 2SAyePBC31k --title "題名" --video path/to/short.mp4

Rewrites the block between the SHORT markers. The vertical poster is cut from
the local video with ffmpeg (img/shorts/<id>.jpg); the YouTube player loads only
when the poster is clicked, because its own thumbnail is letterboxed 16:9.
Prints one JSON line; "changed": false when that video is already shown.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CHANNEL = "https://www.youtube.com/channel/UCs3y4gp02RC7SV3Hr52Lw-Q"
ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
POSTERS = SITE / "img" / "shorts"
FFMPEG = shutil.which("ffmpeg") or str(Path.home() / "AppData/Local/Microsoft/WinGet/Links/ffmpeg.exe")


def make_poster(video_id: str, video: Path) -> Path:
    POSTERS.mkdir(parents=True, exist_ok=True)
    poster = POSTERS / f"{video_id}.jpg"
    if not poster.is_file():
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", "1.5", "-i", str(video), "-frames:v", "1",
                        "-vf", "scale=540:960", "-q:v", "4", str(poster)], check=True)
    for old in POSTERS.glob("*.jpg"):
        if old != poster:
            old.unlink()
    return poster


def render(video_id: str, title: str) -> str:
    t = html.escape(title.strip(), quote=True)
    return f"""<section id="shorts" class="shorts">
  <div class="wrap shorts-inner">
    <div class="shorts-frame">
      <a class="shorts-poster" href="https://www.youtube.com/shorts/{video_id}" data-id="{video_id}" target="_blank" rel="noopener" aria-label="動画を再生">
        <img src="img/shorts/{video_id}.jpg" alt="{t}" loading="lazy">
        <span class="shorts-play" aria-hidden="true"></span>
      </a>
    </div>
    <div class="shorts-text">
      <p class="eyebrow">毎朝7時に新作</p>
      <h2>ネット・パソコン・スマホの<br>ひとくちヒント動画</h2>
      <p class="shorts-title">{t}</p>
      <p class="shorts-links">
        <a class="btn" href="https://www.youtube.com/shorts/{video_id}" target="_blank" rel="noopener">ユーチューブで見る</a>
        <a class="btn btn-ghost" href="{CHANNEL}" target="_blank" rel="noopener">ほかの動画を見る</a>
      </p>
      <p id="app" class="shorts-note">動画は社内ツール「Short movie」で作成し、当社のYouTubeチャンネルへ投稿しています（<a href="privacy.html">プライバシーポリシー</a>・<a href="terms.html">利用規約</a>）。</p>
    </div>
  </div>
  <script>
    document.querySelector(".shorts-poster").addEventListener("click", function (e) {{
      e.preventDefault();
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + this.dataset.id + "?autoplay=1&playsinline=1";
      f.title = this.querySelector("img").alt;
      f.allow = "autoplay; encrypted-media; picture-in-picture";
      f.referrerPolicy = "strict-origin-when-cross-origin";
      f.allowFullscreen = true;
      this.replaceWith(f);
    }});
  </script>
</section>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--video", required=True, type=Path, help="local mp4 for the poster")
    args = ap.parse_args()
    if not ID_RE.match(args.id):
        print(json.dumps({"ok": False, "error": f"bad video id {args.id}"}))
        return 1
    try:
        make_poster(args.id, args.video)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"ok": False, "error": f"poster: {exc}"}, ensure_ascii=False))
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
