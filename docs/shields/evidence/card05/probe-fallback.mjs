// Developer probe restricted to the task-owned local Card05 fixture.
const fixture = 'http://127.0.0.1:8766/card05.html';
const endpoint = 'http://127.0.0.1:9223';
const resource = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?roadium_fixture=5';
const action = process.argv[2] ?? 'state';
if (!['state', 'reload', 'advertising'].includes(action)) throw new Error('Unsupported fixture action');
const response = await fetch(endpoint + '/json/list', {redirect:'error', signal:AbortSignal.timeout(10000)});
const targets = (await response.json()).filter(t => t.type === 'page' && t.url === fixture);
if (!targets.length) throw new Error('Controlled fixture is not open');
for (const duplicate of targets.slice(1)) {
  if (!/^[A-Fa-f0-9]+$/.test(duplicate.id)) throw new Error('Unexpected duplicate ID');
  await fetch(endpoint + '/json/close/' + duplicate.id, {redirect:'error'});
}
const target = targets[0];
const address = new URL(target.webSocketDebuggerUrl);
if (address.protocol !== 'ws:' || !['localhost','127.0.0.1'].includes(address.hostname)
    || address.port !== '9223' || address.username || address.password || address.search || address.hash
    || address.pathname !== `/devtools/page/${target.id}`) throw new Error('Unexpected fixture socket');
address.hostname = '127.0.0.1';
const socket = new WebSocket(address);
const pending = new Map();
const requests = new Set();
const failures = [];
let sequence = 0;
function call(method, params = {}) {
  return new Promise((resolve,reject) => {
    const id = ++sequence;
    const timeout = setTimeout(() => { pending.delete(id); reject(new Error('Fixture call timed out')); },15000);
    pending.set(id,{resolve,reject,timeout});
    socket.send(JSON.stringify({id,method,params}));
  });
}
socket.addEventListener('message', event => {
  const data = JSON.parse(event.data);
  if (data.id && pending.has(data.id)) {
    const item = pending.get(data.id); pending.delete(data.id); clearTimeout(item.timeout);
    data.error ? item.reject(new Error(data.error.message)) : item.resolve(data.result);
  }
  if (data.method === 'Network.requestWillBeSent' && data.params.request.url === resource)
    requests.add(data.params.requestId);
  if (data.method === 'Network.loadingFailed' && requests.has(data.params.requestId))
    failures.push({errorText:data.params.errorText,blockedReason:data.params.blockedReason ?? null});
});
async function evaluate(expression) {
  const result = await call('Runtime.evaluate', {
    expression:`(async()=>{if(location.href!==${JSON.stringify(fixture)})throw new Error('Fixture navigated');${expression}})()`,
    awaitPromise:true,returnByValue:true,userGesture:true
  });
  if (result.exceptionDetails) throw new Error('Controlled page evaluation failed');
  return result.result.value;
}
try {
  await new Promise((resolve,reject) => {
    socket.addEventListener('open',resolve,{once:true});
    socket.addEventListener('error',() => reject(new Error('Fixture socket failed')),{once:true});
  });
  await call('Network.enable');
  if (action === 'reload') {
    await call('Page.enable');
    await call('Page.reload',{ignoreCache:true});
    await new Promise(resolve => setTimeout(resolve,750));
  }
  const state = await evaluate('return window.card05Snapshot();');
  const advertising = action === 'advertising'
    ? await evaluate('return await window.card05AdvertisingProbe();') : undefined;
  console.log(JSON.stringify({fixture,action,state,advertising,advertisingFailures:failures},null,2));
} finally {
  socket.close();
}
