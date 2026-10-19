from pathlib import Path
import json, subprocess, sys
work = Path(__file__).parent
label, expected, blocking = sys.argv[1:]
result = subprocess.check_output(['node', str(work/'probe-advanced.mjs'), 'advertising'])
data = json.loads(result)
assert data['state']['probeIsUndefined'] == (expected == 'undefined'), data
assert data['state']['unsupportedClicks'] == 0
assert data['state']['cosmeticDisplay'] == ('none' if blocking == 'on' else 'block')
error = 'net::ERR_BLOCKED_BY_ADMINISTRATOR' if blocking == 'on' else 'net::ERR_INTERNET_DISCONNECTED'
assert any(f['errorText'] == error for f in data['advertisingFailures']), data
out = Path(r'E:\Android Auto Projects\roadium-browser\docs\shields\evidence\card03')
(out/(label+'.json')).write_bytes(result)
print(label, 'PASS', expected, error)
