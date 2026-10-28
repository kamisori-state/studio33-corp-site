"""Build the よくあるお困りごと block on index.html from cases/cases.yml.

Each case is a typical trouble written as an example (not a real customer
record), with the support and the matching price row. The newest 6 are shown
between the CASES markers. Prints one JSON line.

    cases:
      - id: 2026-10-20-printer
        date: 2026-10-20
        category: パソコン
        title: 急にプリンターで印刷できなくなった
        trouble: 昨日まで使えていたのに…（40〜160字）
        support: 接続先と設定を確認して…（40〜160字）
        price: プリンター・テレビのネット接続 3,300円
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

import yaml

SITE = Path(__file__).resolve().parent.parent
SOURCE = SITE / "cases" / "cases.yml"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CATEGORIES = {"パソコン", "インターネット・Wi-Fi", "セキュリティ", "データ・バックアップ"}
SHOWN = 6


class CaseError(Exception):
    pass


def esc(text: str) -> str:
    return html.escape(str(text).strip(), quote=True)


def load_cases() -> list[dict]:
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8").lstrip("﻿")) or {}
    cases = data.get("cases") or []
    seen = set()
    for i, c in enumerate(cases, 1):
        if not isinstance(c, dict):
            raise CaseError(f"case #{i} is not a mapping")
        missing = [k for k in ("id", "date", "category", "title", "trouble", "support", "price") if not c.get(k)]
        if missing:
            raise CaseError(f"case #{i}: missing {', '.join(missing)}")
        cid = str(c["id"])
        if not ID_RE.match(cid):
            raise CaseError(f"case #{i}: id must be lowercase letters, digits and hyphens")
        if cid in seen:
            raise CaseError(f"duplicate id {cid}")
        seen.add(cid)
        if c["category"] not in CATEGORIES:
            raise CaseError(f"{cid}: category must be one of {', '.join(sorted(CATEGORIES))}")
        if len(str(c["title"])) > 30:
            raise CaseError(f"{cid}: title must be 30 characters or less")
        for key in ("trouble", "support"):
            if not 40 <= len(str(c[key]).strip()) <= 160:
                raise CaseError(f"{cid}: {key} must be 40-160 characters")
        if isinstance(c["date"], str):
            c["date"] = dt.date.fromisoformat(c["date"])
        c["id"] = cid
    return cases


def render(shown: list[dict]) -> str:
    if not shown:
        return ""
    cards = "\n".join(f"""      <article class="case" role="group" aria-roledescription="スライド" aria-label="{i} / {len(shown)}">
        <p class="case-cat">{esc(c['category'])}</p>
        <h3>{esc(c['title'])}</h3>
        <dl>
          <dt>お困りごと</dt><dd>{esc(c['trouble'])}</dd>
          <dt>Studio33 の対応</dt><dd>{esc(c['support'])}</dd>
        </dl>
        <p class="case-price">{esc(c['price'])}</p>
      </article>""" for i, c in enumerate(shown, 1))
    return f"""<section id="cases" class="cases">
  <div class="wrap">
    <p class="eyebrow center">よくあるお困りごと</p>
    <h2 id="cases-heading" class="center">こんなとき、ご相談ください</h2>
    <div class="cases-carousel" role="region" aria-roledescription="カルーセル" aria-labelledby="cases-heading">
    <p id="cases-help" class="cases-carousel-help">左右にスクロールしてご覧ください。キーボードでは左右矢印・Home・Endキーで操作できます。</p>
    <div id="cases-track" class="cases-carousel-track" tabindex="0" aria-label="ご相談例一覧" aria-describedby="cases-help">
{cards}
    </div>
    <div class="cases-carousel-controls" hidden>
      <button type="button" data-cases-prev aria-controls="cases-track" aria-label="前のページ" aria-disabled="true">← 前へ</button>
      <span class="cases-carousel-status" aria-live="polite" aria-atomic="true"></span>
      <button type="button" data-cases-next aria-controls="cases-track" aria-label="次のページ">次へ →</button>
    </div>
    </div>
    <p class="center case-note">よくあるご相談をもとにした例です。料金は税込・世田谷区内は出張費込みです。</p>
  </div>
</section>"""


def main() -> int:
    try:
        cases = load_cases()
        cases.sort(key=lambda c: (c["date"], c["id"]), reverse=True)
        home = SITE / "index.html"
        text = home.read_text(encoding="utf-8")
        block = f"<!-- CASES -->\n{render(cases[:SHOWN])}\n<!-- /CASES -->"
        text, n = re.subn(r"<!-- CASES -->.*?<!-- /CASES -->", lambda _: block, text, flags=re.S)
        if n != 1:
            raise CaseError("index.html has no CASES markers")
        home.write_text(text, encoding="utf-8")
    except (CaseError, OSError, ValueError, yaml.YAMLError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "cases": len(cases),
                      "shown": [{"id": c["id"], "title": c["title"]} for c in cases[:SHOWN]]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
