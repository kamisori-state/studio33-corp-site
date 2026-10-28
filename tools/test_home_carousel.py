"""Homepage discovery and generated carousel regression checks (no network)."""
from test_smartphone_support import Document, ROOT
import html
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def text(name):
    return (ROOT / name).read_text(encoding='utf-8')


def case_content(source):
    block = re.search(r'<!-- CASES -->(.*?)<!-- /CASES -->', source, re.S).group(1)
    return [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', card)).strip()
            for card in re.findall(r'<article\b[^>]*>(.*?)</article>', block, re.S)]


class HomeCarouselChecks(unittest.TestCase):
    def test_image_and_navigation(self):
        source = text('index.html')
        card = source.split('<article id="development"', 1)[1].split('</article>', 1)[0]
        self.assertIn('src="img/development-hero.webp"', card)
        self.assertIn('AI生成', card)
        self.assertIn('href="development.html"', source.split('<nav')[1].split('</nav>')[0])
        self.assertIn('設計・開発は有料・個別見積もり', card)
        image_css = re.search(r'\.development-service-card > img\s*\{([^}]+)\}', text('style.css')).group(1)
        self.assertIn('height: auto', image_css)
        self.assertIn('aspect-ratio: 16 / 9', image_css)

    def test_generated_structure_and_latest_data(self):
        spec = importlib.util.spec_from_file_location('cases_builder', ROOT / 'tools/build-cases.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        cases = sorted(builder.load_cases(), key=lambda c: (c['date'], c['id']), reverse=True)[:6]
        block = builder.render(cases)
        self.assertIn('class="cases-carousel-track"', block)
        self.assertIn('id="cases-heading"', block)
        self.assertIn('aria-controls="cases-track"', block)
        self.assertIn('aria-live="polite"', block)
        self.assertIn('data-cases-prev', block)
        self.assertIn('data-cases-next', block)
        self.assertIn('hidden', block)
        self.assertEqual(6, block.count('<article '))
        positions = []
        for c in cases:
            for key in ['title', 'trouble', 'support', 'price', 'category']:
                self.assertIn(html.escape(c[key], quote=True), block)
            positions.append(block.index(html.escape(c['title'], quote=True)))
        self.assertEqual(sorted(positions), positions)
        current = re.search(r'<!-- CASES -->\n(.*?)\n<!-- /CASES -->', text('index.html'), re.S).group(1)
        self.assertEqual(block, current)

    def test_progressive_interaction_contract(self):
        self.assertIn('cases-carousel.js', text('index.html'))
        css = text('style.css')
        for token in ['.cases-carousel-track', 'overflow-x: auto', 'scroll-snap-type', 'prefers-reduced-motion']:
            self.assertIn(token, css)
        script = text('cases-carousel.js')
        for token in ['ArrowLeft', 'ArrowRight', 'Home', 'End', 'ResizeObserver', 'scroll', 'prefers-reduced-motion']:
            self.assertIn(token, script)
        self.assertNotIn('setInterval', script)
        self.assertNotIn('.focus(', script)

    def test_regeneration_and_source_integrity(self):
        original = (ROOT / 'cases/cases.yml').read_bytes()
        with tempfile.TemporaryDirectory(prefix='studio33-carousel-') as temp:
            site = Path(temp) / 'site'
            shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', '__pycache__', 'sns-img'))
            for script in ['build-cases.py', 'build-blog.py', 'build-cases.py']:
                result = subprocess.run([sys.executable, '-X', 'utf8', str(site / 'tools' / script)], capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            source = (site / 'index.html').read_text(encoding='utf-8')
            self.assertIn('class="cases-carousel-track"', source)
            self.assertEqual(case_content(text('index.html')), case_content(source))
            self.assertEqual(original, (site / 'cases/cases.yml').read_bytes())
        self.assertEqual(original, (ROOT / 'cases/cases.yml').read_bytes())

    @unittest.skipUnless(os.environ.get('STUDIO33_REVIEW_BASELINE'), 'Opt-in delivery baseline')
    def test_delivery_baseline(self):
        base = os.environ['STUDIO33_REVIEW_BASELINE']
        old = subprocess.check_output(['git', 'show', base + ':index.html'], cwd=ROOT).decode('utf-8')
        self.assertEqual(case_content(old), case_content(text('index.html')))
        for name in ['cases/cases.yml', 'development.html', 'pricing.html', 'contact-service.js']:
            self.assertEqual(subprocess.check_output(['git', 'show', base + ':' + name], cwd=ROOT).decode('utf-8'), text(name))


if __name__ == '__main__':
    unittest.main(verbosity=2)
