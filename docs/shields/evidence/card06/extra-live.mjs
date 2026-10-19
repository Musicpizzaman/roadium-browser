// Observe only the task-owned iframe/public YouTube player.
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
const rows=execFileSync('E:/Android Auto Projects/AndroidSdk/platform-tools/adb.exe',['-s','emulator-5554','shell','ps','-A','-o','USER,PID,NAME'],{encoding:'utf8'}).split('\n').map(s=>s.trim().split(/\s+/)).filter(a=>a.at(-1)==='io.github.musicpizzaman.roadium');
const labUser=process.env.ROADIUM_LAB_USER??'11';
if(!['11','13'].includes(labUser)||rows.length!==1||rows[0][0]!==`u${labUser}_a204`)throw Error('Own browser guard');
const targets=await(await fetch('http://127.0.0.1:9223/json/list')).json();const saved=fs.readFileSync('probe-target.txt','utf8').trim();const target=targets.find(t=>t.type==='page'&&t.id===saved);if(!target)throw Error('Own target missing');
const u=new URL(target.webSocketDebuggerUrl);if(u.port!=='9223'||!['localhost','127.0.0.1'].includes(u.hostname))throw Error('Socket guard');u.hostname='127.0.0.1';const ws=new WebSocket(u);let sequence=0;const pending=new Map();
ws.addEventListener('message',e=>{const d=JSON.parse(e.data),p=pending.get(d.id);if(p){pending.delete(d.id);clearTimeout(p.timer);d.error?p.reject(Error(d.error.message)):p.resolve(d.result)}});
function call(method,params={},sessionId){return new Promise((resolve,reject)=>{const id=++sequence,timer=setTimeout(()=>{pending.delete(id);reject(Error(method+' timeout'))},15000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params,sessionId}))})}
try{
await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true})});
let session,kind=process.argv[2]??'embed';
if(kind==='embed'){
 const all=await call('Target.getTargets');
 const child=all.targetInfos.find(t=>t.type==='iframe'&&t.url==='https://www.youtube.com/embed/aqz-KE-bpKQ');
 if(!child){console.log(JSON.stringify({kind,iframeTargetFound:false,targets:all.targetInfos.map(t=>({type:t.type,url:t.url}))},null,2));}
 else{session=(await call('Target.attachToTarget',{targetId:child.targetId,flatten:true})).sessionId;}
}
if(kind!=='embed'||session){
 const r=await call('Runtime.evaluate',{expression:`(async()=>{
 if(!['https://www.youtube.com/','https://m.youtube.com/'].some(prefix=>location.href.startsWith(prefix)))return {invalidDocument:location.href};
 const v=document.querySelector('video'),p=document.getElementById('movie_player');
 const result={url:location.href,title:document.title,video:!!v,error:document.querySelector('.ytp-error-content-wrap-reason')?.textContent??null};
 if(v){p?.playVideo?.();document.querySelector('.ytp-large-play-button')?.click();await new Promise(r=>setTimeout(r,2000));result.before={time:v.currentTime,duration:Number.isFinite(v.duration)?v.duration:null,paused:v.paused,ready:v.readyState};
 result.play=await Promise.race([v.play().then(()=>true,e=>e.name),new Promise(r=>setTimeout(()=>r('timeout'),5000))]);
 await new Promise(r=>setTimeout(r,1000));result.after={time:v.currentTime,paused:v.paused,ready:v.readyState};v.pause();
 }
 const cc=document.querySelector('.ytp-subtitles-button');result.captions={button:!!cc,disabled:cc?.getAttribute('disabled'),before:cc?.getAttribute('aria-pressed'),tracks:p?.getOption?.('captions','tracklist')?.map(t=>({languageCode:t.languageCode,id:t.id}))??[]};
 if(cc&&!cc.hasAttribute('disabled')){cc.click();await new Promise(r=>setTimeout(r,1000));result.captions.after=cc.getAttribute('aria-pressed');cc.click();}
 try{result.qualities=p?.getAvailableQualityLevels?.()??[];result.qualityBefore=p?.getPlaybackQuality?.()??null;
 if(result.qualities.length>1){const q=result.qualities.filter(q=>q!=='auto').at(-1);p.setPlaybackQualityRange?.(q,q);p.setPlaybackQuality?.(q);await new Promise(r=>setTimeout(r,300));result.qualityRequested=q;result.qualityAfter=p.getPlaybackQuality?.();}
 const button=document.querySelector('.ytp-settings-button');
 if(button){button.click();await new Promise(r=>setTimeout(r,100));let items=[...document.querySelectorAll('.ytp-menuitem')].filter(e=>e.getBoundingClientRect().height>0);result.qualityMenu=items.map(e=>e.textContent);const quality=items.find(e=>e.textContent.includes('Quality'));if(quality){quality.click();await new Promise(r=>setTimeout(r,100));items=[...document.querySelectorAll('.ytp-menuitem')].filter(e=>e.getBoundingClientRect().height>0);result.qualityOptions=items.map(e=>e.textContent);const chosen=items.find(e=>e.textContent.includes('144p'));if(chosen){result.selectedQuality=chosen.textContent;chosen.click();await v.play();await new Promise(r=>setTimeout(r,1000));result.qualityAfterUi=p.getPlaybackQuality?.();v.pause();}}}}
 catch(e){result.qualityError=e.name}
 return result;})()`,awaitPromise:true,returnByValue:true,userGesture:true},session);
 console.log(JSON.stringify({kind,time:new Date().toISOString(),result:r.result?.value??null,exception:r.exceptionDetails??null},null,2));
}
}finally{ws.close()}
