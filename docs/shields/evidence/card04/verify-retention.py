from pathlib import Path
import json
E=Path(r'E:\Android Auto Projects\roadium-browser\docs\shields\evidence\card04')
def read(label):return json.loads((E/(label+'-profile.json')).read_text(encoding='utf-8'))
primary,failure,restart=[read(label) for label in ['primary-success','both-transports-fail','failure-restart']]
assert primary['filtering']==failure['filtering']==restart['filtering']
assert primary['adblock']['subscription_signatures']==failure['adblock']['subscription_signatures']==restart['adblock']['subscription_signatures']
for url in primary['filtering']['configurations']['adblock']['subscriptions']:
    p,f,r=[snapshot['adblock']['subscription_metadata'][url] for snapshot in [primary,failure,restart]]
    assert p['version']==f['version']==r['version']=='203001010005'
    assert f['download_count']==r['download_count']==p['download_count']
    assert f['error_count']==r['error_count']==p['error_count']+1==1
    assert p['last_installation_time']==f['last_installation_time']==r['last_installation_time']
    for md in [f,r]:
        d=md['roadium_diagnostics']
        assert d['stage']==5 and d['primary_failure']=='HTTP 503'
        assert d['fallback_attempted'] and d['fallback_outcome']=='failed'
        assert d['last_success_source']==url
        assert d['last_success']==p['roadium_diagnostics']['last_success']
        assert d['active_privileged']==p['roadium_diagnostics']['active_privileged']
result=dict(installed_version_retained='203001010005',cached_signatures_byte_identical=True,
    configuration_unchanged=True,one_error_per_logical_list_update=True,
    success_counters_and_installation_time_unchanged=True,active_source_retained='previous canonical primary',
    failed_attempt_and_working_data_survive_restart=True)
(E/'retention-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Both-source failure and restart retain signatures, choices, version, source, counters and policy.')
