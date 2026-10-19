"""Verify recorded, non-private Card06 evidence; never operate the device."""
from pathlib import Path
import json,hashlib,collections
E=Path(__file__).parent
def read(name):return json.loads((E/name).read_text(encoding='utf-8'))
def state(name):return read(name)['state']
def accepted(name):
    s=state(name)
    assert s['roadiumProbe']=='undefined' and s['propertyAd']=='undefined'
    assert s['rejectedProbe']==s['badValue']=='fixture-value'
    assert s['domHidden'] and s['aborted'] and s['malformed']
    assert not s['errors']
    assert list(s['object']['playerResponse'])==['videoDetails']
    assert list(s['array'][0]['playerResponse'])==['videoDetails']
    assert list(s['response']['playerResponse'])==['videoDetails']
    assert s['missing']=={'ordinary':True}
    assert s['frames'] and s['frames'][-1]['probe']=='undefined'
    assert list(s['frames'][-1]['json']['playerResponse'])==['videoDetails']
    # Accepted syntax does NOT implement the upstream [-] removal grammar.
    assert s['removalGrammar']['entries'][0]['command']['reelWatchEndpoint']['adClientParams']['isAd'] is True
    return s
def denied(name):
    s=state(name)
    assert s['roadiumProbe']=='fixture-value' and s['propertyAd']=='object'
    assert not s['domHidden'] and not s['aborted'] and s['malformed']
    assert s['object']['playerResponse']['adPlacements']==[1]
    assert s['frames'][-1]['probe']=='frame-value'
    assert all(v['time']==0 and v['paused'] for v in s['videos'])
    return s
before=accepted('controlled-final-before.json')
assert all(v['time']==0 for v in before['videos'])
after=accepted('controlled-final-after.json')
assert all(v['time']>.8 for v in after['videos'][:2])
assert after['videos'][2]['time']==0
accepted('advanced-restored-final-trigger.json')
denied('advanced-off-final-trigger.json');denied('untrusted-final-trigger.json')
for name in ['controlled-final-ordinary.json','advanced-off-final-ordinary.json','untrusted-final-ordinary.json','resumed-ordinary.json']:
    operation=read(name)['operation'];assert operation['advanced'] and operation['paused']
assert read('controlled-final-webaudio.json')['operation']=='running'
audio=read('controlled-audio.json')['operation'];assert audio['advanced'] and audio['paused'] and audio['error'] is None
hidden1=state('background-trigger.json');hidden2=state('background-state.json')
assert hidden1['visibility']==hidden2['visibility']=='hidden'
assert all(v['paused'] for v in hidden1['videos']+hidden2['videos'])
assert [v['time'] for v in hidden1['videos']]==[v['time'] for v in hidden2['videos']]
assert state('resumed-state.json')['visibility']=='visible'
assert state('tab-away.json')['visibility']=='hidden'
assert state('tab-returned.json')['visibility']=='visible'
assert read('tab-returned-ordinary.json')['operation']['advanced']
fresh=read('fresh-default-profile.json');assert fresh['advanced_effective'] and not any('experimental-cromite' in s for s in fresh['config']['subscriptions'])
assert 'https://uazo.github.io/cromite/filters/abp-filters-anti-cv.txt' in fresh['config']['subscriptions']
upgrade=read('upgrade-preservation.json');assert upgrade['passed'] and upgrade['experimental_preserved'] and upgrade['advanced_opt_out_preserved']
for name in ['fresh-live-desktop-controls.json','fresh-live-mobile-controls.json']:
    operation=read(name)['operation'];assert operation['advanced'] and operation['paused'] and operation['seek']==10
features=read('fresh-live-features.json')['result']
assert features['captions']['after']=='true' and features['qualityAfter']=='tiny'
embed=read('fresh-live-embed-controls.json')['result']
assert embed['play'] is True and embed['after']['time']>embed['before']['time'] and embed['after']['ready']==4
for name in ['fresh-live-fullscreen.json','fresh-live-embed-fullscreen.json']:assert read(name)['operation']['entered']
installed=read('installed-apk.json');manifest=read('x64-build-manifest.json')
assert installed['verified'] and installed['sha256']==next(a['sha256'] for a in manifest['artifacts'] if a['file']=='ChromePublic.apk')
summary=dict(status='passed-with-explicit-live-gaps',installed_apk_sha256=installed['sha256'],
    fresh_default_verified=True,upgrade_preservation_verified=True,
    supported_runtime_commands=['json-prune','override-property-read','abort-on-property-write','skip-video','hide-if-matches-xpath'],
    dom_json_property_frame_and_privilege_cases='passed',ordinary_audio_video_webaudio='passed',
    background_scriptlet_play_attempt_stays_paused=True,foreground_recovery=True,
    actual_vehicle_restriction_state_tested=False,vehicle_properties_modified=False,
    live_desktop_mobile_embed_playback='passed',captions_english_toggle='passed',quality_actual_144p='passed',seek_seconds=10,
    fullscreen='passed',shorts='did not buffer in this lab; also failed advanced-off baseline; acceptance open',
    pre_roll='no observed opportunity; inconclusive',mid_roll='no observed opportunity; inconclusive',
    network='Loopback CONNECT relay for emulator DNS; end-to-end TLS; some ancillary hosts denied, so ad-format coverage remains limited',
    runtime_grammar_gap='json-prune [-] accepted by parser but does not remove matching array entry; no semantic rewrite performed',
    local_seek_limit='1s WebM seeks settle at keyframe0 with advanced on/off; exact local seek accuracy not claimed')
(E/'installed-verification.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: final binary fresh/upgrade, command/frame/policy, media/background and live playback checks; live gaps retained')
