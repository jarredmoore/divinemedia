#!/usr/bin/env python3
"""Apply a verified Live URL presentation fix; extend the original combined rollback lease."""
import argparse,importlib.util,json,os,pathlib,sys,tarfile,uuid
p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--state',required=True);a=p.parse_args();os.umask(0o077)
bundle=pathlib.Path(a.bundle);state=pathlib.Path(a.state);sys.path.insert(0,str(bundle))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
d=module('deployment',bundle/'deploy-native-live.py');backup=module('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py')
plan_bytes=(state/'plan.json').read_bytes();plan=json.loads(plan_bytes)
assert d.selected()==plan['rows'],'Native plugin configuration changed'
assert {n:d.sha(d.ROOT/n) for n in plan['assets']}==plan['assets'],'Presentation source changed'
original_assets=dict(plan['assets'])
css='divine-shell/shell.css'
assert d.sha(d.ROOT/css)=='c3fa1aac986f4945ad1656466cf6e07cf9280f6812a0fb0706d9fc99f1fff6aa','Stylesheet changed since route release'
plan['assets'][css]=d.sha(d.ROOT/css)
# Extend the combined recovery with the original stylesheet before its first change.
css_backup=state/'files'/css
assert not css_backup.exists(),'Unexpected existing stylesheet recovery copy'
css_backup.parent.mkdir(parents=True,exist_ok=True);css_backup.write_bytes((d.ROOT/css).read_bytes())
refinement=state/('presentation-'+uuid.uuid4().hex[:8]);refinement.mkdir(mode=0o700)
(refinement/'plan-before.json').write_bytes(plan_bytes)
for name in plan['assets']:
 target=refinement/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((d.ROOT/name).read_bytes())
with tarfile.open(refinement/'before.tar.gz','w:gz') as tar:
 for name in ['plan-before.json','divine-shell']:tar.add(refinement/name,arcname=name)
before=backup.off_vm(refinement/'before.tar.gz',refinement.name);old_media=d.media();expected={};report={'result':'pending','state':str(refinement),'combined_rollback_state':str(state),'before_backup':before}
try:
 for name in plan['assets']:
  raw=(bundle/'refined-assets'/name).read_bytes();d.atomic(d.ROOT/name,raw);expected[name]=d.native.digest(raw)
 d.run('docker','exec',d.WEB,'php','-l','/var/www/html/AVideo/divine-shell/head.php')
 assert '33-native-live-2' in d.get('/live?theme=code-black')
 assert d.native.digest(d.get('/divine-shell/shell.js').encode())==expected['divine-shell/shell.js']
 assert d.media()==old_media
 assert (state/'plan.json').read_bytes()==plan_bytes,'Combined recovery plan changed'
 plan['assets']=expected;(state/'plan.json').write_text(json.dumps(plan))
 (refinement/'after.json').write_text(json.dumps({'assets':expected,'combined_plan':plan}))
 after=backup.off_vm(refinement/'after.json',refinement.name)
 report.update({'result':'pass','after_backup':after,'media_hashes_preserved':len(old_media),'native_plugin_configuration_unchanged':True,'database_or_streaming_config_changed':False,'combined_rollback_lease_updated':True})
except Exception as e:
 if {n:d.sha(d.ROOT/n) for n in expected}!=expected:raise RuntimeError('Later asset change prevents refinement rollback') from e
 for name in expected:d.atomic(d.ROOT/name,(refinement/name).read_bytes())
 if (state/'plan.json').read_bytes() not in [plan_bytes,json.dumps(plan).encode()]:raise RuntimeError('Later recovery plan change prevents rollback') from e
 (state/'plan.json').write_bytes(plan_bytes)
 report.update({'result':'fail','rolled_back':True,'error_type':type(e).__name__})
(refinement/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
