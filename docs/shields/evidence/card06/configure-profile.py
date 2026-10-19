from runtime import *
import sys
guard();stop()
data=prefs()
assert data.get('filtering',{}).get('configurations',{}).get('adblock') is not None
kind=sys.argv[1]
assert kind in ['frozen','controlled','custom']
advanced=sys.argv[2]=='true'
experiment='https://raw.githubusercontent.com/uazo/cromite/master/tools/filters/experimental-cromite-filters.txt'
selected=URLS[:2]+[experiment] if kind=='frozen' else URLS[:2] if kind=='controlled' else [URLS[2]]
data.setdefault('adblock',{})['privilegedfilters_enabled']=advanced
data['filtering']['configurations']['adblock'].update(enabled=True,subscriptions=selected,filters=[],domains=[])
for url in selected:data['adblock'].setdefault('subscription_metadata',{}).setdefault(url,{})['expiration_time']='0'
write_prefs(data)
(W/'tls-mode.json').write_text(json.dumps(dict(mode='frozen' if kind=='frozen' else 'controlled',phase=kind+'-'+str(advanced))))
print('Own profile configured',kind,'advanced',advanced)
launch()
