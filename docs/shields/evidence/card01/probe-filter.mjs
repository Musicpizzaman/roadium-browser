// Developer-only probe; operates solely on the exact local Shields fixture.
const fixture='http://127.0.0.1:8765/shields.html';
const endpoint='http://127.0.0.1:9222';
const resource='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?roadium_fixture=1';
const response=await fetch(endpoint+'/json/list',{redirect:'error',signal:AbortSignal.timeout(10000)});
if(!response.ok)throw new Error('Cannot list fixture target');
const targets=await response.json();
const pages=targets.filter(x=>x.type==='page'&&x.url===fixture);
if(pages.length!==1)throw new Error('Exactly one controlled fixture must be open');
const target=pages[0];
const address=new URL(target.webSocketDebuggerUrl);
if(address.protocol!=='ws:'||!['localhost','127.0.0.1'].includes(address.hostname)
    ||address.port!=='9222'||address.username||address.password||address.search||address.hash
    ||address.pathname!==`/devtools/page/${target.id}`)throw new Error('Unexpected socket');
address.hostname='127.0.0.1';
const socket=new WebSocket(address);
const pending=new Map();
const events=[];
const ids=new Set();
let seq=0;
function call(method,params={}) {
  const id=++seq;
  return new Promise((resolve,reject)=>{
    const timeout=setTimeout(()=>{pending.delete(id);reject(new Error('Fixture command timed out'));},15000);
    pending.set(id,{resolve,reject,timeout});
    socket.send(JSON.stringify({id,method,params}));
  });
}
socket.addEventListener('message',event=>{
  const data=JSON.parse(event.data);
  if(data.id&&pending.has(data.id)) {
    const p=pending.get(data.id);pending.delete(data.id);clearTimeout(p.timeout);
    if(data.error)p.reject(new Error(data.error.message));else p.resolve(data.result);
  }
  if(data.method==='Network.requestWillBeSent'&&data.params.request.url===resource)ids.add(data.params.requestId);
  if(data.method==='Network.loadingFailed'&&ids.has(data.params.requestId))
    events.push({errorText:data.params.errorText,blockedReason:data.params.blockedReason??null,type:data.params.type});
});
try {
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',()=>reject(new Error('Socket failed')),{once:true});});
  await call('Network.enable');
  const value=await call('Runtime.evaluate',{expression:`(async()=>{if(location.href!==${JSON.stringify(fixture)})throw new Error('Not fixture');return await window.shieldsProbe();})()`,returnByValue:true,awaitPromise:true,userGesture:true});
  if(value.exceptionDetails)throw new Error('Fixture evaluation failed');
  console.log(JSON.stringify({fixture,result:value.result.value,advertisingResourceFailures:events},null,2));
} finally {socket.close();}
