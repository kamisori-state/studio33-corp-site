"""Read-only HTML/content regression checks. Run: python tools/test_smartphone_support.py"""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.stack = []
        self.errors = []
        self.feed(source)
        if self.stack:
            self.errors.append(f'Unclosed tags: {self.stack}')

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f'Unexpected closing tag: {tag}; stack: {self.stack}')
        else:
            self.stack.pop()


class SiteChecks(unittest.TestCase):
    def test_smartphone_discovery(self):
        source = (ROOT / 'index.html').read_text(encoding='utf-8')
        doc = Document(source)
        self.assertRegex(source, r'<title>[^<]*スマホ')
        for key, value in [('name', 'description'), ('property', 'og:title'), ('property', 'og:description')]:
            meta = next(a for t, a in doc.tags if t == 'meta' and a.get(key) == value)
            self.assertIn('スマホ', meta['content'])
        hero = source.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
        self.assertIn('href="#smartphone"', hero)
        card = source.split('<article id="smartphone"', 1)[1].split('</article>', 1)[0]
        for text in ['iPhone', 'Android', '通知', '音', '文字サイズ', '動作が重い', '容量', 'お見積もり', 'href="#contact"']:
            self.assertIn(text, card)

    def test_support_scope_and_existing_prices(self):
        source = (ROOT / 'index.html').read_text(encoding='utf-8')
        card = source.split('<article id="smartphone"', 1)[1].split('</article>', 1)[0]
        for unsupported in ['画面修理', 'バッテリー交換', 'ロック解除', 'データ復旧', '必ず直る']:
            self.assertNotIn(unsupported, card)
        self.assertNotRegex(card, r'\d[\d,]*円')
        self.assertIn('設定・操作サポートの作業は有料', card)
        original = subprocess.check_output(['git', 'show', 'HEAD:pricing.html'], cwd=ROOT).decode('utf-8')
        current = (ROOT / 'pricing.html').read_text(encoding='utf-8')
        amounts = r'\d[\d,]*円'
        self.assertEqual(re.findall(amounts, original), re.findall(amounts, current))

    def test_form_options(self):
        doc = Document((ROOT / 'index.html').read_text(encoding='utf-8'))
        self.assertTrue(any(t == 'input' and a.get('type') == 'checkbox' and 'スマホ' in a.get('value', '') for t, a in doc.tags))
        source = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('<option>iPhone</option>', source)
        self.assertIn('<option>Android</option>', source)
        self.assertIn('https://formsubmit.co/studio33corp@gmail.com', source)

    def test_smartphone_pricing(self):
        source = (ROOT / 'pricing.html').read_text(encoding='utf-8')
        self.assertIn('スマートフォン（携帯）', source)
        self.assertIn('内容を確認してお見積もり', source)
        self.assertIn('ご相談・お見積もりは無料', source)
        self.assertIn('設定・操作サポートの作業は有料', source)

    def test_html_structure(self):
        for name in ['index.html', 'pricing.html']:
            with self.subTest(page=name):
                doc = Document((ROOT / name).read_text(encoding='utf-8'))
                self.assertEqual([], doc.errors)
                ids = [a['id'] for _, a in doc.tags if 'id' in a]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(1, sum(t == 'h1' for t, _ in doc.tags))

    def test_local_links_and_assets(self):
        count = 0
        for name in ['index.html', 'pricing.html']:
            page = ROOT / name
            doc = Document(page.read_text(encoding='utf-8'))
            for tag, attrs in doc.tags:
                for attr in ['href', 'src']:
                    raw = attrs.get(attr)
                    if raw is None:
                        continue
                    url = urlsplit(raw)
                    if url.scheme or url.netloc:
                        continue
                    target = (ROOT / unquote(url.path.lstrip('/'))) if url.path.startswith('/') else (page.parent / unquote(url.path))
                    if not url.path:
                        target = page
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), f'{name}: missing {raw}')
                    if url.fragment and target.suffix == '.html':
                        other = Document(target.read_text(encoding='utf-8'))
                        self.assertIn(unquote(url.fragment), [a.get('id') for _, a in other.tags], f'{name}: missing anchor {raw}')
                    if tag == 'img':
                        self.assertIn('alt', attrs)
                    count += 1
        print(f'Checked {count} local links/assets (no external requests or form submissions).')

    def test_generated_cases_structure_and_data(self):
        from test_home_carousel import HomeCarouselChecks
        HomeCarouselChecks('test_generated_structure_and_latest_data').test_generated_structure_and_latest_data()


if __name__ == '__main__':
    unittest.main(verbosity=2)
