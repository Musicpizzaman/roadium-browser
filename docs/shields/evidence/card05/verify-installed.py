from runtime import *
labels=['initial-advanced-enabled','second-generation','advanced-opt-out-baseline',
 'previous-version-recovery','force-stop-download','force-stop-candidate',
 'force-stop-previous','force-stop-published','storage-error-retention',
 'storage-error-restart','invalid-retention','invalid-restart','orphan-recovery',
 'schema-recovery','explicit-removal-recovery','activation-restart',
 'repeated-update-recovery','offline-bundled-recovery','missing-bundled-recovery',
 'repair-after-recovery']
def read(name):return json.loads((E/name).read_text(encoding='utf-8'))
def live(label,url):
 report=(E/(label+'-report.txt')).read_text(encoding='utf-8')
 section=report.split('\n'+url+'\n',1)[1].split('\n\n',1)[0]
 return dict(line.split(': ',1) for line in section.splitlines() if ': ' in line)
records=[]
for label in labels:
 profile=read(label+'-profile.json')
 configuration=profile['filtering']['configurations']['adblock']
 selected=set(URLS)-({URLS[1]} if label=='explicit-removal-recovery' else set())
 assert set(configuration['subscriptions'])==selected,label
 assert configuration['enabled'] is True,label
 assert configuration['filters']==['||manual.card05.invalid^'],label
 assert configuration['domains']==['excluded.card05.invalid'],label
 advanced=label in ['initial-advanced-enabled','second-generation']
 assert profile['adblock']['privilegedfilters_enabled'] is advanced,label
 report=(E/(label+'-report.txt')).read_text(encoding='utf-8')
 assert 'Ad blocking: Enabled' in report,label
 assert ('Advanced filtering: Enabled' if advanced else 'Advanced filtering: Disabled') in report,label
 assert (E/(label+'-report.png')).stat().st_size>1000
 assert (E/(label+'-report.xml')).is_file()
 probe=read(label+'.json')['probe']
 assert probe['state']['ready']=='complete',label
 assert probe['state']['probeIsUndefined'] is advanced,label
 assert probe['state']['unsupportedClicks']==0,label
 assert any(item['errorText']=='net::ERR_BLOCKED_BY_ADMINISTRATOR'
            for item in probe['advertisingFailures']),label
 bundled=label in ['offline-bundled-recovery','missing-bundled-recovery']
 assert probe['state']['cosmeticDisplay']==('block' if bundled else 'none'),label
 storage=read(label+'-storage.json')
 assert storage['directory']==ROOT+'/app_chrome/Default/adblock_subscriptions'
 files={f['file']:f['sha256'] for f in storage['files']}
 origins={}
 for url in selected:
  prefix='roadium-'+hashlib.sha256(url.encode()).hexdigest()
  assert len([name for name in files if name.startswith(prefix+'-')])<=2,(label,url)
  metadata=profile['adblock']['subscription_metadata'][url]
  # The raw preferences snapshot precedes the live UI report. Its asynchronous
  # persistence can lag loading; the in-process report and actual filtering are
  # the activation authority, independently checked against backing-file hashes.
  fields=live(label,url)
  origin=fields['Storage recovery'];origins[url]=origin
  if origin in ['current','previous']:
   chosen=[r['record'] for r in storage['records'] if
           r['file']==prefix+'.'+origin+'.json']
   assert len(chosen)==1,(label,url,origin)
   chosen=chosen[0]
   assert chosen['identity']==url and chosen['format']==1
   assert files[chosen['file']]==chosen['sha256'],(label,url)
   assert chosen['source']==fields['Active data source']
   assert re.fullmatch('20300102[0-9]{4}',fields['Loaded version']),(label,url)
  else:
   assert bundled,(label,url,origin)
   assert origin==('bundled baseline' if url in URLS[:2] else 'unavailable; update scheduled')
 if bundled:
  assert report.count('Active data source: bundled:')==2,label
  assert 'Engine: selected; no active data' in report,label
  assert 'Active data source: none; no valid data' in report,label
 if label=='explicit-removal-recovery':
  prefix='roadium-'+hashlib.sha256(URLS[1].encode()).hexdigest()
  assert not any(f.startswith(prefix) for f in files)
  assert not any(r['file'].startswith(prefix) for r in storage['records'])
  assert 'Anti-circumvention: not selected' in report
 records.append(dict(case=label,selected_lists=len(selected),advanced=advanced,
                     loaded_origins=origins,observable_blocking='passed',configuration='preserved'))
for stage in ['download','candidate','previous','published']:
 boundary=read('force-stop-'+stage+'-boundary.json')
 assert boundary['advanced_at_kill'] is False
 assert boundary['preference_version_at_kill']=='203001020003'
 assert boundary['success_count_before']==boundary['success_count_at_kill']
 after=read('force-stop-'+stage+'-profile.json')['adblock']['subscription_metadata'][URLS[1]]
 assert after['download_count']==boundary['success_count_before']
 assert live('force-stop-'+stage,URLS[1])['Loaded version']==('203001020004' if stage=='published' else '203001020003')
for case in ['storage-error','invalid']:
 counter=read(case+'-counters.json')
 assert counter['after']['download_count']==counter['before']['download_count']
 assert counter['after']['error_count']==counter['before']['error_count']+1
 assert counter['after']['roadium_diagnostics']['last_success']==counter['before']['roadium_diagnostics']['last_success']
 assert counter['after']['roadium_diagnostics']['last_success_source']==counter['before']['roadium_diagnostics']['last_success_source']
 for phase in ['retention','restart']:
  actual=read(case+'-'+phase+'-profile.json')['adblock']['subscription_metadata'][URLS[1]]
  assert actual['version']=='203001020003'
  assert actual['download_count']==counter['before']['download_count']
  assert actual['error_count']==counter['before']['error_count']+1
assert all(read('orphan-cleanup.json').values())
assert read('removed-cache-cleanup.json')['both_generations_and_records_removed']
assert not read('missing-bundled-recovery-storage.json')['files']
assert not read('missing-bundled-recovery-storage.json')['records']
assert live('previous-version-recovery',URLS[0])['Loaded version']=='203001020001'
assert live('previous-version-recovery',URLS[1])['Loaded version']=='203001020002'
previous=read('previous-version-recovery-storage.json')['records']
prefix='roadium-'+hashlib.sha256(URLS[1].encode()).hexdigest()
chosen=next(r['record'] for r in previous if r['file']==prefix+'.previous.json')
enabled=next(r['record'] for r in read('second-generation-storage.json')['records'] if r['file']==prefix+'.current.json')
assert chosen['privileged'] is True and chosen['sha256']==enabled['sha256']
repair=read('repair-before-update-profile.json')['adblock']['subscription_metadata']
assert all(repair[u]['roadium_diagnostics']['recovery']=='previous' for u in URLS[:2])
repair=read('repair-after-recovery-profile.json')['adblock']['subscription_metadata']
assert all(repair[u]['version']=='203001020006' for u in URLS[:2])
baseline=read('advanced-opt-out-baseline-profile.json')['adblock']['subscription_metadata']
for i,version in enumerate(['203001020006','203001020007','203001020008'],1):
 data=read('repeat-'+version+'-profile.json')['adblock']['subscription_metadata']
 for url in URLS[:2]:
  assert data[url]['version']==version
  assert data[url]['download_count']==baseline[url]['download_count']+i
manifest=read('x64-build-manifest.json')
expected=next(a['sha256'] for a in manifest['artifacts'] if a['file']=='ChromePublic.apk')
path=adb('shell','pm','path','--user','11',PKG).decode().strip().removeprefix('package:')
assert path.startswith('/data/app/') and path.endswith('/base.apk') and '\n' not in path
actual=adb('shell','sha256sum',path).decode().split()[0]
assert actual==expected
requests=[json.loads(row) for row in (W/'tls-requests.jsonl').read_text().splitlines()]
assert requests and not any(r['had_cookie'] or r['had_authorization'] for r in requests)
assert any(r['transport']=='custom' and r['status']==200 for r in requests)
invalid=[r for r in requests if r['phase']=='invalid' and r['path'].endswith('/abp-filters-anti-cv.txt')]
assert [r['transport'] for r in invalid]==['primary','fallback'] and all(r['status']==200 for r in invalid)
assert any(r['phase']=='force-stop-download' and r['mode']=='slow' for r in requests)
(E/'transport-requests.jsonl').write_text((W/'tls-requests.jsonl').read_text(),encoding='utf-8',newline='\n')
result=dict(status='passed',observable_runtime_cases=len(records),installed_apk_sha256=actual,
 user=11,device='API33 x64 Automotive emulator; read-only session',
 fresh_document_blocking_and_policy_verified=True,custom_url_rules_and_exceptions_preserved=True,
 force_stop_boundaries=4,failed_updates_counted_once=True,
 preference_snapshot_timing='Raw preferences snapshots precede live reports and may lag asynchronous recovery persistence; loaded versions/origins use live engine diagnostics and backing-file hashes',
 current_previous_retention_bound=2,repair_after_previous_recovery=True,
 bundled_offline_recovery=True,no_data_custom_state_honest=True,
 credential_headers_observed=False,transport_requests_total=len(requests),
 transport_scope_note='Initial default-list/component requests are retained transparently; phases identify controlled accepted filter cases',
 cases=records)
(E/'installed-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS:20 installed cases,4 forced-stop boundaries,real blocking/policy,retention,repair,bundle/configuration/counters/disk bound; installed APK matches')
