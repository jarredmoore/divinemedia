from pathlib import Path
import argparse,os
import json,base64,hashlib
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);a=parser.parse_args();os.umask(0o077);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
r=Path(__file__).resolve().parents[2];s=(r/'ops/divinemedia/stage-player-utilities.py').read_text()
a=s.index(" phase='stage-player-plugins'");b=s.index(" phase='start-recovered-cache'",a);s=s[:a]+s[b:]
s=s.replace('open("/srv/divinemedia/backups/native-player-stage-report.json","w").write(json.dumps(report,indent=2))','')
module=(r/'ops/divinemedia/native_live.py').read_text();release=hashlib.sha256(module.encode()+(r/'ops/divinemedia/deploy-native-live.py').read_bytes()+(r/'ops/divinemedia/native-live-stage-tests.py.txt').read_bytes()+(r/'backend/divine-shell/head.php').read_bytes()+(r/'backend/divine-shell/shell.js').read_bytes()).hexdigest()[:12];bundle='/srv/divinemedia/backups/native-live-'+release
s=s.replace('import os,json,tarfile','import pathlib,re,os,json,tarfile',1).replace('source=open(',"bundle="+repr(bundle)+"\nliveRoot=pathlib.Path('/srv/divinemedia/app')\ndomain_snapshot=pathlib.Path(open('/srv/divinemedia/backups/.latest-domain-snapshot').read().strip())\nsource=open(",1)
s=s.replace(" app=scratch+'/app';media=app+'/.compose/videos'", " with tarfile.open(domain_snapshot/'runtime-active.tar.gz') as archive:archive.extractall(scratch+'/domain-runtime',filter=recovery_filter)\n app=scratch+'/app';media=app+'/.compose/videos'")
s=s.replace(" phase='create-isolated-network'",''' phase='copy-current-native-presentation'
 for relative in ['.htaccess','view/include/head.php','.compose/encoder/view/index.php','.compose/encoder/view/index.header.php','.compose/videos/configuration.php','.compose/encoder/videos/configuration.php','view/userLogin.php','view/mini-upload-form/index.php']:
  dest=pathlib.Path(app)/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(liveRoot/relative,dest)
 for name in ['divine-entrance','divine-creator','divine-shell','plugin/Live','plugin/PlayLists']:
  shutil.copytree(liveRoot/name,pathlib.Path(app)/name,dirs_exist_ok=True)
 for relative in ['divine-shell/head.php','divine-shell/shell.js']:shutil.copyfile(pathlib.Path(bundle)/'assets'/relative,pathlib.Path(app)/relative)
 sys.path.insert(0,bundle);import native_live as native
 proposal=native.inspect(app);report['source_hashes']=native.SOURCE_HASHES
 phase='create-isolated-network' ''',1)
s=s.replace(" phase='start-recovered-cache'",''' phase='install-native-feature-schemas'
 main=prefix+'-avideo';db=dict(x.split('=',1) for x in byname['app-database-1']['Config']['Env'] if '=' in x)['MYSQL_DATABASE']
 def sql(q):return docker('exec','-i',main,'mariadb','--protocol=socket','-uroot','-NB',db,data=q).stdout.strip()
 report['native_feature_tables']={}
 for name in ['Live','PlayLists']:
  existing=sql('SHOW TABLES;').splitlines();schema=native.schema_plan((pathlib.Path(app)/'plugin'/name/'install/install.sql').read_text(),name,existing)
  sql(schema);sql(native.insert_plugin(name,proposal[name]));report['native_feature_tables'][name]=list(native.SCHEMAS[name])
 # Only the isolated app configuration enables the shared HLS proxy; no live vhost writes.
 vhost=pathlib.Path(scratch+'/domain-runtime/etc/apache2/sites-enabled/000-default.conf');vhost.write_bytes(native.proxy_vhost(docker('exec','app-avideo-1','cat','/etc/apache2/sites-enabled/000-default.conf').stdout.encode()))
 phase='start-recovered-cache' ''',1)
s=s.replace("(app+'/.compose/letsencrypt','/etc/letsencrypt',True)","(scratch+'/domain-runtime/etc/letsencrypt','/etc/letsencrypt',True)").replace("(scratch+'/runtime/etc/apache2','/etc/apache2',True)","(scratch+'/domain-runtime/etc/apache2','/etc/apache2',True)")
s=s.replace(" web=prefix+'-web';containers.append(web);record=byname['app-avideo-1']", " web=prefix+'-web';containers.append(web);record=byname['app-avideo-1']")
s=s.replace("'--network',network,'--memory','1g'", "'--network',network,'--network-alias','avideo','--memory','1g'")
# Share only disposable HLS between the isolated stream server and Apache.
s=s.replace(" args += [record['Image'],'-c','apache2ctl -D FOREGROUND']", " hls=pathlib.Path(scratch)/'HLS';hls.mkdir(mode=0o777);hls.chmod(0o777)\n args+=['--mount','type=bind,src='+str(hls)+',dst=/HLS']\n args += [record['Image'],'-c','apache2ctl -D FOREGROUND']")
a=s.index(" phase='isolated-web-http'");b=s.index(" report['result']='pass'",a)
tests=(r/'ops/divinemedia/native-live-stage-tests.py.txt').read_text()
assert tests,'Write isolated tests first'
s=s[:a]+tests+s[b:]
s=s.replace("report['error_type']=type(exc).__name__", "report['error_type']=type(exc).__name__;report['assertion']=str(exc)[:160] if isinstance(exc,AssertionError) else None")
s+='\nopen(bundle+"/stage-report.json","w").write(json.dumps(report,indent=2))\n'
s=s.replace('print(json.dumps(report),flush=True)',"print(json.dumps({k:v for k,v in report.items() if k not in ['source_hashes','databases','native_feature_tables']}),flush=True)")
compile(s,'native-live-stage.py','exec')
files={'native_live.py':module,'deploy-native-live.py':(r/'ops/divinemedia/deploy-native-live.py').read_text(),'stage.py':s}
for name in ['head.php','shell.js']:files['assets/divine-shell/'+name]=(r/'backend/divine-shell'/name).read_text()
payload=base64.b64encode(json.dumps(files).encode()).decode()
script="#!/bin/sh\nset -eu\numask 077\npython3 - <<'VM'\nimport pathlib,json,base64\nr=pathlib.Path("+repr(bundle)+");r.mkdir(mode=0o700,exist_ok=True)\nfor n,s in json.loads(base64.b64decode('"+payload+"')).items():\n p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)\nVM\npython3 "+bundle+"/stage.py\n"
(out/'live-stage.sh').write_text(script);(out/'live-release.json').write_text(json.dumps({'bundle':bundle}));print(bundle)
