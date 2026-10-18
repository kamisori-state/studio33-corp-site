"""Build the お客さまの声 block on index.html from voices/voices.yml.

voices.yml holds real customer comments entered by the owner, each with
consent: true. With --publish-next, the first consented voice that is not
yet published is added (its id goes to voices/published.json with today's
date). The block between the VOICES markers shows the newest 6 published
voices; it is empty until the first one is published. Prints one JSON line.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

import yaml

SITE = Path(__file__).resolve().parent.parent
SOURCE = SITE / "voices" / "voices.yml"
LOG = SITE / "voices" / "published.json"
ID_RE = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
SHOWN = 6


class VoiceError(Exception):
    pass


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def load_voices() -> list[dict]:
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8").lstrip("﻿")) or {}
    voices = data.get("voices") or []
    seen = set()
    for i, v in enumerate(voices, 1):
        if not isinstance(v, dict):
            raise VoiceError(f"voice #{i} is not a mapping")
        missing = [k for k in ("id", "text", "who", "service", "received") if not v.get(k)]
        if missing:
            raise VoiceError(f"voice #{i}: missing {', '.join(missing)}")
        vid = str(v["id"])
        if not ID_RE.match(vid):
            raise VoiceError(f"voice #{i}: id must be letters, digits and hyphens")
        if vid in seen:
            raise VoiceError(f"duplicate id {vid}")
        seen.add(vid)
        if not 20 <= len(str(v["text"]).strip()) <= 300:
            raise VoiceError(f"{vid}: text must be 20-300 characters")
        v["id"] = vid
    return voices


def load_log() -> dict:
    return json.loads(LOG.read_text(encoding="utf-8")) if LOG.is_file() else {}


def render(shown: list[dict]) -> str:
    if not shown:
        return ""
    cards = "\n".join(f"""      <figure class="voice">
        <blockquote>{esc(str(v['text']).strip())}</blockquote>
        <figcaption><span class="voice-who">{esc(v['who'])}</span><span class="voice-service">{esc(v['service'])}</span></figcaption>
      </figure>""" for v in shown)
    return f"""<section id="voices" class="voices">
  <div class="wrap">
    <p class="eyebrow center">お客さまの声</p>
    <h2 class="center">ご利用いただいた方から</h2>
    <div class="voice-list">
{cards}
    </div>
    <p class="center voice-note">ご本人の了承をいただいて掲載しています。</p>
  </div>
</section>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish-next", action="store_true", help="publish the next waiting voice")
    args = ap.parse_args()
    try:
        voices = load_voices()
        log = load_log()
        consented = [v for v in voices if v.get("consent") is True]
        waiting = [v for v in consented if v["id"] not in log]
        added = None
        if args.publish_next and waiting:
            added = waiting.pop(0)
            log[added["id"]] = dt.date.today().isoformat()
            LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        live = [v for v in consented if v["id"] in log]
        live.sort(key=lambda v: (log[v["id"]], v["id"]), reverse=True)
        home = SITE / "index.html"
        text = home.read_text(encoding="utf-8")
        block = f"<!-- VOICES -->\n{render(live[:SHOWN])}\n<!-- /VOICES -->"
        text, n = re.subn(r"<!-- VOICES -->.*?<!-- /VOICES -->", lambda _: block, text, flags=re.S)
        if n != 1:
            raise VoiceError("index.html has no VOICES markers")
        home.write_text(text, encoding="utf-8")
    except (VoiceError, OSError, ValueError, yaml.YAMLError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({
        "ok": True,
        "added": added and {"id": added["id"], "who": added["who"]},
        "published": len(live),
        "waiting": len(waiting),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
