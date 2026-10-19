from pathlib import Path
import collections,json,shutil
W=Path(__file__).parent
E=Path(r'E:\Android Auto Projects\roadium-browser\docs\shields\evidence\card04')
BASE='https://uazo.github.io/cromite/filters/'
RAW='https://raw.githubusercontent.com/uazo/cromite/pages/filters/'
NAMES=['easylist.txt','abp-filters-anti-cv.txt']
rows=[json.loads(line) for line in (W/'tls-requests.jsonl').read_text(encoding='utf-8').splitlines()]
expected={'fallback-success':(2,2,503),'fallback-advanced-enabled':(1,1,503),
    'primary-success':(2,0,200),'both-transports-fail':(2,2,503),
    'redirect-rejected':(2,2,302),'html-rejected':(2,2,200),'metadata-redirect-rejected':(2,2,200)}
assert set(r['phase'] for r in rows)==set(expected)
groups=[]
for phase,(primaries,fallbacks,primary_status) in expected.items():
    requests=[r for r in rows if r['phase']==phase]
    assert collections.Counter(r['transport'] for r in requests)==collections.Counter(primary=primaries,**({'fallback':fallbacks} if fallbacks else {})),phase
    for r in requests:
        name=r['path'].rsplit('/',1)[-1]
        assert name in NAMES and not r['had_cookie'] and not r['had_authorization']
        assert r['host']==('uazo.github.io' if r['transport']=='primary' else 'raw.githubusercontent.com')
        assert r['path']==('/cromite/filters/' if r['transport']=='primary' else '/uazo/cromite/pages/filters/')+name
        assert r['status']==(primary_status if r['transport']=='primary' else 503 if phase=='both-transports-fail' else 200)
    for name in NAMES:
        sequence=[r for r in requests if r['path'].endswith('/'+name)]
        if not sequence:continue
        assert sequence[0]['transport']=='primary'
        assert len(sequence)==(2 if fallbacks else 1)
        if len(sequence)==2:assert sequence[1]['transport']=='fallback'
    groups.append(dict(phase=phase,primary_requests=primaries,fallback_requests=fallbacks,
                       primary_status=primary_status,passed=True))
cases=[('fallback-opt-out','203001010004',False,4),
       ('fallback-advanced-enabled','203001010004',True,4),('primary-success','203001010005',True,4),
       ('both-transports-fail','203001010005',True,5),('failure-restart','203001010005',True,5),
       ('redirect-rejected','203001010006',True,4),('html-rejected','203001010007',True,4),
       ('metadata-redirect-rejected','203001010008',True,4)]
configuration=None
for label,version,advanced,stage in cases:
    snapshot=json.loads((E/(label+'-profile.json')).read_text(encoding='utf-8'))
    cfg=snapshot['filtering']['configurations']['adblock']
    assert cfg['enabled'] and cfg['subscriptions']==[BASE+n for n in NAMES]
    if configuration is None:configuration=snapshot['filtering']
    assert snapshot['filtering']==configuration
    assert snapshot['adblock']['privilegedfilters_enabled']==advanced
    report=(E/(label+'-report.txt')).read_text(encoding='utf-8')
    assert report.count('Loaded version: '+version)==2
    for name in NAMES:
        url=BASE+name
        assert RAW+name not in snapshot['adblock']['subscription_metadata']
        md=snapshot['adblock']['subscription_metadata'][url]
        d=md['roadium_diagnostics']
        assert md['version']==version and d['stage']==stage
        assert d['active_privileged']==(advanced and name=='abp-filters-anti-cv.txt')
        if label=='primary-success':
            assert not d['fallback_attempted'] and not d['primary_failure']
            assert d['last_success_source']==url
        elif stage==5:
            assert d['fallback_attempted'] and d['fallback_outcome']=='failed'
            assert d['last_success_source']==url
        else:
            assert d['fallback_attempted'] and d['fallback_outcome']=='activated'
            assert d['last_success_source']==RAW+name
            if label=='redirect-rejected':assert 'redirect' in d['primary_failure'].lower()
            if label=='html-rejected':assert 'html' in d['primary_failure'].lower()
            if label=='metadata-redirect-rejected':assert 'redirect' in d['primary_failure'].lower()
    probe=json.loads((E/(label+'.json')).read_text(encoding='utf-8'))
    assert probe['state']['probeIsUndefined']==advanced
    assert probe['state']['probeString']==('undefined' if advanced else 'fixture-value')
    assert probe['state']['cosmeticDisplay']=='none'
    assert any(f['errorText']=='net::ERR_BLOCKED_BY_ADMINISTRATOR' for f in probe['advertisingFailures'])
shutil.copyfile(W/'tls-requests.jsonl',E/'transport-requests.jsonl')
result=dict(installed_apk_sha256=json.loads((W/'runtime-state.json').read_text(encoding='utf-8'))['installed_apk_sha256'],
    method='Protected root-only flags, task-specific certificate SPKI and exact host resolution; SELinux enforcing; stock verified release-code APK',
    profile_user=13,isolated_browser_uid=1310204,transport_requests=len(rows),
    transport_phases=groups,unapproved_destination_requests=0,credential_bearing_fixture_requests=0,
    canonical_subscription_identity_retained=True,explicit_advanced_opt_out_preserved=True,
    ui_enable_safely_refreshed_only_trusted_anticv=True,observable_runtime_cases=len(cases),
    primary_success_skips_fallback=True,both_source_failure_retains_working_data_and_restart=True,
    http_and_metadata_redirects_rejected_before_target_fetch=True,http_200_html_rejected=True)
(E/'installed-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Eight installed cases, 24 exact fixture requests, canonical identity, policy and retention verified.')
