#!/usr/bin/env python3
"""Back up only the URL settings needed by the hostname migration."""
import hashlib,importlib.util,json,os,pathlib
from domain_settings import read_settings,desired_settings
if __name__=='__main__':
 os.umask(0o077)
 root=pathlib.Path('/srv/divinemedia/backups');snapshot=pathlib.Path((root/'.latest-domain-snapshot').read_text().strip())
 values=read_settings('app-database-1','app-database_encoder-1');desired_settings(values)
 path=snapshot/'database-url-settings-before.json';data=json.dumps(values,indent=2).encode()
 if path.exists() and path.read_bytes()!=data:raise RuntimeError('Original settings snapshot already exists; refusing replacement')
 path.write_bytes(data);path.chmod(0o600)
 report_path=snapshot/'database-settings-backup-report.json'
 if report_path.exists():
  report=json.loads(report_path.read_text())
  if report['sha256']!=hashlib.sha256(data).hexdigest() or not report['roundtrip_verified']:raise RuntimeError('Existing backup proof does not match')
 else:
  spec=importlib.util.spec_from_file_location('domain_backup',pathlib.Path(__file__).with_name('prepare-domain-certificate.py'));backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
  report=backup.off_vm(path,snapshot.name);report_path.write_text(json.dumps(report,indent=2))
 print(json.dumps({'result':'pass','snapshot':str(snapshot),'url_settings_backup':report}))
