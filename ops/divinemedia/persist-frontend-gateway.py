#!/usr/bin/env python3
"""Migrate an existing gateway key into the access-denied persistent videos volume."""
import hashlib, importlib.util, json, os, pathlib, subprocess, tarfile, uuid
ROOT=pathlib.Path('/srv/divinemedia/app'); WEB='app-avideo-1'
def run(*args,data=None):
 return subprocess.run(args,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=60).stdout
if __name__=='__main__':
 os.umask(0o077)
 target=ROOT/'divine-api/index.php'; before=target.read_bytes()
 old=b"$keyFile = '/var/www/tmp/divine-frontend-gateway.key';\n$expected = is_file($keyFile) ? trim((string)file_get_contents($keyFile)) : '';"
 new=b"// PHP guard and persistent volume keep this credential outside disposable native tmp storage.\n$keyFile = '/var/www/html/AVideo/videos/.divine-private/frontend-gateway.php';\nif (is_file($keyFile)) {\n    define('DM_GATEWAY_INTERNAL', true);\n    $expected = trim((string)require $keyFile);\n} else {\n    // Compatibility for restored rehearsals and installations not yet migrated.\n    $keyFile = '/var/www/tmp/divine-frontend-gateway.key';\n    $expected = is_file($keyFile) ? trim((string)file_get_contents($keyFile)) : '';\n}"
 assert before.count(old)==1
 key=run('docker','exec',WEB,'cat','/var/www/tmp/divine-frontend-gateway.key').strip()
 assert len(key)==64 and all(c in b'0123456789abcdef' for c in key)
 private=ROOT/'.compose/videos/.divine-private'; assert not private.exists()
 state=pathlib.Path('/srv/divinemedia/backups')/('gateway-persistence-'+uuid.uuid4().hex[:12]);state.mkdir(mode=0o700)
 (state/'index.php').write_bytes(before)
 spec=importlib.util.spec_from_file_location('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
 with tarfile.open(state/'before.tar.gz','w:gz') as tar:tar.add(target,arcname='index.php')
 proof=backup.off_vm(state/'before.tar.gz',state.name)
 try:
  private.mkdir(mode=0o750);os.chown(private,33,33)
  deny=private/'.htaccess';deny.write_text('Require all denied\n');deny.chmod(0o644)
  guard=b"<?php if (!defined('DM_GATEWAY_INTERNAL')) { http_response_code(404); exit; } return "
  probe=private/'probe.php';probe.write_bytes(guard+b"'access-denied-probe';\n");probe.chmod(0o644)
  code=run('curl','-sS','--resolve','media.divinemedia.us:443:127.0.0.1','-o','/dev/null','-w','%{http_code}','https://media.divinemedia.us/videos/.divine-private/probe.php').decode()
  assert code in ('403','404'),'Private directory must deny HTTP before credential placement'
  probe.unlink();secret=private/'frontend-gateway.php';secret.write_bytes(guard+b"'"+key+b"';\n");secret.chmod(0o600);os.chown(secret,33,33)
  tmp=target.with_suffix('.gateway-update.php');tmp.write_bytes(before.replace(old,new));tmp.chmod(target.stat().st_mode&0o777)
  run('docker','exec',WEB,'php','-l','/var/www/html/AVideo/divine-api/index.gateway-update.php');tmp.replace(target)
  assert run('curl','-sS','--resolve','media.divinemedia.us:443:127.0.0.1','-o','/dev/null','-w','%{http_code}','https://media.divinemedia.us/videos/.divine-private/frontend-gateway.php').decode() in ('403','404')
  # PHP CLI reads the credential internally; it never appears in command arguments or output.
  php="define('DM_GATEWAY_INTERNAL',true);$k=trim(require '/var/www/html/AVideo/videos/.divine-private/frontend-gateway.php');$c=curl_init('https://media.divinemedia.us/divine-api/index.php?action=session');curl_setopt_array($c,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_RESOLVE=>['media.divinemedia.us:443:127.0.0.1'],CURLOPT_HTTPHEADER=>['X-Divine-Gateway-Key: '.$k,'X-Divine-Frontend-Origin: https://divinemedia.us']]);$d=json_decode(curl_exec($c),true);if(curl_getinfo($c,CURLINFO_RESPONSE_CODE)!==200||!isset($d['csrf']))exit(1);echo 'pass';"
  assert run('docker','exec',WEB,'php','-r',php)==b'pass'
  result={'result':'pass','state':str(state),'before_backup':proof,'persistent_private_directory_http_status':int(code),'gateway_session_smoke':'pass','container_restarted':False,'media_content_modified':False,'index_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 except Exception:
  target.write_bytes(before)
  for p in private.glob('*'):p.unlink()
  if private.exists():private.rmdir()
  raise
 (state/'report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
