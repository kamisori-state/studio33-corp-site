/* Progressive enhancement: touch/swipe uses the browser's native horizontal scroll. */
(() => {
  'use strict';
  document.querySelectorAll('.cases-carousel').forEach((carousel) => {
    const track = carousel.querySelector('.cases-carousel-track');
    const cards = Array.from(track.children);
    const controls = carousel.querySelector('.cases-carousel-controls');
    const previous = controls.querySelector('[data-cases-prev]');
    const next = controls.querySelector('[data-cases-next]');
    const status = controls.querySelector('.cases-carousel-status');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let stops = [];
    let page = 0;
    let timer;
    const position = () => Math.max(0, track.scrollLeft);
    const nearest = () => stops.reduce((best, left, i) =>
      Math.abs(left - position()) < Math.abs(stops[best] - position()) ? i : best, 0);
    function announce() {
      page = nearest();
      previous.setAttribute('aria-disabled', String(page === 0));
      next.setAttribute('aria-disabled', String(page === stops.length - 1));
      const label = `${page + 1} / ${stops.length} ページ（全${cards.length}件）`;
      if (status.textContent !== label) status.textContent = label;
    }
    function measure() {
      const max = Math.max(0, track.scrollWidth - track.clientWidth);
      const width = cards[0].getBoundingClientRect().width;
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      const visible = Math.max(1, Math.round((track.clientWidth + gap) / (width + gap)));
      stops = [];
      for (let i = 0; i < cards.length; i += visible) {
        const left = Math.min(max, i * (width + gap));
        if (!stops.length || left > stops[stops.length - 1] + 1) stops.push(left);
      }
      if (max > stops[stops.length - 1] + 1) stops.push(max);
      announce();
    }
    function go(target) {
      const index = Math.max(0, Math.min(stops.length - 1, target));
      // Retain focus on the initiating control; edge buttons stay focusable.
      page = index;
      track.scrollTo({left: stops[index], behavior: reducedMotion.matches ? 'instant' : 'smooth'});
    }
    previous.addEventListener('click', () => go(page - 1));
    next.addEventListener('click', () => go(page + 1));
    track.addEventListener('keydown', (event) => {
      if (event.target !== track || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      const targets = {ArrowLeft: page - 1, ArrowRight: page + 1, Home: 0, End: stops.length - 1};
      if (!(event.key in targets)) return;
      event.preventDefault();
      go(targets[event.key]);
    });
    track.addEventListener('scroll', () => {
      clearTimeout(timer);
      timer = setTimeout(announce, 140);
    }, {passive: true});
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe(track);
    else window.addEventListener('resize', measure);
    measure();
    controls.hidden = false;
  });
})();
