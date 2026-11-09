#!/usr/bin/env python3
"""Build an isolated native-account/API rehearsal, never a production fixture."""
from pathlib import Path
import argparse,base64,json,hashlib,os
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();os.umask(0o077)
repo=Path(__file__).resolve().parents[2];out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
files={'native_live.py':(repo/'ops/divinemedia/native_live.py').read_text()}
for path in (repo/'backend/frontend-api').glob('*.php'):files['api/'+path.name]=path.read_text()
tests=(repo/'ops/divinemedia/unified-stage-tests.py.txt').read_text()
release=hashlib.sha256(json.dumps(files,sort_keys=True).encode()+tests.encode()+Path(__file__).read_bytes()).hexdigest()[:12]
bundle='/srv/divinemedia/backups/unified-frontend-'+release
s=(repo/'ops/divinemedia/stage-player-utilities.py').read_text()
start=s.index(" phase='stage-player-plugins'");end=s.index(" phase='start-recovered-cache'",start);s=s[:start]+s[end:]
s=s.replace('import os,json,tarfile','import pathlib,secrets,re,os,json,tarfile',1)
s=s.replace('source=open(',"bundle="+repr(bundle)+"\nliveRoot=pathlib.Path('/srv/divinemedia/app')\ndomain_snapshot=pathlib.Path(open('/srv/divinemedia/backups/.latest-domain-snapshot').read().strip())\nsource=open(",1)
s=s.replace(" app=scratch+'/app';media=app+'/.compose/videos'"," with tarfile.open(domain_snapshot/'runtime-active.tar.gz') as archive:archive.extractall(scratch+'/domain-runtime',filter=recovery_filter)\n app=scratch+'/app';media=app+'/.compose/videos'")
s=s.replace(" phase='create-isolated-network'",'''
 phase='current-native-source-copy'
 for name in ['objects','plugin']:shutil.copytree(liveRoot/name,pathlib.Path(app)/name,dirs_exist_ok=True)
 for relative in ['.htaccess','.compose/videos/configuration.php','.compose/encoder/videos/configuration.php']:
  shutil.copyfile(liveRoot/relative,pathlib.Path(app)/relative)
 shutil.copytree(pathlib.Path(bundle)/'api',pathlib.Path(app)/'divine-api')
 (pathlib.Path(app)/'divine-api').chmod(0o755)
 for path in (pathlib.Path(app)/'divine-api').glob('*.php'):path.chmod(0o644)
 sys.path.insert(0,bundle);import native_live as native
 proposal=native.inspect(app)
 phase='create-isolated-network' ''',1)
s=s.replace(" phase='start-recovered-cache'",'''
 phase='isolated-native-feature-tables'
 main=prefix+'-avideo';db=dict(x.split('=',1) for x in byname['app-database-1']['Config']['Env'] if '=' in x)['MYSQL_DATABASE']
 def sql(q):return docker('exec','-i',main,'mariadb','--protocol=socket','-uroot','-NB',db,data=q).stdout.strip()
 for name in ['Live','PlayLists']:
  existing=sql('SHOW TABLES;').splitlines()
  sql(native.schema_plan((pathlib.Path(app)/'plugin'/name/'install/install.sql').read_text(),name,existing));sql(native.insert_plugin(name,proposal[name]))
 # Match the persisted live vhost; the original recovery snapshot predates the HLS proxy.
 vhost=pathlib.Path(scratch+'/domain-runtime/etc/apache2/sites-enabled/000-default.conf')
 vhost.write_text(docker('exec','app-avideo-1','cat','/etc/apache2/sites-enabled/000-default.conf').stdout)
 phase='start-recovered-cache' ''',1)
s=s.replace(" phase='start-recovered-web-runtime'",'''
 phase='isolated-empty-stream-stats'
 live=prefix+'-live';containers.append(live)
 conf=pathlib.Path(scratch)/'nginx.conf'
 conf.write_text("pid /tmp/nginx.pid; error_log /dev/stderr; events { worker_connections 64; } rtmp { server { listen 1935; application live { live on; record off; } } } http { access_log off; server { listen 8080; location /stat { rtmp_stat all; } } }")
 docker('run','-d','--name',live,'--network',network,'--network-alias','live','--memory','128m','--cpus','0.25','--pids-limit','64','--mount','type=bind,src='+str(conf)+',dst=/tmp/dm-nginx.conf,readonly','--entrypoint','/usr/local/nginx/sbin/nginx',byname['app-live-1']['Image'],'-c','/tmp/dm-nginx.conf','-g','daemon off;')
 phase='start-recovered-web-runtime' ''',1)
s=s.replace("'--network',network,'--memory','1g'","'--network',network,'--network-alias','avideo','--memory','1g'")
s=s.replace("(app+'/.compose/letsencrypt','/etc/letsencrypt',True)","(scratch+'/domain-runtime/etc/letsencrypt','/etc/letsencrypt',True)")
s=s.replace("(scratch+'/runtime/etc/apache2','/etc/apache2',True)","(scratch+'/domain-runtime/etc/apache2','/etc/apache2',True)")
start=s.index(" phase='isolated-web-http'");end=s.index(" report['result']='pass'",start);s=s[:start]+tests+s[end:]
s=s.replace('open("/srv/divinemedia/backups/native-player-stage-report.json","w").write(json.dumps(report,indent=2))','')
s=s.replace("report['error_type']=type(exc).__name__","report['error_type']=type(exc).__name__;report['assertion']=str(exc)[:180] if isinstance(exc,AssertionError) else None")
s+="\nopen(bundle+'/stage-report.json','w').write(json.dumps(report,indent=2))\n"
compile(s,'unified-stage.py','exec');files['stage.py']=s
payload=base64.b64encode(json.dumps(files).encode()).decode()
script="#!/bin/sh\nset -eu\numask 077\npython3 - <<'VM'\nimport json,base64,pathlib\nr=pathlib.Path("+repr(bundle)+");r.mkdir(mode=0o700,exist_ok=True)\nfor n,s in json.loads(base64.b64decode('"+payload+"')).items():\n p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)\nVM\npython3 "+bundle+"/stage.py\n"
(out/'stage.sh').write_text(script);(out/'release.json').write_text(json.dumps({'bundle':bundle,'release':release}));print(bundle)
