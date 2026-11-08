"""Narrow, leased URL-setting updates. Never update media or queue records."""
import hashlib,json,pathlib,subprocess
OLD='https://media.divinecreativegroup.com/'
NEW='https://media.divinemedia.us/'
FIELDS={'main':'encoderURL','encoder':'allowedStreamersURL'}
TABLES={'main':'configurations','encoder':'configurations_encoder'}
def query(container,sql):
 command=['docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" --batch --raw --skip-column-names']
 return subprocess.run(command,input=sql,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=35).stdout.strip()
def read_settings(main_db,encoder_db):
 return {label:json.loads(query(container,"SELECT JSON_OBJECT('value',`"+FIELDS[label]+"`) FROM `"+TABLES[label]+"` WHERE id=1;"))['value'] for label,container in [('main',main_db),('encoder',encoder_db)]}
def desired_settings(before):
 if before['main'] not in [OLD+'Encoder/',NEW+'Encoder/','https://localhost/Encoder/']:raise RuntimeError('Unexpected configured Encoder URL')
 after={'main':NEW+'Encoder/','encoder':before['encoder']}
 if before['encoder']:
  allowed=[x.strip().rstrip('/')+'/' for x in before['encoder'].splitlines() if x.strip()]
  if NEW not in allowed:
   after['encoder']=before['encoder'].rstrip('\r\n')+'\n'+NEW
 return after
def literal(value):return 'NULL' if value is None else "UNHEX('"+value.encode().hex()+"')"
def change(container,label,before,after):
 if before==after:return
 field=FIELDS[label]
 sql='UPDATE `'+TABLES[label]+'` SET `'+field+'`='+literal(after)+' WHERE id=1 AND `'+field+'` <=> '+literal(before)+'; SELECT ROW_COUNT();'
 if query(container,sql)!='1':raise RuntimeError('Configuration lease changed; refusing overwrite')
def apply(main_db,encoder_db,expected,state):
 before=read_settings(main_db,encoder_db)
 if before!=expected:raise RuntimeError('URL settings changed since verified backup')
 after=desired_settings(before);containers={'main':main_db,'encoder':encoder_db};written=[]
 state=pathlib.Path(state);state.mkdir(mode=0o700,parents=True,exist_ok=False)
 (state/'settings.json').write_text(json.dumps({'before':before,'after':after},indent=2))
 try:
  for label in FIELDS:change(containers[label],label,before[label],after[label]);written.append(label)
 except Exception:
  for label in reversed(written):change(containers[label],label,after[label],before[label])
  raise
 return {'url_settings_applied':True,'changed_fields':[label for label in FIELDS if before[label]!=after[label]],'rollback_state':str(state)}
def rollback(main_db,encoder_db,state):
 plan=json.loads((pathlib.Path(state)/'settings.json').read_text())
 if read_settings(main_db,encoder_db)!=plan['after']:raise RuntimeError('Later setting edit prevents rollback')
 for label,container in [('main',main_db),('encoder',encoder_db)]:change(container,label,plan['after'][label],plan['before'][label])
 return {'url_settings_rolled_back':True}
