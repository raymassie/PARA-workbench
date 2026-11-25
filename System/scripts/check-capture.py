#!/usr/bin/env python3
"""Read-only PARA capture acceptance evidence. No Git or model is required.

Use --manifest PATH --vault ROOT. Schema and boundaries are documented in
System/skills/capture-acceptance.md. A mechanical PASS never establishes semantic
coverage, classification, source truth, authorization or independent review.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote


class Invalid(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise Invalid(label + ' must be nonempty text')
    return value


def hash_value(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise Invalid('Expected a lowercase SHA-256')
    return value


def inspect_capture(vault, manifest):
    root = Path(vault).resolve(strict=True)
    checks, seen = [], {}
    result = {'schema_version': 1, 'mechanical_verdict': 'BLOCKED',
              'process': {'read_only': True, 'status': 'SUCCESS'}, 'checks': checks,
              'limits': ['UNVERIFIED: semantic completeness and appropriate PARA classification',
                         'UNVERIFIED: source truth, topic relevance and actual authorization',
                         'UNVERIFIED: completeness of caller-supplied pre-state and coverage inventory',
                         'UNVERIFIED: independent review and actual Home inventory correctness']}

    def path(name):
        text(name, 'path')
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or str(p) != name or '\\' in name or any(ord(c) < 32 for c in name):
            raise Invalid('Use canonical vault-relative paths: ' + name)
        full = root / name
        if not full.resolve().is_relative_to(root):
            raise Invalid('Path escapes vault: ' + name)
        for item in (full, *full.parents):
            if item == root:
                break
            if item.is_symlink():
                raise Invalid('Symlinks require manual review: ' + name)
        return full

    def read(name):
        p = path(name)
        if not p.is_file():
            raise Invalid('Required file missing: ' + name)
        data = p.read_bytes()
        if name in seen and seen[name] != data:
            raise Invalid('Input changed during inspection: ' + name)
        seen[name] = data
        return data

    def note(name):
        name = text(name, 'note path')
        if not name.startswith(('01-projects/', '02-areas/', '03-resources/', '04-archive/projects/', '04-archive/areas/', '04-archive/resources/')):
            raise Invalid('Substance must use a PARA bucket: ' + name)
        return read(name).decode('utf-8')

    def check(name, operation):
        try:
            checks.append({'id': name, 'verdict': 'PASS', 'evidence': operation()})
        except (Invalid, OSError, UnicodeError, TypeError, KeyError, ValueError) as exc:
            checks.append({'id': name, 'verdict': 'REVISE' if isinstance(exc, Invalid) else 'BLOCKED', 'evidence': str(exc)})

    try:
        if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
            raise Invalid('Expected schema_version 1 object')
        if not isinstance(manifest.get('capture'), dict) or not isinstance(manifest.get('home'), dict):
            raise Invalid('capture and home must be objects')
        for key in ('ideas', 'coverage', 'preserved_files', 'existing_notes', 'indexes'):
            if not isinstance(manifest.get(key), list) or any(not isinstance(item, dict) for item in manifest[key]):
                raise Invalid(key + ' must be a list of objects')
        if not isinstance(manifest['home'].get('before_text'), str) or not isinstance(manifest['home'].get('expected_links'), list):
            raise Invalid('Home requires before_text and expected_links list')
        capture = manifest['capture']
        original = text(capture['original_path'], 'original_path')
        if not original.startswith('00-raw/'):
            raise Invalid('Original must be under 00-raw')
        path(original)
        original_hash = hash_value(capture['sha256'])
        state = capture['state']
        if state not in ('archived', 'task', 'unreadable', 'unresolved'):
            raise Invalid('Unsupported capture state')
        ideas = manifest['ideas']
        expected = manifest['expected_coverage']
        coverage = manifest['coverage']
        if not isinstance(ideas, list) or not ideas or not isinstance(expected, list) or not isinstance(coverage, list):
            raise Invalid('ideas must be nonempty; coverage inventories must be lists')
        ids = [text(i['id'], 'idea id') for i in ideas]
        if len(set(ids)) != len(ids):
            raise Invalid('Duplicate idea ID')
    except (Invalid, KeyError, TypeError) as exc:
        result['process']['status'] = 'BLOCKED'
        checks.append({'id': 'manifest', 'verdict': 'BLOCKED', 'evidence': str(exc)})
        return result

    def raw_check():
        if state == 'archived':
            destination = text(capture['archive_path'], 'archive_path')
            if not destination.startswith('04-archive/raw/'):
                raise Invalid('Original archive destination must be 04-archive/raw')
            if path(original).exists():
                raise Invalid('Archived original still exists in inbox')
            previous = capture['archive_before']
            if not isinstance(previous, dict):
                raise Invalid('archive_before must map every existing raw-archive path to its pre-move hash')
            if destination in previous:
                raise Invalid('Archive destination existed before the move; choose a collision-safe sibling')
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-.+', PurePosixPath(destination).name):
                raise Invalid('Archive filename requires date prefix')
            for name, old_hash in previous.items():
                if not name.startswith('04-archive/raw/') or digest(read(name)) != hash_value(old_hash):
                    raise Invalid('Existing sealed archive changed: ' + name)
            current_paths = {str(p.relative_to(root)) for p in (root/'04-archive/raw').rglob('*') if p.is_file()}
            if current_paths != set(previous) | {destination}:
                raise Invalid('Archive inventory differs from the declared single capture move')
            data = read(destination)
        else:
            text(capture.get('reason'), 'unresolved capture reason')
            destination = original
            data = read(original)
            if capture.get('archive_path'):
                raise Invalid('Unresolved/task/unreadable capture must remain in 00-raw')
        if digest(data) != original_hash:
            raise Invalid('Original bytes changed, including metadata; raw tagging is forbidden')
        return {'state': state, 'path': destination, 'sha256': digest(data)}
    check('raw_preservation_and_collision', raw_check)

    def idea_check():
        destinations = []
        for idea in ideas:
            status = idea['state']
            if status == 'filed':
                if not isinstance(idea.get('destinations'), list) or not idea['destinations']:
                    raise Invalid('Filed idea requires destinations')
                for destination in idea['destinations']:
                    note(destination)
                    destinations.append(destination)
            elif status in ('skipped', 'flagged'):
                text(idea.get('reason'), 'skip/flag reason')
                if idea.get('destinations'):
                    raise Invalid('Skipped/flagged ideas must not claim filed destinations')
                if status == 'flagged' and state == 'archived':
                    raise Invalid('Flagged task/idea prevents archiving the original')
            else:
                raise Invalid('Every idea must be filed, skipped or flagged')
        if state in ('task', 'unreadable', 'unresolved') and not any(i['state'] == 'flagged' for i in ideas):
            raise Invalid('Retained capture needs an explicitly flagged idea')
        return {'ideas': len(ideas), 'destinations': destinations}
    check('idea_dispositions', idea_check)

    def coverage_check():
        if any(not isinstance(x, str) or not x.strip() for x in expected) or len(expected) != len(set(expected)):
            raise Invalid('Coverage IDs must be distinct nonempty strings')
        actual = [text(c['id'], 'coverage id') for c in coverage]
        if len(actual) != len(set(actual)) or set(actual) != set(expected):
            raise Invalid('Every declared section/example/table-column coverage unit must occur exactly once')
        by_id = {i['id']: i for i in ideas}
        filed = {i['id'] for i in ideas if i['state'] == 'filed'}
        if not filed.issubset({c['idea_id'] for c in coverage}):
            raise Invalid('Every filed idea needs at least one declared coverage unit')
        for item in coverage:
            idea = by_id[item['idea_id']]
            if idea['state'] != 'filed' or item['destination'] not in idea['destinations']:
                raise Invalid('Coverage destination does not belong to the filed idea')
            if item.get('kind') not in ('text', 'table_column'):
                raise Invalid('Coverage kind must be text or table_column')
            fragment = text(item['evidence_text'], 'literal coverage evidence')
            if fragment not in note(item['destination']):
                raise Invalid('Declared coverage evidence missing: ' + item['id'])
        return {'covered_declared_units': actual, 'inventory_completeness': 'UNVERIFIED'}
    check('declared_coverage', coverage_check)

    def preserve_check():
        for item in manifest['preserved_files']:
            if digest(read(item['path'])) != hash_value(item['sha256']):
                raise Invalid('Preserved file changed: ' + item['path'])
        for item in manifest['existing_notes']:
            old = text(item['before_text'], 'existing-note before text')
            if digest(old.encode('utf-8')) != hash_value(item['before_sha256']):
                raise Invalid('Existing-note before text does not match pre-state hash')
            if old not in note(item['path']):
                raise Invalid('Prior note content not retained contiguously; inspect merge manually: ' + item['path'])
        return {'unchanged_files': len(manifest['preserved_files']), 'append_style_merges': len(manifest['existing_notes'])}
    check('existing_material', preserve_check)

    def indexes_check():
        for item in manifest['indexes']:
            if not text(item['path'], 'index path').startswith('00-wiki/'):
                raise Invalid('Topic index must be in 00-wiki')
            qualified = item['qualifying_notes']
            if len(set(qualified)) < 2:
                raise Invalid('A topic index needs two distinct related notes; relation remains semantic')
            index = read(item['path']).decode('utf-8')
            links = {x.split('|')[0].split('#')[0] for x in re.findall(r'\[\[([^\]]+)\]\]', index)}
            for target in qualified:
                note(target)
                if target.removesuffix('.md') not in links and target not in links:
                    raise Invalid('Qualifying note missing from topic index: ' + target)
        return {'indexes': len(manifest['indexes']), 'index_only_semantics': 'UNVERIFIED'}
    check('qualifying_indexes', indexes_check)

    def home_check():
        home = manifest['home']
        old = home['before_text']
        if digest(old.encode('utf-8')) != hash_value(home['before_sha256']):
            raise Invalid('Home pre-state text/hash mismatch')
        new = read('Home.md').decode('utf-8')
        start, end = text(home['generated_start'], 'Home start marker'), text(home['generated_end'], 'Home end marker')
        def split(value):
            if value.count(start) != 1 or value.count(end) != 1:
                raise Invalid('Home generated boundaries must occur once')
            a, b = value.index(start)+len(start), value.index(end)
            if a >= b:
                raise Invalid('Reversed Home boundaries')
            return value[:a], value[a:b], value[b:]
        before_parts, after_parts = split(old), split(new)
        if before_parts[0] != after_parts[0] or before_parts[2] != after_parts[2]:
            raise Invalid('Home manual material or boundaries changed')
        if home.get('refresh_checked') is not True:
            raise Invalid('Librarian must explicitly confirm Home inventory refresh review')
        links = {unquote(x.split('#')[0]) for x in re.findall(r'\[[^\]]*\]\(([^)]+)\)', after_parts[1])}
        for target in home['expected_links']:
            path(target)
            if not path(target).exists() or target not in links:
                raise Invalid('Expected Home link missing/unavailable: ' + target)
        return {'manual_material_unchanged': True, 'expected_links': home['expected_links'], 'inventory_accuracy': 'UNVERIFIED'}
    check('home_boundaries_and_declared_links', home_check)
    check('snapshot_consistency', lambda: {'files': len(seen)} if all(path(p).read_bytes() == data for p, data in seen.items()) else (_ for _ in ()).throw(Invalid('Inspected input changed during check')))
    result['inspected'] = {p: digest(data) for p, data in sorted(seen.items())}
    verdicts = {x['verdict'] for x in checks}
    result['mechanical_verdict'] = 'BLOCKED' if 'BLOCKED' in verdicts else 'REVISE' if 'REVISE' in verdicts else 'PASS'
    if 'BLOCKED' in verdicts:
        result['process']['status'] = 'BLOCKED'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault', required=True)
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args(argv)
    try:
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise Invalid('Duplicate JSON key: '+key)
                result[key] = value
            return result
        manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'), object_pairs_hook=unique)
        result = inspect_capture(args.vault, manifest)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'mechanical_verdict': 'BLOCKED', 'process': {'read_only': True, 'status': 'BLOCKED'}, 'error': str(exc)}
    print(json.dumps(result, indent=2))
    return {'PASS': 0, 'REVISE': 1, 'BLOCKED': 2}[result['mechanical_verdict']]


if __name__ == '__main__':
    sys.exit(main())
