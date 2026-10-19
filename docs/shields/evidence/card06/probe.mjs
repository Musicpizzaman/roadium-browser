// Own lab browser only. No scriptlet injection; observe normal loaded documents.
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
const processes=execFileSync('E:/Android Auto Projects/AndroidSdk/platform-tools/adb.exe',['-s','emulator-5554','shell','ps','-A','-o','USER,PID,NAME'],{encoding:'utf8'}).split('\n').map(s=>s.trim().split(/\s+/)).filter(a=>a.at(-1)==='io.github.musicpizzaman.roadium');
const labUser=process.env.ROADIUM_LAB_USER??'11';
if(!['11','13'].includes(labUser)||processes.length!==1||processes[0][0]!==`u${labUser}_a204`)throw Error('Expected only owned lab browser main process');
const action=process.argv[2]??'state';
const allowed=new Set(['state','reload','trigger','ordinary','webaudio','audio','loop','live-desktop','live-mobile','live-embed','live-shorts','live-captions','live-controls','fullscreen']);
allowed.add('tab-away');allowed.add('tab-back');
if(!allowed.has(action))throw Error('Unknown probe action');
const fixture='http://127.0.0.1:8766/card06.html';
const pageAllowed=u=>u===fixture||u==='http://127.0.0.1:8766/embed.html'||/^https:\/\/(www|m)\.youtube\.com\/(watch\?v=aqz-KE-bpKQ|shorts\/[A-Za-z0-9_-]+|embed\/aqz-KE-bpKQ)/.test(u);
let targets;
for(let attempt=0;attempt<20;attempt++){try{targets=await(await fetch('http://127.0.0.1:9223/json/list',{signal:AbortSignal.timeout(2000)})).json();break}catch(e){if(attempt===19)throw e;await new Promise(r=>setTimeout(r,500))}}
const saved=fs.existsSync('probe-target.txt')?fs.readFileSync('probe-target.txt','utf8').trim():null;
const localAction=['state','reload','trigger','ordinary','webaudio','audio','loop'].includes(action);
const target=(localAction?targets.find(t=>t.type==='page'&&t.url===fixture):null)||targets.find(t=>t.type==='page'&&t.id===saved)||targets.find(t=>t.type==='page'&&pageAllowed(t.url));
if(!target)throw Error('No owned test target');
fs.writeFileSync('probe-target.txt',target.id);
const url=new URL(target.webSocketDebuggerUrl);
if(!['localhost','127.0.0.1'].includes(url.hostname)||url.port!=='9223'||url.pathname!==`/devtools/page/${target.id}`)throw Error('Unexpected socket');
url.hostname='127.0.0.1';
const ws=new WebSocket(url);let id=0;const pending=new Map(),events=[];
ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(m.error.message)):p.resolve(m.result)}if(m.method==='Runtime.exceptionThrown')events.push({method:m.method,text:m.params.exceptionDetails.text});});
const call=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;const timer=setTimeout(()=>{pending.delete(n);reject(Error('CDP timeout '+method))},20000);pending.set(n,{resolve,reject,timer});ws.send(JSON.stringify({id:n,method,params}))});
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function evaluate(expression){const result=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true,userGesture:true});if(result.exceptionDetails)return {exception:result.exceptionDetails.text,description:result.exceptionDetails.exception?.description};return result.result.value;}
try{
await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true})});await call('Page.enable');await call('Runtime.enable');
let operation;
if(action==='tab-away'){operation=await call('Target.createTarget',{url:'about:blank'});await call('Target.activateTarget',{targetId:operation.targetId});await pause(750)}
if(action==='tab-back'){await call('Page.bringToFront');await pause(500);operation={activated:target.id}}
if(action==='reload'){await call('Page.reload',{ignoreCache:true});await pause(1200)}
if(action==='trigger'){operation=await evaluate('window.card06Trigger();true');await pause(1000)}
if(action==='ordinary')operation=await evaluate('window.card06Ordinary()');
if(action==='webaudio')operation=await evaluate('window.card06WebAudio()');
if(action==='audio')operation=await evaluate("(async()=>{const a=document.getElementById('audio');const before=a.currentTime;let play=await Promise.race([a.play().then(()=>true,e=>e.name),new Promise(r=>setTimeout(()=>r('timeout'),3000))]);await new Promise(r=>setTimeout(r,400));const after=a.currentTime;a.pause();return {before,after,advanced:after>before,paused:a.paused,duration:a.duration,error:a.error?.code??null,play};})()");
if(action==='loop')operation=await evaluate("(async()=>{const v=document.getElementById('ordinary');v.loop=true;await v.play();return {paused:v.paused};})()");
if(action.startsWith('live-')&&action!=='live-controls'){
 let destination=action==='live-mobile'?'https://m.youtube.com/watch?v=aqz-KE-bpKQ':action==='live-embed'?'http://127.0.0.1:8766/embed.html':'https://www.youtube.com/watch?v=aqz-KE-bpKQ';
 if(action==='live-captions')destination='https://www.youtube.com/watch?v=M7lc1UVf-VE';
 if(['live-desktop','live-captions'].includes(action))await call('Emulation.setUserAgentOverride',{userAgent:'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36'});
 if(action==='live-mobile')await call('Emulation.setUserAgentOverride',{userAgent:'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Mobile Safari/537.36'});
 if(action==='live-shorts'){
 const link=await evaluate('document.querySelector(\'a[href^="/shorts/"]\')?.href??null');
 if(typeof link==='string'&&/^https:\/\/(www|m)\.youtube\.com\/shorts\/[A-Za-z0-9_-]+$/.test(link))destination=link;
 else destination='https://www.youtube.com/shorts';
 }
 if(!operation){await call('Page.navigate',{url:destination});await pause(12000)}
}
if(action==='live-controls')operation=await evaluate(`(async()=>{const v=document.querySelector('video');if(!v)return {video:false};const before={time:v.currentTime,paused:v.paused};try{await v.play()}catch(e){return {before,error:e.name}}await new Promise(r=>setTimeout(r,1500));const after=v.currentTime;v.pause();const paused=v.paused;if(v.duration>10)v.currentTime=Math.min(10,v.duration/2);return {before,after,advanced:after>before.time,paused,seek:v.currentTime,captionControl:!!document.querySelector('.ytp-subtitles-button'),qualityControl:!!document.querySelector('.ytp-settings-button')};})()`);
if(action==='fullscreen')operation=await evaluate(`(async()=>{try{await(document.querySelector('video')??document.documentElement).requestFullscreen();const entered=!!document.fullscreenElement;if(entered)await document.exitFullscreen();return {entered}}catch(e){return {error:e.name}}})()`);
const state=await evaluate(`(async()=>{if(location.href===${JSON.stringify(fixture)})return window.card06State();return {url:location.href,title:document.title,ready:document.readyState,ua:navigator.userAgent,videos:[...document.querySelectorAll('video')].map(v=>({time:v.currentTime,duration:Number.isFinite(v.duration)?v.duration:null,paused:v.paused,ready:v.readyState,error:v.error?.code??null})),adShowing:!!document.querySelector('.ad-showing,.ad-interrupting'),errorText:document.querySelector('.ytp-error-content-wrap-reason,.player-error-message-renderer')?.textContent?.slice(0,300)??null,consent:!!document.querySelector('form[action*="consent"]'),frames:[...document.querySelectorAll('iframe')].map(f=>({src:f.src,title:f.title}))};})()`);
console.log(JSON.stringify({action,target:target.id,time:new Date().toISOString(),state,operation,exceptions:events},null,2));
}finally{ws.close()}
