"""Offline self-check of recorded observations; not a new network measurement."""
import hashlib,json,pathlib,re
root=pathlib.Path(__file__).resolve().parents[2]
x=root/'experiments/001-github-read'
d=json.loads((x/'observations.json').read_text());assert [r['id'] for r in d['records']]==['G01','G02','G03']
for r in d['records']:
 a=r['connector']['snapshot'];b=r['comparison']['snapshot']
 assert a==b,(r['id'],'snapshot mismatch')
 assert r['result']=='PASS' and all(r['matches'].values())
 assert r['connector']['started_at']<=r['connector']['ended_at']
 assert r['comparison']['attempts'][-1]['exit_code']==0
 if r['id']=='G01':
  raw=a['body_utf8'].encode();assert len(raw)==a['bytes'];assert hashlib.sha256(raw).hexdigest()==a['sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==a['git_blob']
 else: assert a['number']==(45 if r['id']=='G02' else 46)
for path in root.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
  if '://' not in target and not target.startswith('#'):
   assert (path.parent/target.split('#')[0]).is_file(),(path,target)
m=json.loads((x/'manifest.json').read_text())
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='manifest.json'}
assert set(m)==actual
for name,row in m.items():
 b=(root/name).read_bytes();assert len(b)==row['bytes'];assert hashlib.sha256(b).hexdigest()==row['sha256']
print('PASS: 3 operation records, README byte/hash/blob, Issue/PR fields, chronology, relative links, manifest '+str(len(m))+' files')
