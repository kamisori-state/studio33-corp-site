"""Read-only service checks: python -m unittest discover -s tools -p 'test_*.py' -v"""
from test_smartphone_support import Document, ROOT
from pathlib import Path
import collections
import json
import re
import subprocess
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

import os
BASE = os.environ.get('STUDIO33_REVIEW_BASELINE')

def text(name):
    return (ROOT / name).read_text(encoding='utf-8')

def original(name):
    return subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT).decode('utf-8')

class DevelopmentChecks(unittest.TestCase):
    def test_regeneration_survival_in_disposable_copy(self):
        with tempfile.TemporaryDirectory(prefix='studio33-development-build-') as temp:
            site = Path(temp) / 'site'
            shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', '__pycache__', 'sns-img'))
            for script in ['build-cases.py', 'build-blog.py']:
                result = subprocess.run([sys.executable, str(site / 'tools' / script)], capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(0, result.returncode, script + ': ' + result.stderr)
            rebuilt = (site / 'index.html').read_text(encoding='utf-8')
            self.assertIn('class="development-entry"', rebuilt)
            self.assertIn('id="development-inquiry"', rebuilt)
            self.assertIn('https://studio33-corp.net/development.html', (site / 'sitemap.xml').read_text(encoding='utf-8'))
            self.assertEqual(text('development.html'), (site / 'development.html').read_text(encoding='utf-8'))
            strip_generated = lambda s: re.sub(r'<!-- (CASES|BLOG:LATEST) -->.*?<!-- /\1 -->', '', s, flags=re.S)
            self.assertEqual(strip_generated(text('index.html')), strip_generated(rebuilt))

    def test_development_hero_image(self):
        source = text('development.html')
        doc = Document(source)
        images = [a for t,a in doc.tags if t == 'img' and a.get('class') == 'development-hero-image']
        self.assertEqual(1, len(images), 'The development hero needs its own image')
        image = images[0]
        self.assertEqual('img/development-hero.webp', image.get('src'))
        self.assertTrue((ROOT / image['src']).is_file())
        self.assertTrue(image.get('alt'))
        self.assertEqual('high', image.get('fetchpriority'))
        self.assertTrue(int(image['width']) > int(image['height']) > 0)
        self.assertIn('画像はサービス内容のイメージです', source)
        self.assertIn('AI生成', source)
        self.assertIn('img/development-hero.webp', source.split('og:image')[1].split('>')[0])
        css = text('style.css')
        self.assertIn('.development-hero-image', css)
        self.assertIn('object-fit: cover', css)

    def test_service_scope_and_terms(self):
        source = text('development.html')
        for token in ['中小企業', '小規模事業者', 'ご相談例', '業務ツール', '社内用Webアプリ', 'Excel', 'CSV', '定型業務', '小規模改善', '初回相談', '無料', '設計・開発は有料', '個別見積', 'サーバー', '外部サービス', '保守', '対応可否', '仕様', '納期', '納品', '検収', '見積もり・契約時', '機密情報', '個人情報', '概要のみ', '要件整理', '見積もり合意', '開発・確認']:
            self.assertIn(token, source, token)
        self.assertNotRegex(source, r'\d[\d,]*円|最安|必ず|即日|実績多数')

    def test_discovery_and_form_contract(self):
        for name in ['index.html', 'pricing.html']:
            self.assertTrue('href="development.html"' in text(name), name + ': missing service link')
        src = text('index.html')
        self.assertIn('href="development.html"', src.split('<section class="hero">')[1].split('</section>')[0])
        self.assertIn('受託開発のご相談', src)
        new = Document(src)
        forms = [a for t,a in new.tags if t == 'form']
        self.assertEqual(1, len(forms))
        self.assertEqual('https://formsubmit.co/studio33corp@gmail.com', forms[0].get('action'))
        self.assertEqual('POST', forms[0].get('method'))
        names = {a.get('name') for t,a in new.tags if t in ['input','select','textarea']}
        self.assertTrue({'ご相談の内容', 'お困りごと'}.issubset(names))
        if BASE:
            old = Document(original('index.html'))
            self.assertEqual([a for t,a in old.tags if t == 'form'], forms)
            contract = lambda doc: collections.Counter((t, a.get('name'), a.get('type'), a.get('value')) for t,a in doc.tags if t in ['input','select','textarea'])
            self.assertFalse(contract(old) - contract(new), 'Existing form keys/options changed')
        self.assertIn('service=development#contact', text('development.html'))
        self.assertIn('contact-service.js', src)

    def test_metadata_and_sitemap(self):
        source = text('development.html')
        doc = Document(source)
        for key,val in [('name','description'),('property','og:title'),('property','og:description'),('property','og:url'),('property','og:type'),('property','og:image')]:
            self.assertTrue(any(t == 'meta' and a.get(key) == val and a.get('content') for t,a in doc.tags), val)
        self.assertTrue(any(t=='link' and a.get('rel')=='canonical' and a.get('href')=='https://studio33-corp.net/development.html' for t,a in doc.tags))
        self.assertIn('https://studio33-corp.net/development.html', text('sitemap.xml'))
        self.assertRegex(text('tools/build-blog.py'), r'STATIC_PAGES = .*"development.html"')
        ET.fromstring(text('sitemap.xml'))

    @unittest.skipUnless(BASE, 'One-time change review: set STUDIO33_REVIEW_BASELINE explicitly')
    def test_baseline_protection(self):
        for name in ['index.html','pricing.html']:
            self.assertEqual(re.findall(r'\d[\d,]*円', original(name)), re.findall(r'\d[\d,]*円', text(name)))
        from test_home_carousel import case_content
        self.assertEqual(case_content(original('index.html')), case_content(text('index.html')))
        for marker in ['BLOG:LATEST','VOICES','SHORT']:
            pattern = r'<!-- ' + marker + r' -->.*?<!-- /' + marker + r' -->'
            self.assertEqual(re.findall(pattern, original('index.html'), re.S), re.findall(pattern, text('index.html'), re.S), marker)
        for name in ['cases/cases.yml','voices/voices.yml','personal-info.html','privacy.html','terms.html','chat.js']:
            self.assertEqual(original(name), text(name), name)

    def test_html_links_anchors_jsonld(self):
        count = 0
        for name in ['index.html','pricing.html','development.html']:
            source = text(name)
            doc = Document(source)
            self.assertEqual([], doc.errors, name)
            ids = [a['id'] for _,a in doc.tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)), name)
            self.assertEqual(1, sum(t=='h1' for t,_ in doc.tags), name)
            for payload in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', source, re.S):
                json.loads(payload)
            for tag,attrs in doc.tags:
                if tag == 'img': self.assertIn('alt', attrs)
                for attr in ['href','src']:
                    if attr not in attrs: continue
                    url = urlsplit(attrs[attr])
                    if url.scheme or url.netloc: continue
                    target = ROOT / unquote(url.path) if url.path else ROOT / name
                    if target.is_dir(): target /= 'index.html'
                    self.assertTrue(target.is_file(), name + ': ' + attrs[attr])
                    if url.fragment and target.suffix=='.html':
                        self.assertIn(unquote(url.fragment), [a.get('id') for _,a in Document(target.read_text(encoding='utf-8')).tags])
                    count += 1
        print(f'Development: {count} local links/assets and fragments checked; no external submissions.')

if __name__ == '__main__': unittest.main(verbosity=2)
