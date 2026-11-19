"""Offline synthetic record validator. No network, product calls or truth certification.
Exit 0: record consistent (not experiment PASS); 1: rejected; 2: live mode blocked.
The schema subset below fails closed on unknown keywords. Provenance/evidence
assertions still require a human/independent audit; references are not signatures.
"""
import base64
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent

class Invalid(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise Invalid(reason)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load(path):
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, 'DUPLICATE_JSON_KEY:' + k)
            out[k] = v
        return out
    return json.loads(pathlib.Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Invalid('NONFINITE_NUMBER')))

def schema_check(value, schema, at='$'):
    known = {'$schema', '$id', 'title', 'type', 'properties', 'required',
             'additionalProperties', 'items', 'enum', 'const', 'minLength',
             'pattern', 'minimum', 'maximum', 'minItems', 'maxItems', 'uniqueItems'}
    require(not set(schema) - known, 'UNSUPPORTED_SCHEMA_KEYWORD')
    types = schema.get('type', [])
    if isinstance(types, str):
        types = [types]
    checks = {'object': type(value) is dict, 'array': type(value) is list,
              'string': type(value) is str, 'integer': type(value) is int,
              'number': type(value) in (int, float), 'boolean': type(value) is bool,
              'null': value is None}
    require(not types or any(checks.get(t, False) for t in types), 'SCHEMA_TYPE:' + at)
    if 'enum' in schema:
        require(value in schema['enum'], 'SCHEMA_ENUM:' + at)
    if 'const' in schema:
        require(value == schema['const'], 'SCHEMA_CONST:' + at)
    if type(value) is str:
        require(len(value) >= schema.get('minLength', 0), 'SCHEMA_EMPTY:' + at)
        if 'pattern' in schema:
            require(re.fullmatch(schema['pattern'], value) is not None, 'SCHEMA_PATTERN:' + at)
    if type(value) in (int, float):
        require(schema.get('minimum', value) <= value <= schema.get('maximum', value), 'SCHEMA_RANGE:' + at)
    if type(value) is list:
        require(schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', len(value)), 'SCHEMA_LENGTH:' + at)
        if schema.get('uniqueItems'):
            require(len({json.dumps(v, sort_keys=True) for v in value}) == len(value), 'SCHEMA_DUPLICATES:' + at)
        for i, item in enumerate(value):
            schema_check(item, schema.get('items', {}), at + '/' + str(i))
    if type(value) is dict:
        require(set(schema.get('required', [])) <= set(value), 'SCHEMA_MISSING:' + at)
        props = schema.get('properties', {})
        extra = set(value) - set(props)
        additional = schema.get('additionalProperties', True)
        require(additional is not False or not extra, 'SCHEMA_EXTRA:' + at)
        for key, item in value.items():
            if key in props:
                schema_check(item, props[key], at + '/' + key)
            elif type(additional) is dict:
                schema_check(item, additional, at + '/' + key)

def time(value):
    try:
        d = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as e:
        raise Invalid('BAD_TIMESTAMP') from e
    require(d.tzinfo is not None, 'TIMEZONE_REQUIRED')
    return d

def check_lock():
    lock = load(ROOT / 'protocol.lock.json')
    require(type(lock) is dict and lock.get('version') == 1, 'BAD_LOCK')
    require(set(lock['files']) == {'protocol.json', 'input.schema.json', 'verify.py',
            'expected-readme.txt', 'target-tree.txt', 'INSTRUCTIONS.txt'}, 'LOCK_SET')
    for name, meta in lock['files'].items():
        b = (ROOT / name).read_bytes()
        require(len(b) == meta['size'] and sha(b) == meta['sha256'], 'LOCK_CHANGED:' + name)
    return load(ROOT / 'protocol.json')

def expected_id(r):
    exp, client, variant = r['selected_experience'], r['initial_client_surface'], r['experience_variant']
    if exp == 'dot':
        return 'DOT'
    if exp == 'Chat':
        return {'Web': 'CHAT-WEB', 'desktop': 'CHAT-DESKTOP', 'iOS': 'CHAT-MOBILE', 'Android': 'CHAT-MOBILE'}.get(client, 'UNKNOWN')
    if exp == 'Work':
        if variant == 'Cloud':
            return {'Web': 'WORK-CLOUD-WEB', 'desktop': 'WORK-CLOUD-DESKTOP', 'iOS': 'WORK-CLOUD-MOBILE', 'Android': 'WORK-CLOUD-MOBILE'}.get(client, 'UNKNOWN')
        if variant == 'Local' and client == 'desktop':
            return 'WORK-LOCAL'
    if exp == 'Codex':
        if variant == 'Cloud' and client != 'UNKNOWN':
            return 'CODEX-CLOUD'
        if variant == 'Local' and client in ('CLI', 'IDE', 'desktop'):
            return 'CODEX-LOCAL'
    return 'UNKNOWN'

def check_attribution(r):
    cid = r['comparison_id']
    require(cid == expected_id(r), 'START_ID_CONTRADICTION')
    if cid == 'UNKNOWN':
        require(r['comparison_id_status'] == 'UNRESOLVED' and r['comparison_id_reason'].strip(), 'UNKNOWN_ID_NOT_PRESERVED')
    else:
        require(r['comparison_id_status'] == 'CONFIRMED', 'ID_STATUS')
    sites = set()
    ids = set()
    segment_windows = []
    for s in r['segments']:
        require(s['segment_id'] not in ids, 'DUPLICATE_SEGMENT')
        ids.add(s['segment_id'])
        begin, end = time(s['started_at']), time(s['ended_at'])
        require(begin <= end, 'SEGMENT_TIME')
        if segment_windows:
            require(segment_windows[-1][1] <= begin, 'SEGMENT_OVERLAP_OR_OUT_OF_ORDER')
        segment_windows.append((begin, end))
        if s['execution_site'] != 'UNKNOWN':
            require(s['site_evidence_basis'] == 'execution-log', 'CLIENT_IS_NOT_EXECUTION_EVIDENCE')
        sites.add(s['execution_site'])
    for o in r['operations']:
        begin, end = time(o['started_at']), time(o['ended_at'])
        require(begin <= end, 'OP_TIME')
        require(sum(a <= begin and end <= b for a, b in segment_windows) == 1,
                'OP_OUTSIDE_OR_AMBIGUOUS_SEGMENT')
    site = r['execution_site']
    if site == 'mixed':
        require({'local', 'cloud'} <= sites, 'MIXED_NOT_OBSERVED')
    elif site in ('local', 'cloud'):
        require(sites == {site}, 'SEGMENT_SITE_CONTRADICTION')
    if r['executor'] != 'UNKNOWN':
        require(r['segments'][-1]['executor'] == r['executor'], 'EXECUTOR_SEGMENT_CONTRADICTION')
    # UNKNOWN site is allowed but never converted into local/cloud by ID or client.
    if r['model_verified'] != 'UNKNOWN':
        require(r['model_evidence_basis'] == 'execution-log', 'DISPLAY_IS_NOT_MODEL_EVIDENCE')
    if r['delegate_chain']:
        require(r['delegate_evidence'] and r['attribution'] != 'executor-only', 'DELEGATE_NOT_SOLO')
        require(r['executor'] == r['delegate_chain'][-1], 'DELEGATE_EXECUTOR_CONTRADICTION')
    if r['attribution'] == 'orchestration-and-delegate':
        require(bool(r['delegate_chain']), 'DELEGATE_CHAIN_MISSING')
    for correction in r['corrections']:
        time(correction['at'])
    # Corrections do not replace initial ID; each corrected execution is a separate record.

def run_outcome(r, p):
    ops = r['operations']
    if not ops:
        return 'NOT_TESTED'
    target = p['target']
    terminal = {}
    by_case = {}
    order = []
    for o in ops:
        case = o['case_id']
        if case not in by_case:
            by_case[case] = []
            order.append(case)
        attempts = by_case[case]
        require(o['attempt'] == len(attempts) + 1, 'ATTEMPT_SEQUENCE')
        if attempts:
            require(attempts[-1]['observation'] == 'communication_failure', 'RETRY_NOT_COMMUNICATION_FAILURE')
        attempts.append(o)
        require(o['repository'] == target['repository'] and o['commit'] == target['commit'], 'TARGET_CHANGED')
        require(o['route'] == case[0], 'ROUTE_CHANGED')
        require(o['tool'] == {'A':'synthetic:github.fetch_file','B':'synthetic:unauthenticated-https-get'}[o['route']], 'UNREGISTERED_SYNTHETIC_TOOL')
        require(o['timeout_seconds'] == r['conditions']['timeout']['value'], 'TIMEOUT_CONDITION_MISMATCH')
        require(o['timeout_enforced'], 'DEADLINE_UNENFORCED')
        require(o['source'] == 'https://api.github.com/repos/' + target['repository'] + '/contents/' + o['path'] + '?ref=' + target['commit'], 'SOURCE_MISMATCH')
        require(o['path'] == target['normal_path' if case.endswith('N') else 'missing_path'], 'PATH_CHANGED')
        require(time(o['started_at']) <= time(o['ended_at']), 'OP_TIME')
        require(o['http_status_direct'] == (o['http_status'] is not None), 'HTTP_STATUS_NOT_DIRECT')
        if o['observation'] != 'success':
            require(o['file_body_base64'] is None, 'ERROR_AS_FILE_BODY')
        terminal[case] = o
    require(order == p['order'][:len(order)], 'OPERATION_ORDER')
    require([o['case_id'] for o in ops] == [case for case in order for _ in by_case[case]], 'INTERLEAVED_RETRY')
    for before, after in zip(ops, ops[1:]):
        require(time(before['ended_at']) <= time(after['started_at']), 'OVERLAPPING_OPERATIONS')
    # Same route/tool within route, including retries. No substitution counted as success.
    for route in ['A', 'B']:
        group = [o for o in ops if o['route'] == route]
        require(len({o['tool'] for o in group}) <= 1, 'TOOL_SUBSTITUTION')
    for o in ops:
        if o['case_id'].endswith('N') and o['observation'] == 'explicit_missing':
            return 'FAIL'
        if o['observation'] == 'success':
            if o['case_id'].endswith('M'):
                return 'FAIL'
            require(o['file_body_base64'] is not None, 'SUCCESS_WITHOUT_BYTES')
            try:
                b = base64.b64decode(o['file_body_base64'], validate=True)
            except Exception as e:
                raise Invalid('BAD_BASE64') from e
            blob = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
            if b != (ROOT/'expected-readme.txt').read_bytes() or len(b) != target['normal_size'] or sha(b) != target['normal_sha256'] or blob != target['normal_git_blob']:
                return 'FAIL'
    observations = [o['observation'] for o in terminal.values()]
    if 'permission_constraint' in observations:
        return 'BLOCKED'
    if len(terminal) != 4:
        return 'UNKNOWN'
    if all(o == 'not_tested' for o in observations):
        return 'NOT_TESTED'
    if any(o in ('communication_failure', 'general_error', 'not_tested') for o in observations):
        return 'UNKNOWN'
    for case in ('A-M', 'B-M'):
        o = terminal[case]
        require(o['observation'] == 'explicit_missing', 'MISSING_NOT_EXPLICIT')
        require('NOT_FOUND' in o['raw_response'] or 'Not Found' in o['raw_response'], 'MISSING_ERROR_NOT_PRESENT')
    require(terminal['B-M']['http_status'] == 404 and terminal['B-N']['http_status'] == 200, 'COMPARISON_HTTP_EVIDENCE')
    require(terminal['A-N']['observation'] == terminal['B-N']['observation'] == 'success', 'NORMAL_CONTROL_MISSING')
    return 'PASS'

def compare(packet, p):
    c, profile = packet['comparison'], packet['profile']
    if not c['performed']:
        require(not c['ranking_claim'], 'RANKING_WITHOUT_COMPARISON')
        return 'NOT_TESTED', 'COMPARISON_NOT_PERFORMED'
    runs = packet['runs']
    if c['stop_triggered']:
        return '比較不可', 'STOP_CONDITION'
    if profile['id_required'] and any(r['comparison_id'] == 'UNKNOWN' for r in runs):
        return '比較不可', 'UNRESOLVED_ATTRIBUTION'
    diffs = []
    for name in profile['condition_names']:
        a, b = [r['conditions'][name]['value'] for r in runs]
        if a is None or b is None or a == 'UNKNOWN' or b == 'UNKNOWN':
            return '比較不可', 'IMPORTANT_EVIDENCE_UNKNOWN:' + name
        if a != b:
            diffs.append(name)
    require(set(c['difference_assessments']) == set(diffs), 'DIFFERENCE_LEDGER_MISMATCH')
    outside = []
    for name in diffs:
        assessment = c['difference_assessments'][name]
        if not assessment['impact_known']:
            return '比較不可', 'UNKNOWN_DIFFERENCE_IMPACT:' + name
        if name in profile['required_equivalences']:
            return '比較不可', 'REQUIRED_EQUIVALENCE_MISMATCH:' + name
        tolerance = profile['allowed_deviations'].get(name)
        a, b = [r['conditions'][name]['value'] for r in runs]
        if tolerance and type(a) in (int, float) and type(b) in (int, float) and abs(a-b) <= tolerance['absolute_max_difference']:
            continue
        outside.append(name)
    if outside:
        if profile['comparison_purpose'] == 'descriptive' and set(outside) <= set(profile['descriptive_differences']):
            return '条件差あり', 'OBSERVED_DESCRIPTIVE_DIFFERENCES:' + ','.join(outside)
        return '比較不可', 'OUTSIDE_PREDECLARED_TOLERANCE'
    return '比較可能', 'EQUIVALENT_WITHIN_PREDECLARED_TOLERANCE'

def evaluate(packet):
    try:
        p = check_lock()
        required = {'comparison_purpose','metric','required_equivalences','allowed_deviations','stop_conditions','condition_names','descriptive_differences','id_required'}
        require(type(packet) is dict and type(packet.get('profile')) is dict and required <= set(packet['profile']), 'MISSING_PREDECLARED_FIELD')
        schema_check(packet, load(ROOT / 'input.schema.json'))
        if packet['record_kind'] != 'SYNTHETIC':
            return {'record_validation':'BLOCKED','experiment_outcome':'NOT_TESTED','comparison_decision':'NOT_TESTED','reason':'LIVE_ADAPTER_NOT_IMPLEMENTED_OR_AUTHORIZED'}
        require(packet['protocol_id'] == p['protocol_id'] and packet['protocol_version'] == p['protocol_version'] and packet['protocol_sha256'] == sha((ROOT/'protocol.json').read_bytes()), 'PROTOCOL_VERSION_OR_HASH')
        profile = packet['profile']
        require(profile == p['profiles'][profile['comparison_purpose']], 'PREDECLARED_PROFILE_CHANGED')
        require(time(packet['preregistered_at']) < time(packet['results_available_at']), 'POSTHOC_PROTOCOL')
        require(len({r['run_id'] for r in packet['runs']}) == 2, 'DUPLICATE_RUN')
        outcomes = []
        for r in packet['runs']:
            check_attribution(r)
            for o in r['operations']:
                require(time(packet['preregistered_at']) <= time(o['started_at']) <= time(o['ended_at']) <= time(packet['results_available_at']), 'OP_OUTSIDE_DECLARED_WINDOW')
            require(r['conditions']['fixture']['value'] == p['target']['normal_sha256'], 'FIXTURE_CONDITION_MISMATCH')
            require(r['conditions']['permissions']['value'] == 'public-fixed-commit-read-only', 'PERMISSION_CONDITION_MISMATCH')
            outcome = run_outcome(r, p)
            require(outcome == r['claimed_outcome'], 'FALSE_OUTCOME_CLAIM:' + outcome)
            outcomes.append(outcome)
        custody = packet['custody']
        if 'PASS' in [custody['saved'], custody['retrieved'], custody['byte_match'], custody['independent_audit']]:
            require(bool(custody['evidence']), 'CUSTODY_WITHOUT_EVIDENCE')
        if custody['byte_match'] == 'PASS':
            require(custody['saved'] == custody['retrieved'] == 'PASS', 'RETRIEVAL_NOT_DONE')
        if custody['independent_audit'] == 'PASS':
            raise Invalid('INDEPENDENT_REVIEW_IS_SEPARATE_GATE')
        decision, reason = compare(packet, p)
        if packet['comparison']['ranking_claim']:
            require(decision == '比較可能' and profile['comparison_purpose'] == 'controlled-ranking', 'UNSUPPORTED_RANKING_CLAIM')
            require(all(outcome == 'PASS' for outcome in outcomes), 'RANKING_REQUIRES_PASS_RUNS')
            raise Invalid('SYNTHETIC_RANKING_NOT_AUTHORIZED')
        return {'record_validation':'PASS','experiment_outcome':'NOT_TESTED','synthetic_run_outcomes':outcomes,'comparison_decision':decision,'reason':reason,'ranking_status':'NOT_TESTED','ranking_reason':'NO_REAL_EXECUTION_OR_INDEPENDENT_EVIDENCE','scope':'synthetic record consistency only; not product/provenance verification'}
    except (Invalid, KeyError, TypeError, ValueError) as e:
        return {'record_validation':'FAIL','protocol_validation':'REJECTED','experiment_outcome':'NOT_TESTED','comparison_decision':'比較不可','reason':str(e)}

if __name__ == '__main__':
    try:
        result = evaluate(load(sys.argv[1]))
    except (OSError, Invalid, ValueError, IndexError) as e:
        result = {'record_validation':'FAIL','protocol_validation':'REJECTED','experiment_outcome':'NOT_TESTED','comparison_decision':'比較不可','reason':str(e)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit({'PASS':0,'FAIL':1,'BLOCKED':2}[result['record_validation']])
