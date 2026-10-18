"""Build the お役立ち記事 (blog) pages from blog/posts/*.md.

Each post is Markdown with YAML front matter:

    ---
    title: 夜になるとWi-Fiが遅いのはなぜ？
    description: 検索結果に出る120字ほどの説明
    date: 2026-10-21
    slug: wifi-slow-at-night
    image: net-trouble.jpg        # file in /img
    category: インターネット・Wi-Fi
    ---
    本文（Markdown）

Outputs blog/<slug>.html, blog/index.html, sitemap.xml and the latest-posts
block on index.html (between the BLOG:LATEST markers). Prints one JSON line.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

import yaml
from markdown_it import MarkdownIt

SITE = Path(__file__).resolve().parent.parent
BASE = "https://studio33-corp.net"
POSTS_DIR = SITE / "blog" / "posts"
REQUIRED = ["title", "description", "date", "slug", "image", "category"]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATIC_PAGES = ["", "pricing.html", "privacy.html", "terms.html"]

md = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table")

HEAD = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image}">
<meta property="og:type" content="{og_type}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../style.css">
{extra}</head>
<body class="lp blog">
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="../"><span class="brand-mark">S</span><span>Studio<span class="brand-33">33</span></span></a>
    <nav class="site-nav">
      <a href="../#internet">ネットの不調</a>
      <a href="../#services">サービス</a>
      <a class="nav-keep" href="../pricing.html">料金</a>
      <a href="./">お役立ち記事</a>
      <a class="btn btn-sm" href="../#contact">ご相談はこちら</a>
    </nav>
  </div>
</header>
"""

FOOT = """
<section class="contact pricing-cta">
  <div class="wrap center">
    <p class="eyebrow light">世田谷区のネット・パソコンのお困りごと</p>
    <h2>自分で直らないときは、<br>Studio33 にご相談ください。</h2>
    <p class="contact-lead">世田谷区内は出張費込み。ご相談・お見積もりは無料です。</p>
    <a class="btn btn-lg btn-white" href="../#contact">無料で相談する</a>
    <p class="contact-mail"><a href="../pricing.html">料金を見る</a></p>
  </div>
</section>

<footer class="site-footer">
  <div class="wrap footer-inner">
    <a class="brand" href="../"><span class="brand-mark">S</span><span>Studio<span class="brand-33">33</span></span></a>
    <p>世田谷区のインターネット・パソコンサポート</p>
    <nav><a href="../pricing.html">料金</a><a href="./">お役立ち記事</a><a href="../privacy.html">プライバシーポリシー</a><a href="../terms.html">利用規約</a></nav>
    <p class="copy">&copy; 2026 Studio33</p>
  </div>
</footer>

<a class="mobile-cta" href="../#contact">無料で相談する</a>
<script src="../chat.js" defer></script>
</body>
</html>
"""


class PostError(Exception):
    pass


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def jp_date(d: dt.date) -> str:
    return f"{d.year}年{d.month}月{d.day}日"


def load_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").lstrip("﻿")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        raise PostError(f"{path.name}: front matter (--- ... ---) is missing")
    meta = yaml.safe_load(m.group(1)) or {}
    missing = [k for k in REQUIRED if not meta.get(k)]
    if missing:
        raise PostError(f"{path.name}: missing {', '.join(missing)}")
    slug = str(meta["slug"])
    if not SLUG_RE.match(slug):
        raise PostError(f"{path.name}: slug must be lowercase letters, digits and hyphens")
    if slug != path.stem:
        raise PostError(f"{path.name}: file name must be <slug>.md ({slug}.md)")
    date = meta["date"]
    if isinstance(date, str):
        date = dt.date.fromisoformat(date)
    if not (SITE / "img" / meta["image"]).is_file():
        raise PostError(f"{path.name}: image img/{meta['image']} not found")
    body = m.group(2).strip()
    if len(body) < 400:
        raise PostError(f"{path.name}: body is too short ({len(body)} chars)")
    return {**meta, "slug": slug, "date": date, "body_html": md.render(body), "chars": len(body)}


def render_post(p: dict) -> str:
    url = f"{BASE}/blog/{p['slug']}.html"
    image = f"{BASE}/img/{p['image']}"
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["description"],
        "datePublished": p["date"].isoformat(),
        "image": image,
        "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": "Studio33"},
        "publisher": {"@type": "Organization", "name": "Studio33"},
    }
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n"
    head = HEAD.format(
        title=esc(f"{p['title']} | Studio33 世田谷区のネット・パソコンサポート"),
        og_title=esc(p["title"]), description=esc(p["description"]),
        url=url, image=image, og_type="article", extra=extra,
    )
    return head + f"""
<main class="post">
  <div class="post-wrap">
    <nav class="crumbs"><a href="../">トップ</a> › <a href="./">お役立ち記事</a> › <span>{esc(p['category'])}</span></nav>
    <p class="post-meta"><span class="post-cat">{esc(p['category'])}</span><time datetime="{p['date'].isoformat()}">{jp_date(p['date'])}</time></p>
    <h1>{esc(p['title'])}</h1>
    <img class="post-hero" src="../img/{esc(p['image'])}" alt="">
    <div class="post-body">
{p['body_html']}
    </div>
    <aside class="post-cta">
      <p class="post-cta-title">世田谷区でネットの不調にお困りなら</p>
      <p>「ネット不調まるごとパック」8,800円（税込・世田谷区内は出張費込み）で、原因の診断からルーターの設定まで対応します。</p>
      <a class="btn" href="../#contact">無料で相談する</a>
    </aside>
  </div>
</main>
""" + FOOT


def card(p: dict, prefix: str) -> str:
    return f"""      <a class="post-card" href="{prefix}{p['slug']}.html">
        <img src="{'../' if prefix == '' else ''}img/{esc(p['image'])}" alt="" loading="lazy">
        <div class="post-card-body">
          <p class="post-meta"><span class="post-cat">{esc(p['category'])}</span><time datetime="{p['date'].isoformat()}">{jp_date(p['date'])}</time></p>
          <h3>{esc(p['title'])}</h3>
          <p>{esc(p['description'])}</p>
        </div>
      </a>"""


def render_index(posts: list[dict]) -> str:
    head = HEAD.format(
        title="お役立ち記事 | Studio33 世田谷区のネット・パソコンサポート",
        og_title="お役立ち記事 | Studio33",
        description="Wi-Fiが遅い・つながらないときの対処法など、世田谷区のネット・パソコンサポート Studio33 が分かりやすく解説します。",
        url=f"{BASE}/blog/", image=f"{BASE}/img/net-hero.jpg", og_type="website", extra="",
    )
    cards = "\n".join(card(p, "") for p in posts) or '      <p class="center">記事は準備中です。</p>'
    return head + f"""
<section class="page-hero">
  <img src="../img/setagaya.jpg" alt="" class="page-hero-img">
  <div class="wrap page-hero-body">
    <p class="hero-kicker">お役立ち記事</p>
    <h1>ネットとパソコンの<br><span class="hl">「困った」</span>を解決するヒント</h1>
    <p class="hero-lead">Wi-Fiが遅い、つながらない。自分で試せることを、世田谷区のネット・パソコンサポート Studio33 が分かりやすく解説します。</p>
  </div>
</section>
<section class="blog-list">
  <div class="wrap">
    <div class="post-grid">
{cards}
    </div>
  </div>
</section>
""" + FOOT


def render_latest(posts: list[dict]) -> str:
    if not posts:
        return ""
    cards = "\n".join(card(p, "blog/") for p in posts[:3])
    return f"""<section id="blog" class="blog-latest">
  <div class="wrap">
    <p class="eyebrow center">お役立ち記事</p>
    <h2 class="center">自分で試せる、ネットとパソコンのヒント</h2>
    <div class="post-grid">
{cards}
    </div>
    <p class="center blog-more"><a class="btn btn-ghost" href="blog/">記事をもっと見る</a></p>
  </div>
</section>"""


def render_sitemap(posts: list[dict]) -> str:
    today = dt.date.today().isoformat()
    urls = [(f"{BASE}/{p}", today) for p in STATIC_PAGES]
    urls.append((f"{BASE}/blog/", posts[0]["date"].isoformat() if posts else today))
    urls += [(f"{BASE}/blog/{p['slug']}.html", p["date"].isoformat()) for p in posts]
    items = "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n'


def main() -> int:
    try:
        posts = [load_post(f) for f in sorted(POSTS_DIR.glob("*.md"))]
        slugs = [p["slug"] for p in posts]
        if len(slugs) != len(set(slugs)):
            raise PostError("duplicate slug")
        posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
        for p in posts:
            (SITE / "blog" / f"{p['slug']}.html").write_text(render_post(p), encoding="utf-8")
        (SITE / "blog" / "index.html").write_text(render_index(posts), encoding="utf-8")
        (SITE / "sitemap.xml").write_text(render_sitemap(posts), encoding="utf-8")
        home = SITE / "index.html"
        text = home.read_text(encoding="utf-8")
        block = f"<!-- BLOG:LATEST -->\n{render_latest(posts)}\n<!-- /BLOG:LATEST -->"
        text, n = re.subn(r"<!-- BLOG:LATEST -->.*?<!-- /BLOG:LATEST -->", lambda _: block, text, flags=re.S)
        if n != 1:
            raise PostError("index.html has no BLOG:LATEST markers")
        home.write_text(text, encoding="utf-8")
    except (PostError, OSError, ValueError, yaml.YAMLError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({
        "ok": True,
        "posts": [{"slug": p["slug"], "title": p["title"], "date": p["date"].isoformat(),
                   "chars": p["chars"], "url": f"{BASE}/blog/{p['slug']}.html"} for p in posts],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
