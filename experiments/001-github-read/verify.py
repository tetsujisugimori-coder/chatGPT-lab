"""Offline verification of recorded evidence, not a network remeasurement.
Scope: every repository file except root .git (directory or worktree pointer),
the exact experiments/002-github-missing-path subtree (separate manifest),
and this experiment's manifest itself. Other hidden files are NOT ignored.
"""
import hashlib
import json
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPERIMENT = 'experiments/001-github-read'
MANIFEST = EXPERIMENT + '/manifest.json'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def scoped_files(root):
    files = set()
    for base, dirs, names in os.walk(root, followlinks=False):
        base = pathlib.Path(base)
        if base == root / 'experiments':
            dirs[:] = [d for d in dirs if d != '002-github-missing-path']
        if base == root:
            dirs[:] = [d for d in dirs if d != '.git']
            names = [n for n in names if n != '.git']
        for directory in dirs:
            require(not (base / directory).is_symlink(), 'scope: symlink directory')
        for name in names:
            path = base / name
            require(not path.is_symlink(), 'scope: symlink file')
            rel = path.relative_to(root).as_posix()
            if rel != MANIFEST:
                files.add(rel)
    return files


def snapshot(value, operation):
    require(type(value) is dict, operation + ': snapshot object required')
    if operation == 'G01':
        required = {'body_utf8', 'bytes', 'sha256', 'git_blob'}
        require(required <= value.keys(), 'G01: snapshot fields missing')
        require(type(value['body_utf8']) is str, 'G01: body type')
        require(type(value['bytes']) is int and value['bytes'] >= 0, 'G01: bytes type')
        for key, width in [('sha256', 64), ('git_blob', 40)]:
            require(type(value[key]) is str and re.fullmatch('[0-9a-f]{'+str(width)+'}', value[key]), 'G01: '+key+' type')
        raw = value['body_utf8'].encode('utf-8')
        require(len(raw) == value['bytes'], 'G01: byte count mismatch')
        require(hashlib.sha256(raw).hexdigest() == value['sha256'], 'G01: SHA mismatch')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == value['git_blob'], 'G01: blob mismatch')
        return {'body_bytes', 'git_blob'}
    fields = {'number', 'title', 'state', 'body', 'updated_at'}
    if operation == 'G03':
        fields |= {'base', 'head'}
    require(fields <= value.keys(), operation + ': snapshot fields missing')
    require(type(value['number']) is int and value['number'] == (45 if operation == 'G02' else 46), operation + ': number')
    for key in ['title', 'state', 'body', 'updated_at']:
        require(type(value[key]) is str, operation + ': '+key+' type')
    require(value['state'] in {'open', 'closed'}, operation + ': state')
    require(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value['updated_at']), operation + ': updated_at format')
    if operation == 'G03':
        for key in ['base', 'head']:
            v = value[key]
            require(type(v) is dict and {'ref', 'sha'} <= v.keys(), 'G03: '+key+' fields missing')
            require(type(v['ref']) is str and bool(v['ref']), 'G03: '+key+' ref')
            require(type(v['sha']) is str and re.fullmatch('[0-9a-f]{40}', v['sha']), 'G03: '+key+' sha')
    return fields


def verify(root=ROOT):
    d = json.loads((root / EXPERIMENT / 'observations.json').read_text())
    require([r['id'] for r in d['records']] == ['G01', 'G02', 'G03'], 'operation set')
    for r in d['records']:
        a, b = r['connector']['snapshot'], r['comparison']['snapshot']
        required = snapshot(a, r['id'])
        snapshot(b, r['id'])
        require(a == b, r['id'] + ': snapshot mismatch')
        matches = r['matches']
        require(type(matches) is dict and set(matches) == required, r['id'] + ': matches fields')
        require(all(type(v) is bool and v is True for v in matches.values()), r['id'] + ': matches boolean true required')
        require(r['result'] == 'PASS', r['id'] + ': result')
        require(r['connector']['started_at'] <= r['connector']['ended_at'], r['id'] + ': chronology')
        require(r['comparison']['attempts'][-1]['exit_code'] == 0, r['id'] + ': comparison exit')
    actual = scoped_files(root)
    required_files = {'README.md', 'docs/research-map.md'} | {EXPERIMENT+'/'+p for p in ['PLAN.md', 'RESULTS.md', 'observations.json', 'verify.py']}
    require(required_files <= actual, 'scope: required file missing')
    m = json.loads((root / MANIFEST).read_text())
    require(set(m) == actual, 'manifest: file set mismatch')
    for name, row in m.items():
        raw = (root / name).read_bytes()
        require(type(row['bytes']) is int and len(raw) == row['bytes'], 'manifest: size '+name)
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'manifest: SHA '+name)
        if name.endswith('.md'):
            for target in re.findall(r'\]\(([^)]+)\)', raw.decode()):
                if '://' not in target and not target.startswith('#'):
                    require((root / name).parent.joinpath(target.split('#')[0]).is_file(), 'link: '+name)
    print('PASS: offline schema/comparison, README bytes/SHA/blob, links, manifest '+str(len(m))+' files; not network remeasurement')


if __name__ == '__main__':
    try:
        verify()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('FAIL:', error)
        raise SystemExit(1)
