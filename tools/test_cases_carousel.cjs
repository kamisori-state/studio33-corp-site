/* No dependencies: exercise the actual script with a minimal DOM/scroll adapter.
   This is a runtime unit test, not a substitute for browser/touch rendering. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../cases-carousel.js'), 'utf8');
function fixture(visible, reduced = true) {
  const handlers = {};
  const button = () => ({attrs: {}, setAttribute(k,v) {this.attrs[k]=v;}, addEventListener(k,f) {this[k]=f;}});
  const prev = button(), next = button(), status = {textContent: ''};
  const controls = {hidden: true, querySelector(s) {return s.includes('prev') ? prev : s.includes('next') ? next : status;}};
  const track = {clientWidth: visible * 300 + (visible - 1) * 22, scrollWidth: 6 * 300 + 5 * 22,
    scrollLeft: 0, children: Array.from({length:6}, () => ({getBoundingClientRect: () => ({width:300})})),
    addEventListener(k,f) {handlers[k]=f;}, scrollTo(o) {this.last=o; this.scrollLeft=o.left; handlers.scroll();}};
  const carousel = {querySelector: s => s.includes('track') ? track : controls};
  let resize;
  vm.runInNewContext(code, {document: {querySelectorAll: () => [carousel]}, window: {matchMedia: () => ({matches:reduced}), ResizeObserver: true},
    ResizeObserver: class {constructor(f) {resize=f;} observe() {}}, getComputedStyle: () => ({columnGap:'22px'}),
    setTimeout: f => {f(); return 1;}, clearTimeout() {}});
  const key = k => handlers.keydown({target: track, key:k, preventDefault() {}});
  return {track, prev, next, status, controls, key, resize, nativeScroll: () => handlers.scroll()};
}
for (const visible of [1,2,3]) {
  const f=fixture(visible);
  assert.equal(f.controls.hidden,false);
  assert.match(f.status.textContent, /^1 \/ /);
  assert.equal(f.prev.attrs['aria-disabled'],'true');
  f.prev.click(); assert.equal(f.track.scrollLeft,0);
  f.key('End'); assert.equal(f.track.scrollLeft, f.track.scrollWidth-f.track.clientWidth);
  assert.equal(f.next.attrs['aria-disabled'],'true');
  const end=f.track.scrollLeft; f.next.click(); assert.equal(f.track.scrollLeft,end);
  f.key('Home'); assert.equal(f.track.scrollLeft,0);
  f.key('ArrowRight'); assert.ok(f.track.scrollLeft>0);
  f.key('ArrowLeft'); assert.equal(f.track.scrollLeft,0);
  f.next.click(); assert.ok(f.track.scrollLeft>0);
  assert.equal(f.track.last.behavior,'instant');
  f.track.clientWidth=300; f.resize(); assert.match(f.status.textContent,/\/ 6 ページ/);
  // Native swipe/scroll feeds the same state, without preventing touch events.
  f.track.scrollLeft=f.track.scrollWidth-f.track.clientWidth; f.nativeScroll();
  assert.equal(f.next.attrs['aria-disabled'],'true');
}
const normal=fixture(1,false); normal.next.click(); assert.equal(normal.track.last.behavior,'smooth');
console.log('PASS: 1/2/3-card pages; initial/latest, buttons, arrows, Home/End, boundaries, resize, native scroll state, reduced motion.');
