from runtime import *
import tarfile,io
CACHE=ROOT+'/app_chrome/Default/adblock_subscriptions'
def restore():
 guard();stop()
 state=json.loads((W/'runtime-state.json').read_text())
 payload=(W/'runtime-base.tar').read_bytes()
 assert hashlib.sha256(payload).hexdigest()==json.loads((W/'runtime-base.json').read_text())['sha256']
 prefixes={'roadium-'+hashlib.sha256(url.encode()).hexdigest() for url in URLS}
 paths=adb('shell','find',CACHE,'-mindepth','1','-maxdepth','1').decode().splitlines()
 for path in paths:
  assert path.startswith(CACHE+'/')
  name=path.rsplit('/',1)[-1]
  owned=any(name.startswith(prefix) for prefix in prefixes)
  assert not owned or re.fullmatch(r'roadium-[0-9a-f]{64}(?:-[0-9A-Fa-f]{32}\.fb|\.(?:current|previous)\.json(?:\.pending)?)',name),name
  if owned:adb('shell','rm','-f',path)
 # Snapshot restore intentionally resets only this task-created user's own
 # cache/Preferences between independent destructive fault cases.
 remote='/data/local/tmp/roadium-card05-base.tar'
 adb('push',str(W/'runtime-base.tar'),remote)
 adb('shell','tar','-xf',remote,'-C',ROOT)
 adb('shell','rm','-f',remote)
 adb('shell','chown','-R',state['profile_uid'],CACHE)
 adb('shell','chcon','-R',state['context'],CACHE)
 adb('shell','chown',state['profile_uid'],PREF)
 adb('shell','chcon',state['context'],PREF)
 assert prefs()['adblock']['privilegedfilters_enabled'] is False
if __name__=='__main__':restore()
