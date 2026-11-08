#!/usr/bin/env python3
"""Install or roll back the additive creator on a specified AVideo tree.
Only adds a theme include to two view templates; no handler or database changes.
"""
import argparse,datetime,hashlib,json,os,pathlib,shutil,stat,tempfile,uuid
MARKER='DM_CREATOR_V1'
HOOK="""\n<?php /* DM_CREATOR_V1: presentation only; retain native upload handlers. */
if (is_file(dirname(__DIR__, 2) . '/divine-creator/theme.php')) {
    require dirname(__DIR__, 2) . '/divine-creator/theme.php';
}
?>\n"""
def digest(data):return hashlib.sha256(data).hexdigest()
def atomic(path,data,original_stat):
    fd,tmp=tempfile.mkstemp(prefix='.dm-creator-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.chmod(tmp,stat.S_IMODE(original_stat.st_mode))
        if os.geteuid()==0:os.chown(tmp,original_stat.st_uid,original_stat.st_gid)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def install(root,assets,backup_root,expected=None,apply=False):
    root=pathlib.Path(root).resolve();assets=pathlib.Path(assets).resolve()
    target=root/'divine-creator'
    if target.exists():raise RuntimeError('Creator directory already exists; refusing an unreviewed overwrite')
    paths=['view/mini-upload-form/index.php','.compose/encoder/view/index.php'];originals={};changes={};metadata={}
    for name in paths:
        path=root/name
        if path.is_symlink():raise RuntimeError('Core source must not be a symlink')
        originals[name]=path.read_bytes();metadata[name]=path.stat()
        if expected and digest(originals[name])!=expected[name]:raise RuntimeError('Source changed since isolated verification: '+name)
    for name,data in originals.items():
        if MARKER.encode() in data or data.lower().count(b'</body>')!=1:
            raise RuntimeError('Unsupported or already patched creator template: '+name)
        offset=data.lower().index(b'</body>')
        changes[name]=data[:offset]+HOOK.encode()+data[offset:]
    asset_files=sorted(p for p in assets.iterdir() if p.is_file())
    required={'theme.php','creator.css','creator.js','mark.svg'}
    if {p.name for p in asset_files}!=required:raise RuntimeError('Unexpected creator asset set')
    plan={'before':{name:digest(data) for name,data in originals.items()},'after':{name:digest(data) for name,data in changes.items()},'assets':{p.name:digest(p.read_bytes()) for p in asset_files}}
    if not apply:return plan
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    backup=pathlib.Path(backup_root)/('creator-'+stamp);backup.mkdir(mode=0o700,parents=True,exist_ok=False)
    for name,data in originals.items():
        dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    (backup/'plan.json').write_text(json.dumps(plan,indent=2))
    staging=root/('.divine-creator-'+stamp);staging.mkdir(mode=0o755);os.chmod(staging,0o755)
    try:
        for p in asset_files:shutil.copyfile(p,staging/p.name);os.chmod(staging/p.name,0o644)
        os.replace(staging,target)
        for name,data in changes.items():atomic(root/name,data,metadata[name])
    except Exception:
        for name,data in originals.items():atomic(root/name,data,metadata[name])
        shutil.rmtree(target,ignore_errors=True);shutil.rmtree(staging,ignore_errors=True)
        raise
    plan['rollback_snapshot']=str(backup)
    return plan
def rollback(root,snapshot):
    root=pathlib.Path(root).resolve();snapshot=pathlib.Path(snapshot).resolve();plan=json.loads((snapshot/'plan.json').read_text())
    for name,sha in plan['after'].items():
        if digest((root/name).read_bytes())!=sha:raise RuntimeError('Core source changed after install; refusing overwrite: '+name)
    target=root/'divine-creator'
    for name,sha in plan['assets'].items():
        if not (target/name).is_file() or digest((target/name).read_bytes())!=sha:raise RuntimeError('Creator assets changed after install; refusing removal')
    if {p.name for p in target.iterdir()}!=set(plan['assets']):raise RuntimeError('Unowned files in creator directory; refusing removal')
    for name,sha in plan['before'].items():
        if digest((snapshot/name).read_bytes())!=sha:raise RuntimeError('Rollback snapshot checksum mismatch: '+name)
    for name in plan['before']:atomic(root/name,(snapshot/name).read_bytes(),(root/name).stat())
    shutil.rmtree(target)
    return {'rolled_back':True,'before':plan['before']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--assets');p.add_argument('--backup-root');p.add_argument('--expected');p.add_argument('--apply',action='store_true');p.add_argument('--rollback')
    args=p.parse_args()
    if args.rollback:result=rollback(args.root,args.rollback)
    else:
        if not args.assets or not args.backup_root:p.error('--assets and --backup-root required')
        expected=json.loads(pathlib.Path(args.expected).read_text()) if args.expected else None
        result=install(args.root,args.assets,args.backup_root,expected,args.apply)
    print(json.dumps(result,indent=2))
