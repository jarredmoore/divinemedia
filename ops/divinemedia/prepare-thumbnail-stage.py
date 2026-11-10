#!/usr/bin/env python3
"""Extend the native-account recovery rehearsal with thumbnail hook verification."""
import argparse,base64,hashlib,json,pathlib,re,subprocess,sys,os
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();os.umask(0o077)
repo=pathlib.Path(__file__).resolve().parents[2];out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
subprocess.run([sys.executable,str(repo/'ops/divinemedia/prepare-unified-frontend-stage.py'),'--output',str(out/'base')],check=True,stdout=subprocess.DEVNULL)
base=(out/'base/stage.sh').read_text();payload=re.search(r"base64.b64decode\('([A-Za-z0-9+/=]+)'\)",base).group(1);files=json.loads(base64.b64decode(payload))
assets={p.name:p.read_text() for p in (repo/'backend/divine-thumbnails').glob('*.php')}
tests=(repo/'ops/divinemedia/thumbnail-stage-tests.py.txt').read_text()
release=hashlib.sha256(json.dumps(assets,sort_keys=True).encode()+tests.encode()+base.encode()+pathlib.Path(__file__).read_bytes()).hexdigest()[:12]
bundle='/srv/divinemedia/backups/native-thumbnails-'+release;old=json.loads((out/'base/release.json').read_text())['bundle']
s=files['stage.py'].replace(old,bundle)
s=s.replace(" proposal=native.inspect(app)"," shutil.copytree(pathlib.Path(bundle)/'thumbnail-plugin',pathlib.Path(app)/'plugin/DivineThumbnails')\n for path in (pathlib.Path(app)/'plugin/DivineThumbnails').glob('*.php'):path.chmod(0o644)\n (pathlib.Path(app)/'plugin/DivineThumbnails').chmod(0o755)\n proposal=native.inspect(app)")
s=s.replace(" # Match the persisted live vhost", " sql(native.insert_plugin('DivineThumbnails',{'uuid':'dbdb9ef6-71f0-48e4-b512-67cf98f50b1d','options':{},'version':'1.0'}))\n report['thumbnail_source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path(bundle+'/thumbnail-plugin').glob('*.php')}\n # Match the persisted live vhost")
s=s.replace(" phase='session-logout'",tests+"\n phase='session-logout'")
s=s.replace('print(json.dumps(report),flush=True)',"print(json.dumps({k:v for k,v in report.items() if k not in ['api_source_hashes','last_request']}),flush=True)")
compile(s,'thumbnail-stage.py','exec');files['stage.py']=s
files.update({'thumbnail-plugin/'+n:raw for n,raw in assets.items()})
payload=base64.b64encode(json.dumps(files).encode()).decode();script="#!/bin/sh\nset -eu\numask 077\npython3 - <<'VM'\nimport json,base64,pathlib\nr=pathlib.Path("+repr(bundle)+");r.mkdir(mode=0o700,exist_ok=True)\nfor n,s in json.loads(base64.b64decode('"+payload+"')).items():\n p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)\nVM\npython3 "+bundle+"/stage.py\n"
(out/'stage.sh').write_text(script);(out/'release.json').write_text(json.dumps({'bundle':bundle,'release':release}));print(bundle)
