from runtime import *
import socket
assert 'emulator-5554' not in subprocess.check_output([ADB,'devices']).decode()
for port in [8844,8766]:
 with socket.socket() as sock:
  sock.settimeout(1)
  assert sock.connect_ex(('127.0.0.1',port))!=0
output=subprocess.check_output(['powershell.exe','-NoProfile','-Command',
 "Get-CimInstance Win32_Process -Filter 'ProcessId=47220 OR ProcessId=42032' | Select-Object ProcessId | ConvertTo-Json -Compress"],timeout=15).decode().strip()
assert not output or output=='null',output
result=dict(status='passed',own_user_removed=True,original_users_preserved=True,
 foreground_restored_before_shutdown=10,flags_removed=True,helper_removed=True,
 port_mappings_removed=True,host_fixture_servers_stopped=True,
 network_settings_restored=True,selinux='Enforcing',own_read_only_emulator_closed=True,
 avd_snapshot_saved=False,vehicle_properties_modified=False,
 saved_avd_disk_verification='Read-only/no-snapshot-save launch verified; byte-for-byte pre-launch disk hash was not captured',
 production_signing_material_accessed=False,private_backups_kept_outside_repository=True,
 host_cleanup_note='Legacy Windows PowerShell Stop-Process failed; the same re-verified own server PIDs were terminated with .NET Process.Kill; both listeners, process exits and emulator exit verified')
(E/'cleanup-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: own server processes/listeners and read-only emulator are closed; prior on-device cleanup checks and original user restoration passed')
