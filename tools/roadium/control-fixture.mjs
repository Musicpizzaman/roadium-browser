#!/usr/bin/env node
// Developer instrumentation for the local Roadium fixture on an Android emulator.
const fixture = 'http://127.0.0.1:8765/';
const endpoint = 'http://127.0.0.1:9222';
const buttons = new Map([
  ['audio', 'btn-audio'], ['video', 'btn-video'], ['web', 'btn-web'],
  ['speech', 'btn-speak'], ['cancel', 'btn-cancel'], ['retry', 'btn-retry'],
]);
const action = process.argv[2];
if (process.argv.length !== 3 || (!buttons.has(action) && !['status', 'stop'].includes(action))) {
  console.error('Usage: node control-fixture.mjs status|audio|video|web|speech|cancel|retry|stop');
  process.exit(2);
}
const deadline = Date.now() + 10000;
let socket;
try {
  const response = await fetch(`${endpoint}/json/list`, {
    redirect: 'error', signal: AbortSignal.timeout(10000),
  });
  if (!response.ok) throw new Error('DevTools target listing failed');
  const targets = await response.json();
  if (!Array.isArray(targets)) throw new Error('Invalid DevTools target list');
  const pages = targets.filter(target => target.type === 'page' && target.url === fixture);
  if (pages.length !== 1) throw new Error('Exactly one local fixture page is required');
  const target = pages[0];
  const url = new URL(target.webSocketDebuggerUrl);
  if (url.protocol !== 'ws:' || !['127.0.0.1', 'localhost'].includes(url.hostname)
      || url.port !== '9222' || url.username || url.password || url.search || url.hash
      || !/^[A-Za-z0-9_-]+$/.test(target.id)
      || url.pathname !== `/devtools/page/${target.id}`) {
    throw new Error('Unexpected DevTools socket address');
  }
  url.hostname = '127.0.0.1';
  const change = buttons.has(action)
    ? `document.getElementById('${buttons.get(action)}').click();`
    : action === 'stop'
      ? `if (retryInterval) document.getElementById('btn-retry').click();
         a.pause(); v.pause(); if (ctx) await ctx.suspend(); if (speech) speech.cancel();`
      : '';
  const expression = `(async () => {
    if (location.href !== '${fixture}') throw new Error('Fixture page changed');
    ${change}
    return {
      url: location.href, visibility: document.visibilityState,
      audio: {paused: a.paused, currentTime: a.currentTime, muted: a.muted},
      video: {paused: v.paused, currentTime: v.currentTime, muted: v.muted},
      webAudio: ctx ? ctx.state : 'inactive', retry: Boolean(retryInterval),
      speech: speech ? {speaking: speech.speaking, pending: speech.pending,
        paused: speech.paused, voices: speech.getVoices().length} : null
    };
  })()`;
  const value = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('DevTools command timed out')),
                             Math.max(1, deadline - Date.now()));
    const finish = (error, result) => {
      clearTimeout(timer);
      error ? reject(error) : resolve(result);
    };
    socket = new WebSocket(url);
    socket.addEventListener('open', () => socket.send(JSON.stringify({
      id: 1, method: 'Runtime.evaluate', params: {
        expression, userGesture: true, returnByValue: true, awaitPromise: true,
      },
    })), {once: true});
    socket.addEventListener('error', () => finish(new Error('DevTools socket failed')), {once: true});
    socket.addEventListener('close', () => finish(new Error('DevTools socket closed')), {once: true});
    socket.addEventListener('message', event => {
      let reply;
      try { reply = JSON.parse(event.data); }
      catch { finish(new Error('Invalid DevTools reply')); return; }
      if (reply.id !== 1) return;
      if (reply.error || reply.result?.exceptionDetails) {
        finish(new Error('Fixture evaluation failed'));
      } else if (reply.result?.result?.type !== 'object' || !reply.result.result.value) {
        finish(new Error('Missing fixture state'));
      } else {
        finish(null, reply.result.result.value);
      }
    });
  });
  console.log(JSON.stringify(value));
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
} finally {
  if (socket) socket.close();
}
