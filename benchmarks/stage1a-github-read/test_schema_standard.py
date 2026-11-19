"""Cross-check all seven timestamp fields with the public Draft 2020-12 schema.

Optional offline development dependency: jsonschema==4.26.0.
No product requests or real experiment execution.
"""
import copy
import json
import pathlib

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / 'input.schema.json').read_text(encoding='utf-8'))
BASE = json.loads((ROOT / 'fixtures/base.json').read_text(encoding='utf-8'))

VALID = (
    '2000-01-01T00:00:25Z',
    '2000-01-01T00:00:25.000000Z',
    '2000-01-01T00:00:25.000001Z',
    '2000-01-01T09:00:25+09:00',
    '1999-12-31T19:00:25-05:00',
)
INVALID = (
    '2000-01-01T00:00:25Zjunk',
    '2000-01-01T00:00:25Z\n',
    '2000-01-01T00:00:25Z\r\n',
    '2000-01-01T00:00:25+09:00:30',
    '2000-01-01T00:00:25.0000001Z',
    '2000-01-01T00:00:25.0000000Z',
    '2000-01-01T00:00:25',
    'prefix2000-01-01T00:00:25Z',
    '\n2000-01-01T00:00:25Z',
)
PATHS = (
    ('preregistered_at',),
    ('results_available_at',),
    ('runs', 0, 'segments', 0, 'started_at'),
    ('runs', 0, 'segments', 0, 'ended_at'),
    ('runs', 0, 'corrections', 0, 'at'),
    ('runs', 0, 'operations', 0, 'started_at'),
    ('runs', 0, 'operations', 0, 'ended_at'),
)


def set_field(packet, path, value):
    current = packet
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


def main():
    Draft202012Validator.check_schema(SCHEMA)
    validator = Draft202012Validator(SCHEMA)
    base = copy.deepcopy(BASE)
    base['runs'][0]['corrections'] = [{
        'old_value': 'synthetic-old',
        'new_value': 'synthetic-new',
        'reason': 'synthetic-valid-correction',
        'actor': 'synthetic-operator',
        'at': '2000-01-01T00:00:05Z',
        'evidence': ['synthetic:correction'],
    }]
    assert validator.is_valid(base), 'base packet with valid correction must satisfy full schema'
    checks = 0
    for path in PATHS:
        for value, expected in [(v, True) for v in VALID] + [(v, False) for v in INVALID]:
            packet = copy.deepcopy(base)
            set_field(packet, path, value)
            accepted = validator.is_valid(packet)
            assert accepted is expected, (
                f'JSON Schema timestamp mismatch at {path}: '
                f'{value!r}, expected={expected}, actual={accepted}'
            )
            checks += 1
    print(f'PASS Draft 2020-12: 7 timestamp paths, {checks}/{checks} cases; experiment NOT_TESTED')


if __name__ == '__main__':
    main()
