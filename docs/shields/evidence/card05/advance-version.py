from runtime import *
import sys
version=sys.argv[1];label=sys.argv[2]
assert re.fullmatch('20300102[0-9]{4}',version)
mode('primary',version,label)
expire();launch();wait_version(version)
print('Activated',version,'for both approved canonical identities')
