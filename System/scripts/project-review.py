#!/usr/bin/env python3
"""Read-only version-bound review and continuation advice for canonical project tasks."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
_spec = importlib.util.spec_from_file_location('project_tasks', Path(__file__).with_name('project-tasks.py'))
_tasks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tasks)
START, END = '<!-- para-review:start -->', '<!-- para-review:end -->'
ROLES = ('worker', 'checker', 'librarian')


def fingerprint(task):
    """Checkbox changes report progress; wording and prerequisites change the contract."""
    value = {key: task[key] for key in ('id', 'title', 'after')}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def metadata(text):
    if START not in text and END not in text:
        return None
    body = _tasks.block(text, START, END).strip()
    if not body.startswith('```json\n') or not body.endswith('\n```'):
        raise ValueError('Review block must contain one fenced JSON object.')
    # Metadata stays adjacent, outside the existing UI-managed blocks.
    bounds = (text.index(START), text.index(END) + len(END))
    for a, b in ((_tasks.TASK_START, _tasks.TASK_END), (_tasks.STATE_START, _tasks.STATE_END)):
        if max(bounds[0], text.index(a)) < min(bounds[1], text.index(b) + len(b)):
            raise ValueError('Review block overlaps a task/state block.')
    value = json.loads(body[8:-4], object_pairs_hook=_pairs)
    if not isinstance(value, dict) or value.get('schema_version') != 1:
        raise ValueError('Review metadata needs schema_version 1.')
    return value


def strings(value):
    return isinstance(value, list) and bool(value) and all(isinstance(x, str) and x.strip() for x in value)


def manifest(root, project, value, required=False):
    if not isinstance(value, dict) or (required and not value):
        return ['missing output manifest' if required else 'missing input manifest']
    errors = []
    for name, expected in value.items():
        if not isinstance(name, str) or not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            errors.append('invalid manifest entry')
            continue
        path = root / name
        if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root):
            errors.append('manifest path outside vault: ' + name)
        elif path.resolve() == project:
            errors.append('project note cannot hash itself: ' + name)
        elif not path.is_file():
            errors.append('missing file: ' + name)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append('changed file: ' + name)
    return errors


def evaluate(root, project):
    root = Path(root).resolve()
    project = root / project
    if project not in _tasks.Store(root).candidates():
        raise ValueError('Use a vault-owned canonical project note; nested implementation roots and archive paths are excluded.')
    text = project.read_text()
    _tasks.validate_blocks(text)
    tasks = _tasks.read_tasks(text)
    meta = metadata(text)
    rows = {t['id']: {'id': t['id'], 'reported_done': t['done'], 'definition_sha256': fingerprint(t),
                      'accepted': False, 'action': None, 'issues': []} for t in tasks}
    if meta is None:
        return {'mode': 'legacy-untracked', 'tasks': list(rows.values()), 'eligible': [],
                'stop_allowed': False, 'project_complete': False,
                'remaining': ['Librarian: inspect existing evidence and authority; adopt optional receipts deliberately.']}
    ids = set(rows)
    authorized = meta.get('authorized_tasks', [])
    receipts = meta.get('tasks', {})
    permissions = meta.get('permission_scope', {})
    if (not isinstance(authorized, list) or len(authorized) != len(set(authorized))
            or not set(authorized) <= ids or not isinstance(receipts, dict) or not set(receipts) <= ids
            or not isinstance(permissions, dict) or not set(permissions) <= ids):
        raise ValueError('Authority and receipt keys must reference unique canonical task IDs.')
    if authorized and not isinstance(meta.get('approval_reference'), str):
        raise ValueError('Authorized tasks need an actual approval_reference.')
    if authorized and not meta['approval_reference'].strip():
        raise ValueError('Authorized tasks need an actual approval_reference.')
    for tid in authorized:
        if not strings(permissions.get(tid)):
            raise ValueError('Authorized task needs explicit permission_scope: ' + tid)
    by_id = {t['id']: t for t in tasks}
    eligible = []

    def visit(tid):
        row, task = rows[tid], by_id[tid]
        if row['action'] is not None:
            return
        for dep in task['after']:
            visit(dep)
        if any(not rows[dep]['accepted'] for dep in task['after']):
            row['action'] = 'wait_for_dependencies'
            row['issues'] = ['unaccepted prerequisite: ' + dep for dep in task['after'] if not rows[dep]['accepted']]
            return
        if tid not in authorized:
            row['action'] = 'needs_authority'
            return
        receipt = receipts.get(tid)
        if not isinstance(receipt, dict):
            row['action'] = 'review_reported_completion' if task['done'] else 'execute'
        else:
            binding = {key: receipt.get(key) for key in ('definition_sha256', 'inputs', 'outputs')}
            stale = []
            if binding['definition_sha256'] != row['definition_sha256']:
                stale.append('changed task definition')
            stale += manifest(root, project, binding['inputs'])
            stale += manifest(root, project, binding['outputs'])
            mode = receipt.get('review_mode', 'independent')
            if mode not in ('independent', 'sequential'):
                raise ValueError('Unknown review_mode for ' + tid)
            row['review_mode'] = mode
            row['independent'] = mode == 'independent'
            if mode == 'sequential' and (receipt.get('sequential_opt_in') is not True
                                        or receipt.get('requires_independence', False)):
                stale.append('sequential fallback not permitted for this task')
            if stale:
                row['action'], row['issues'] = 'repair', stale
            else:
                actors = []
                for role in ROLES:
                    review = receipt.get(role)
                    if not isinstance(review, dict):
                        row['action'] = 'review_' + role
                        break
                    same = all(review.get(key) == val for key, val in binding.items())
                    actor = review.get('actor')
                    if (not same or not isinstance(actor, str) or not actor.strip()
                            or not strings(review.get('checks')) or not strings(review.get('evidence'))):
                        row['action'], row['issues'] = 'review_' + role, ['incomplete or stale ' + role + ' review']
                        break
                    if mode == 'independent' and actor.strip().casefold() in actors:
                        row['action'], row['issues'] = 'review_' + role, ['independent roles need distinct actors']
                        break
                    actors.append(actor.strip().casefold())
                    verdict = review.get('verdict')
                    if verdict == 'BLOCKED':
                        blocker = review.get('blocker')
                        if (isinstance(blocker, dict) and all(isinstance(blocker.get(k), str) and blocker[k].strip()
                                                             for k in ('reason', 'next_action'))
                                and strings(blocker.get('evidence'))):
                            row['action'], row['issues'] = 'blocked', [blocker]
                        else:
                            row['action'], row['issues'] = 'review_' + role, ['BLOCKED needs exact reason, next_action and evidence']
                        break
                    if verdict != 'PASS':
                        row['action'], row['issues'] = ('repair' if verdict == 'REVISE' else 'review_' + role), [role + ' has not passed']
                        break
                    if not binding['outputs']:
                        row['action'], row['issues'] = 'repair', ['PASS needs a real output manifest']
                        break
                    if role == 'librarian' and review.get('confirmed_output') is not True:
                        row['action'], row['issues'] = 'review_librarian', ['Librarian must inspect actual output']
                        break
                if row['action'] is None:
                    row['accepted'] = task['done']
                    row['action'] = 'accepted' if task['done'] else 'reconcile_progress'
        if row['action'] not in ('accepted', 'blocked', 'wait_for_dependencies', 'needs_authority'):
            eligible.append({'id': tid, 'action': row['action'], 'permission_scope': permissions[tid]})

    for task in tasks:
        visit(task['id'])
    all_accepted = all(row['accepted'] for row in rows.values())
    state = _tasks.block(text, _tasks.STATE_START, _tasks.STATE_END)
    confirmed = re.search(r'^\*\*Finish line confirmed:\*\* yes\s*$', state, re.M) is not None
    pending = re.search(r'^\*\*Librarian review:\*\* pending\b', text, re.M) is not None
    if pending:
        eligible.append({'action': 'librarian_followthrough', 'project': str(project.relative_to(root)),
                         'permission_scope': ['existing authorized contextual follow-through only']})
    remaining = [dict(id=r['id'], action=r['action'], issues=r['issues']) for r in rows.values() if not r['accepted']]
    return {'mode': 'review-tracked', 'tasks': list(rows.values()), 'eligible': eligible,
            'stop_allowed': not eligible, 'project_complete': all_accepted and confirmed and not pending,
            'pending_librarian_followthrough': pending,
            'recorded_status': _tasks.status_of(text),
            'finish_line': 'confirmed' if confirmed else 'requires_explicit_user_confirmation',
            'remaining': remaining, 'scope_accepted': all(rows[t]['accepted'] for t in authorized) if authorized else False,
            'limit': 'Snapshot evidence and recorded authority require Librarian judgment; no task text is executed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--project', required=True)
    parser.add_argument('--assert-stop', action='store_true', help='exit 1 while authorized work or review can proceed')
    args = parser.parse_args()
    try:
        result = evaluate(args.vault, args.project)
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({'error': str(error), 'stop_allowed': False}))
        return 2
    print(json.dumps(result, indent=2))
    return 1 if args.assert_stop and not result['stop_allowed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
