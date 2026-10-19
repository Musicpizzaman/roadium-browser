from runtime import *
guard();stop()
data=prefs()
assert data.get('filtering',{}).get('configurations',{}).get('adblock') is not None
adblock=data.setdefault('adblock',{})
adblock['privilegedfilters_enabled']=True
config=data['filtering']['configurations']['adblock']
config.update(enabled=True,subscriptions=URLS,filters=['||manual.card05.invalid^'],
              domains=['excluded.card05.invalid'])
for url in URLS:
 adblock.setdefault('subscription_metadata',{}).setdefault(url,{})['expiration_time']='0'
write_prefs(data)
print('Own profile selected two approved lists + one custom URL; manual rule, exception and explicit advanced opt-in')
launch()
