#!/bin/bash
set -euo pipefail
umask 077
backup="/srv/divinemedia/backups/verified-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 700 "$backup"
inventory(){
 python3 - "$1" <<'PY'
import os,hashlib,json,sys
root='/srv/divinemedia/app/.compose/videos'; rows=[]
for base,dirs,files in os.walk(root):
 for name in sorted(files):
  if not name.lower().endswith(('.mp3','.mp4')):continue
  p=os.path.join(base,name);h=hashlib.sha256()
  with open(p,'rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  rows.append({'path':os.path.relpath(p,root),'bytes':os.path.getsize(p),'sha256':h.hexdigest()})
with open(sys.argv[1],'w') as f:json.dump(sorted(rows,key=lambda r:r['path']),f)
PY
}
inventory "$backup/media-before.json"
for spec in 'app-database-1 avideo' 'app-database_encoder-1 encoder'; do
 read -r container label <<< "$spec"
 docker exec "$container" sh -c 'export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb-dump --user="$MYSQL_USER" --single-transaction --quick --skip-lock-tables --hex-blob --routines --events --triggers --no-tablespaces --databases "$MYSQL_DATABASE"' 2> "$backup/$label-dump.stderr" | gzip -1 > "$backup/$label.sql.gz"
 docker exec "$container" sh -c 'export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" -NB -e "SELECT COALESCE(ENGINE,'\''VIEW'\''),COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() GROUP BY ENGINE;"' > "$backup/$label-engines.tsv" 2>/dev/null
 printf 'PASS database dump %s\n' "$label"
done
docker exec app-database-1 sh -c 'export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" -NB -e "SELECT COUNT(*) FROM videos;"' > "$backup/video-row-count.txt" 2>/dev/null
set +e
nice -n 19 tar -C /srv/divinemedia --warning=no-file-changed -czf "$backup/application.tar.gz" app 2> "$backup/application-tar.stderr"
tar_status=$?
set -e
if [ "$tar_status" -gt 1 ]; then printf 'FAIL application archive\n';exit 1;fi
nice -n 19 tar -czf "$backup/host-support.tar.gz" /etc/fstab /etc/cron.d /etc/systemd/system 2> "$backup/host-tar.stderr"
docker inspect app-avideo-1 app-database-1 app-database_encoder-1 app-live-1 app-memcached-1 > "$backup/container-recovery-metadata.json"
inventory "$backup/media-after.json"
cmp -s "$backup/media-before.json" "$backup/media-after.json" || { printf 'FAIL media changed during backup; not marking verified\n';exit 1; }
for file in "$backup"/*.gz; do gzip -t "$file";done
python3 - "$backup" <<'PY'
import sys,json,tarfile,hashlib,os,datetime
root=sys.argv[1]; inventory=json.load(open(root+'/media-after.json'));expected={r['path']:r for r in inventory};matched=set()
with tarfile.open(root+'/application.tar.gz','r:gz') as t:
 for m in t:
  prefix='app/.compose/videos/'
  if not m.isfile() or not m.name.startswith(prefix):continue
  rel=m.name[len(prefix):]
  if rel not in expected:continue
  h=hashlib.sha256();f=t.extractfile(m)
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
  assert h.hexdigest()==expected[rel]['sha256'], 'archive media hash mismatch'
  matched.add(rel)
assert matched==set(expected),'missing media in archive'
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'media_count':len(inventory),'media_bytes':sum(r['bytes'] for r in inventory),'media_stable_during_backup':True,'archived_media_hashes_verified':len(matched),'main_video_rows':int(open(root+'/video-row-count.txt').read()),'files':[]}
for name in sorted(os.listdir(root)):
 p=root+'/'+name
 if not os.path.isfile(p):continue
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 manifest['files'].append({'name':name,'bytes':os.path.getsize(p),'sha256':h.hexdigest()})
with open(root+'/manifest.json','w') as f:json.dump(manifest,f,indent=2)
print(json.dumps({k:v for k,v in manifest.items() if k!='files'}))
PY
printf '%s\n' "$backup" > /srv/divinemedia/backups/.latest-verification-backup
printf 'BACKUP_PATH %s\n' "$backup"
printf 'BACKUP_SIZE\n'
du -sh "$backup"
printf 'LIVE_HEALTH\n'
docker ps --format '{{.Names}} {{.Status}}'
