#!/usr/bin/env node
// Local developer probe for real renderer theme preferences and painted content.
import {writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';

const args = process.argv.slice(2);
const command = args[0];
if (!['status', 'reload', 'capture'].includes(command)
    || args.length !== (command === 'capture' ? 2 : 1)) {
  console.error('Usage: node theme-fixture.mjs status|reload|capture [new-output.png]');
  process.exit(2);
}
const endpoint = 'http://127.0.0.1:9222';
const allowed = new Set(['http://127.0.0.1:8765/theme-native.html',
                         'http://127.0.0.1:8765/theme-light.html']);
const deadline = Date.now() + 15000;
const pending = new Map();
let socket, nextId = 1, opening, loaded;
function fail(error) {
  if (opening) { clearTimeout(opening.timer); opening.reject(error); opening = null; }
  if (loaded) { clearTimeout(loaded.timer); loaded.reject(error); loaded = null; }
  for (const request of pending.values()) {
    clearTimeout(request.timer); request.reject(error);
  }
  pending.clear();
}
function request(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    const timer = setTimeout(() => {
      pending.delete(id); reject(new Error(`${method} timed out`));
    }, Math.max(1, deadline - Date.now()));
    pending.set(id, {resolve, reject, timer});
    try { socket.send(JSON.stringify({id, method, params})); }
    catch (error) { clearTimeout(timer); pending.delete(id); reject(error); }
  });
}
try {
  const response = await fetch(`${endpoint}/json/list`, {
    redirect: 'error', signal: AbortSignal.timeout(10000),
  });
  if (!response.ok) throw new Error('DevTools target listing failed');
  const targets = await response.json();
  if (!Array.isArray(targets)) throw new Error('Invalid DevTools target list');
  const pages = targets.filter(target => target.type === 'page' && allowed.has(target.url));
  if (pages.length !== 1) throw new Error('Exactly one local theme fixture page is required');
  const target = pages[0];
  const url = new URL(target.webSocketDebuggerUrl);
  if (url.protocol !== 'ws:' || !['127.0.0.1', 'localhost'].includes(url.hostname)
      || url.port !== '9222' || url.username || url.password || url.search || url.hash
      || !/^[A-Za-z0-9_-]+$/.test(target.id)
      || url.pathname !== `/devtools/page/${target.id}`) {
    throw new Error('Unexpected DevTools socket address');
  }
  url.hostname = '127.0.0.1';
  socket = new WebSocket(url);
  const ready = new Promise((resolve, reject) => {
    opening = {resolve, reject, timer: setTimeout(() => fail(new Error('Socket open timed out')),
                                                Math.max(1, deadline - Date.now()))};
  });
  socket.addEventListener('open', () => {
    if (!opening) return;
    clearTimeout(opening.timer); opening.resolve(); opening = null;
  }, {once: true});
  socket.addEventListener('error', () => fail(new Error('DevTools socket failed')));
  socket.addEventListener('close', () => fail(new Error('DevTools socket closed')));
  socket.addEventListener('message', event => {
    let reply;
    try { reply = JSON.parse(event.data); }
    catch { fail(new Error('Invalid DevTools reply')); return; }
    if (reply.method === 'Page.loadEventFired' && loaded) {
      clearTimeout(loaded.timer); loaded.resolve(); loaded = null;
    }
    const waiting = pending.get(reply.id);
    if (!waiting) return;
    pending.delete(reply.id); clearTimeout(waiting.timer);
    if (reply.error) waiting.reject(new Error(`${reply.error.message || 'DevTools command failed'}`));
    else waiting.resolve(reply.result);
  });
  await ready;
  async function status() {
    const result = await request('Runtime.evaluate', {
      expression: `({url:location.href, dark:matchMedia('(prefers-color-scheme: dark)').matches,
        light:matchMedia('(prefers-color-scheme: light)').matches,
        authoredBackground:getComputedStyle(document.body).backgroundColor,
        visibility:document.visibilityState})`,
      returnByValue: true,
    });
    const value = result?.result?.value;
    if (result?.exceptionDetails || !value || value.url !== target.url) {
      throw new Error('Theme fixture changed or evaluation failed');
    }
    return value;
  }
  let value = await status();
  if (command === 'reload') {
    await request('Page.enable');
    const load = new Promise((resolve, reject) => {
      loaded = {resolve, reject, timer: setTimeout(() => {
        loaded = null; reject(new Error('Fixture reload timed out'));
      }, Math.max(1, deadline - Date.now()))};
    });
    // Attach a rejection handler before issuing the reload request.
    const reload = Promise.all([request('Page.reload', {ignoreCache: true}), load]);
    await reload;
    value = await status();
  } else if (command === 'capture') {
    const result = await request('Page.captureScreenshot', {
      format: 'png', fromSurface: true, captureBeyondViewport: false,
    });
    value = await status();
    if (typeof result?.data !== 'string') throw new Error('Missing painted screenshot');
    const png = Buffer.from(result.data, 'base64');
    if (!png.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) {
      throw new Error('Invalid PNG screenshot');
    }
    const output = resolve(args[1]);
    if (!output.toLowerCase().endsWith('.png')) throw new Error('Screenshot output must be PNG');
    await writeFile(output, png, {flag: 'wx'});
    value.output = output;
  }
  console.log(JSON.stringify(value));
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
} finally {
  fail(new Error('Probe finished'));
  if (socket) socket.close();
}
