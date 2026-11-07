#!/bin/bash
set -euo pipefail
umask 077
backup=$(cat /srv/divinemedia/backups/.latest-verification-backup)
mapfile -t images < <(python3 - "$backup" <<'IMAGE_IDS'
import json,sys
print('\n'.join(sorted(set(r['Image'] for r in json.load(open(sys.argv[1]+'/container-recovery-metadata.json'))))))
IMAGE_IDS
)
nice -n 19 docker image save "${images[@]}" | nice -n 19 gzip -1 > "$backup/container-images.tar.gz"
gzip -t "$backup/container-images.tar.gz"
python3 - "$backup" <<'IMAGE_MANIFEST'
import os,json,hashlib,sys,tarfile,datetime
root=sys.argv[1];name='container-images.tar.gz';h=hashlib.sha256()
with open(root+'/'+name,'rb') as f:
 for b in iter(lambda:f.read(1048576),b''):h.update(b)
required=set(r['Image'].removeprefix('sha256:') for r in json.load(open(root+'/container-recovery-metadata.json')))
found=set()
with tarfile.open(root+'/'+name,'r|gz') as archive:
 for member in archive:
  candidate=member.name.rsplit('/',1)[-1].removesuffix('.json')
  if member.isfile() and candidate in required:
   digest=hashlib.sha256(archive.extractfile(member).read()).hexdigest()
   assert digest==candidate,'Recovery image config checksum mismatch'
   found.add(digest)
assert required<=found,'Missing recovery image'
json.dump({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'image_count':len(required),'image_config_ids_verified':True,'files':[{'name':name,'sha256':h.hexdigest(),'bytes':os.path.getsize(root+'/'+name)}]},open(root+'/images-manifest.json','w'),indent=2)
print('PASS recovery images exported and config IDs verified:',len(required))
IMAGE_MANIFEST
python3 "$(dirname "$0")/blob-roundtrip.py" --images
