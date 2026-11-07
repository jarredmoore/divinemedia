#!/bin/sh
set -eu
umask 077
python3 - <<'FINAL_SAFETY_CHECK'
import os,json,hashlib,subprocess,shutil
root=open('/srv/divinemedia/backups/.latest-verification-backup').read().strip();source=open('/srv/divinemedia/backups/.latest-roundtrip-backup').read().strip()
report=json.load(open(source+'/restore-verification.json'));expected=json.load(open(source+'/media-after.json'));count=0
for row in expected:
 p='/srv/divinemedia/app/.compose/videos/'+row['path'];h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 assert h.hexdigest()==row['sha256'],'Original media changed'
 count+=1
report['original_media_hashes_unchanged']=count
health=subprocess.check_output(['docker','ps','--format','{{.Names}} {{.Status}}'],text=True).strip().splitlines();report['live_containers_after_rehearsal']=health
assert not subprocess.check_output(['docker','ps','-a','--filter','name=dm-rehearsal-','--format','{{.Names}}'],text=True).strip(),'Scratch containers remain'
json.dump(report,open(root+'/recovery-verification.json','w'),indent=2)
name='recovery-verification.json';content=open(root+'/'+name,'rb').read();json.dump({'files':[{'name':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}]},open(root+'/verification-manifest.json','w'),indent=2)
print('PASS original media unchanged:',count)
for row in health:print(row)
print('PASS no remaining rehearsal containers')
FINAL_SAFETY_CHECK
python3 "$(dirname "$0")/blob-roundtrip.py" --verification
