from runtime import *
import io,tarfile
guard()
end=time.monotonic()+25
while time.monotonic()<end:
 data=prefs(); d=data['adblock']['subscription_metadata'][URLS[1]]['roadium_diagnostics']
 if data['adblock']['privilegedfilters_enabled'] is False and d.get('active_privileged') is False:break
 time.sleep(.5)
else:raise RuntimeError('Opt-out conversion did not finish')
stop()
assert set(data['filtering']['configurations']['adblock']['subscriptions'])==set(URLS)
assert data['filtering']['configurations']['adblock']['filters']==['||manual.card05.invalid^']
assert data['filtering']['configurations']['adblock']['domains']==['excluded.card05.invalid']
payload=adb('exec-out','tar','-cf','-','-C',ROOT,
 'app_chrome/Default/Preferences','app_chrome/Default/adblock_subscriptions')
with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
 for member in archive.getmembers():
  assert member.name=='app_chrome/Default/Preferences' or member.name.startswith('app_chrome/Default/adblock_subscriptions')
  assert '..' not in member.name and not member.name.startswith('/')
  assert member.isfile() or member.isdir()
assert not (W/'runtime-base.tar').exists()
(W/'runtime-base.tar').write_bytes(payload)
record=dict(sha256=hashlib.sha256(payload).hexdigest(),user=11,advanced=False,
 subscriptions=URLS,manual_rules=['||manual.card05.invalid^'],exceptions=['excluded.card05.invalid'])
(W/'runtime-base.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Backed up own three-list current/previous baseline and explicit opt-out')
launch()
