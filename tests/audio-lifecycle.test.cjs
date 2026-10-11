const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const html = readFileSync(join(__dirname, '../app/src/main/assets/index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function setup({ hidden = false, native = false } = {}) {
  const events = {};
  const timers = new Map();
  const contexts = [];
  let nativeHidden = native;
  let nextId = 0;
  const listen = (name, fn) => { events[name] = fn; };
  class AudioContext {
    constructor() {
      this.state = 'running';
      this.currentTime = 0;
      this.notes = 0;
      this.resumes = 0;
      this.closes = 0;
      contexts.push(this);
    }
    resume() { this.resumes++; this.state = 'running'; return Promise.resolve(); }
    close() { this.closes++; this.state = 'closed'; return Promise.resolve(); }
    createOscillator() {
      this.notes++;
      return {
        frequency: { setValueAtTime() {}, exponentialRampToValueAtTime() {} },
        connect() { return { connect() {} }; }, start() {}, stop() {}
      };
    }
    createGain() {
      return {
        gain: { setValueAtTime() {}, exponentialRampToValueAtTime() {} }
      };
    }
  }
  const window = {
    AudioContext, addEventListener: listen,
    AndroidBridge: { isAppInBackground: () => nativeHidden }
  };
  const document = { hidden, addEventListener: listen };
  const context = vm.createContext({
    window, document, performance: { now: () => 100 },
    setInterval(fn) { const id = ++nextId; timers.set(id, fn); return id; },
    clearInterval(id) { timers.delete(id); }
  });
  // Execute the production lifecycle state and audio functions, with mocked WebAudio.
  const lifecycle = script.slice(script.indexOf('  let audioCtx = null;'),
    script.indexOf('  let boostTrailTimer'));
  const audio = script.slice(script.indexOf('  function playTone('),
    script.indexOf('  function awardHit('));
  vm.runInContext('let lastTime = 0;\n' + lifecycle + '\n' + audio, context);
  return {
    context, contexts, timers, document, events, window,
    run: code => vm.runInContext(code, context),
    setNative: value => { nativeHidden = value; }
  };
}

test('the entire game script parses', () => {
  new vm.Script(script);
});

test('hiding closes audio and clears the BGM timer; late effects cannot restart it', () => {
  const h = setup();
  h.run('startMischiefBgm()');
  const tick = [...h.timers.values()][0];
  tick();
  const old = h.contexts[0];
  assert.ok(old.notes > 0);
  h.document.hidden = true;
  h.events.visibilitychange();
  assert.equal(old.state, 'closed');
  assert.equal(h.timers.size, 0);
  const notes = old.notes;
  tick();
  h.run('playTone(440); playBoing(); playShatterSound(); startMischiefBgm()');
  assert.equal(old.notes, notes);
  assert.equal(h.contexts.length, 1);
  assert.equal(h.timers.size, 0);
});

test('foreground return starts one fresh context and one BGM timer', () => {
  const h = setup();
  h.run('startMischiefBgm()');
  h.document.hidden = true;
  h.events.visibilitychange();
  h.events.pagehide();
  h.document.hidden = false;
  h.events.visibilitychange();
  assert.equal(h.timers.size, 0); // pagehide remains in effect
  h.events.pageshow();
  h.events.pageshow();
  h.events.visibilitychange();
  assert.equal(h.contexts.length, 2);
  assert.equal(h.timers.size, 1);
});

test('native pause blocks late timer callbacks before the lifecycle JS arrives', () => {
  const h = setup();
  h.run('startMischiefBgm()');
  const tick = [...h.timers.values()][0];
  h.setNative(true);
  tick();
  h.run('ensureAudio(); playTone(440)');
  assert.equal(h.contexts[0].notes, 0);
  h.window.PotBreakerLifecycle.setNativeBackground(true);
  assert.equal(h.contexts[0].closes, 1);
  assert.equal(h.timers.size, 0);
  h.setNative(false);
  h.window.PotBreakerLifecycle.setNativeBackground(false);
  assert.equal(h.timers.size, 1);
});

test('hidden initial load and page restoration do not start previously inactive BGM', () => {
  const h = setup({ hidden: true });
  h.run('ensureAudio(); startMischiefBgm()');
  h.events.visibilitychange();
  assert.equal(h.contexts.length, 0);
  h.document.hidden = false;
  h.events.visibilitychange();
  assert.equal(h.timers.size, 0);
});

test('web works without the Android bridge and retries a suspended context on input', () => {
  const h = setup();
  delete h.window.AndroidBridge;
  h.run('startMischiefBgm()');
  h.events.pagehide();
  h.events.pageshow();
  h.contexts[1].state = 'suspended';
  h.run('ensureAudio(); startMischiefBgm()');
  assert.equal(h.contexts[1].resumes, 1);
  assert.equal(h.timers.size, 1);
});
