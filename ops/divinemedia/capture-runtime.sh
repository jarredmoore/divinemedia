#!/bin/bash
set -euo pipefail
umask 077
backup=$(cat /srv/divinemedia/backups/.latest-verification-backup)
docker exec app-avideo-1 tar --dereference -C / -czf - etc/apache2 etc/php etc/ssl > "$backup/web-runtime-config.tar.gz" 2> "$backup/web-runtime-capture.stderr"
gzip -t "$backup/web-runtime-config.tar.gz"
python3 - "$backup" <<'RUNTIME_MANIFEST'
import json,sys,hashlib,os,datetime
root=sys.argv[1];name='web-runtime-config.tar.gz';h=hashlib.sha256(open(root+'/'+name,'rb').read()).hexdigest()
json.dump({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'name':name,'sha256':h,'bytes':os.path.getsize(root+'/'+name)}]},open(root+'/runtime-manifest.json','w'),indent=2)
print('PASS captured active web runtime configuration')
RUNTIME_MANIFEST
python3 "$(dirname "$0")/blob-roundtrip.py" --runtime
