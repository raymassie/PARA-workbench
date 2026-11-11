#!/usr/bin/env python3
"""Local task UI backed by canonical PARA project Markdown, no external services."""
import argparse
import datetime as dt
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import tempfile
from urllib.parse import quote, urlparse
import uuid
import webbrowser
from vault_lock import vault_write_lock

TASK_START, TASK_END = '<!-- para-tasks:start -->', '<!-- para-tasks:end -->'
STATE_START, STATE_END = '<!-- para-project-state:start -->', '<!-- para-project-state:end -->'
TASK_RE = re.compile(r'^- \[([ xX])\] (.+?) <!-- task:([a-z0-9-]+)(?: after:([a-z0-9,-]+))? -->$')
SKILL_START, SKILL_END = '<!-- para-skills:start -->', '<!-- para-skills:end -->'
CATALOG = {
    'researcher': ('Researcher', r'\b(research|investigate|fact.check|verify claims|compare (?:vendors|products|competitors)|evidence)\b', 'Answer bounded questions or verify evidence.', 'Before decisions or claims that need evidence.'),
    'strategist': ('Strategist', r'\b(strategy|strategic|positioning|trade.?offs|target audience|market position|choose a direction)\b', 'Resolve direction, audience, and material tradeoffs.', 'Before downstream work depends on unresolved direction.'),
    'content-strategist': ('Content strategist', r'\b(ongoing (?:content|publishing)|editorial (?:calendar|program)|content (?:plan|calendar|strategy)|publish(?:ing)? (?:weekly|monthly)|weekly newsletter)\b', 'Plan a sustainable ongoing publishing program.', 'Before committing to formats and cadence.'),
    'copywriter': ('Copywriter', r'\b(copywriting|copy|draft|write|writing|article|newsletter|email|headlines?)\b', 'Draft a concrete written asset from its brief.', 'When the audience, purpose, and necessary proof are known.'),
    'designer': ('Designer', r'\b(design|redesign|visual|branding|layout|wireframes?|typography|user experience|interface)\b', 'Set or review visual and interaction direction.', 'When a visual or interaction decision is needed.'),
    'dev': ('Dev', r'\b(code|coding|software|implement|programming|app|website|web app|bug|debug|api|database|integration|form|authentication)\b', 'Implement or fix software in its own repository.', 'When required behavior and authorized write paths are clear.'),
    'editor': ('Editor', r'\b(proofread|edit (?:copy|text|article|draft)|editorial review)\b', 'Review a draft for truth, provenance, clarity, and voice.', 'After a concrete draft exists, before release readiness.'),
    'pm': ('PM', r'\b(dependencies|milestones|workstreams|coordinate|coordination|multi.phase)\b', 'Coordinate genuine dependencies and project state.', 'When several dependent deliverables need coordination.'),
}

def recommend_skills(payload):
    parts = [payload.get('name', ''), payload.get('goal', '')]
    actions = payload.get('tasks', [])
    if not all(isinstance(p, str) for p in parts) or not isinstance(actions, list) or not all(isinstance(p, str) for p in actions):
        raise ValueError('Describe the project and its actions as text.')
    text = '\n'.join(parts + actions).lower()
    selected = {name for name, (_, pattern, _, _) in CATALOG.items() if re.search(pattern, text)}
    if 'copywriter' in selected:
        selected.add('editor')
    if len(selected - {'pm', 'editor'}) >= 3:
        selected.add('pm')
    return [{'id': name, 'name': label, 'reason': reason, 'when': when,
             'path': f'skills/{name}/SKILL.md'}
            for name, (label, _, reason, when) in CATALOG.items() if name in selected]

def intake_dates(payload):
    values = {}
    for key, label in (('started', 'start date'), ('due', 'end date')):
        raw = payload.get(key)
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f'Choose the {label}, or explicitly mark it undecided.')
        raw = raw.strip()
        if raw != 'undecided':
            try:
                parsed = dt.date.fromisoformat(raw)
                if parsed.isoformat() != raw:
                    raise ValueError()
            except ValueError:
                raise ValueError(f'The {label} must be YYYY-MM-DD or undecided.') from None
        values[key] = raw
    kind = payload.get('date_type')
    if kind not in ('deadline', 'target', 'undecided') or (kind == 'undecided') != (values['due'] == 'undecided'):
        raise ValueError('Identify the end date as a firm deadline, a target, or undecided.')
    if values['started'] != 'undecided' and values['due'] != 'undecided' and values['due'] < values['started']:
        raise ValueError('The end date cannot precede the start date.')
    return {**values, 'date_type': kind}

def render_skill_plan(payload):
    rows = recommend_skills(payload)
    if not rows:
        return '**Selection:** Librarian only for now; no specialist is indicated by the brief. Reassess when scope changes.'
    return ('**Selection:** initial suggestions from the project brief; the Librarian reviews applicability before dispatch.\n\n'
            + '\n'.join(f'- [[{r["path"][:-3]}|{r["name"]}]] — {r["reason"]} Invoke: {r["when"]}' for r in rows))

class Conflict(ValueError):
    pass

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def block(text, start, end):
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('The project needs exactly one managed task/state block; ask the Librarian to repair it.')
    a, b = text.index(start), text.index(end)
    if a >= b:
        raise ValueError('Task/state block boundaries are reversed.')
    return text[a + len(start):b]

def replace_block(text, start, end, body):
    block(text, start, end)
    a, b = text.index(start) + len(start), text.index(end)
    return text[:a] + '\n' + body.strip() + '\n' + text[b:]

def validate_blocks(text):
    block(text, TASK_START, TASK_END)
    block(text, STATE_START, STATE_END)
    tasks = (text.index(TASK_START), text.index(TASK_END) + len(TASK_END))
    state = (text.index(STATE_START), text.index(STATE_END) + len(STATE_END))
    if max(tasks[0], state[0]) < min(tasks[1], state[1]):
        raise ValueError('Task and state blocks must be separate, without nesting or overlap.')

def read_tasks(text):
    content = block(text, TASK_START, TASK_END)
    tasks = []
    for line in content.splitlines():
        if not line.strip():
            continue
        match = TASK_RE.fullmatch(line)
        if not match:
            raise ValueError('Use one checkbox per task with a stable task ID; see prompts/project-update.md.')
        checked, title, task_id, after = match.groups()
        tasks.append({'id': task_id, 'title': title, 'done': checked.lower() == 'x',
                      'after': after.split(',') if after else []})
    ids = {t['id'] for t in tasks}
    if not tasks or len(ids) != len(tasks):
        raise ValueError('A project needs at least one task, with unique IDs.')
    if any(not set(t['after']) <= ids for t in tasks):
        raise ValueError('A task dependency does not exist in this project.')
    by_id = {t['id']: t for t in tasks}
    visited = set()
    def visit(task_id, trail):
        if task_id in trail:
            raise ValueError('Task dependencies contain a cycle.')
        if task_id in visited:
            return
        for dep in by_id[task_id]['after']:
            visit(dep, trail | {task_id})
        visited.add(task_id)
    for task_id in ids:
        visit(task_id, set())
    return tasks

def status_of(text):
    if text.startswith('---\n'):
        front = text.split('\n---\n', 1)[0]
        match = re.search(r'^status: *(.+)$', front, re.M)
    else:
        match = re.search(r'^\*\*Status:\*\* *(.+)$', text, re.M)
    if not match:
        raise ValueError('Project status field is missing; ask the Librarian to repair the note.')
    return match.group(1).strip().strip('"\'')

def set_status(text, status):
    if text.startswith('---\n'):
        front, rest = text.split('\n---\n', 1)
        front, n = re.subn(r'^status: *[^\n]*$', 'status: ' + status, front, count=1, flags=re.M)
        result = front + '\n---\n' + rest
    else:
        result, n = re.subn(r'^\*\*Status:\*\* *[^\n]*$', '**Status:** ' + status, text, count=1, flags=re.M)
    if n != 1:
        raise ValueError('Project status could not be updated safely.')
    return result

class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def confined(self, path):
        if not path.is_relative_to(self.root) or not path.resolve().is_relative_to(self.root):
            raise ValueError('Refusing a path outside the vault.')
        while path != self.root:
            if path.is_symlink():
                raise ValueError('Refusing a write through a symlink.')
            path = path.parent

    def candidates(self):
        folder = self.root/'01-projects'
        if not folder.is_dir():
            return []
        paths = [p for p in folder.glob('*.md') if p.name != 'README.md']
        paths += [p/'README.md' for p in folder.iterdir() if p.is_dir() and (p/'README.md').is_file()]
        result = []
        for path in paths:
            # Ignore project-owned mixed roots and symlinks; never traverse implementation trees.
            if any(p.is_symlink() for p in (path, *path.parents) if p != self.root.parent):
                continue
            if path.parent != folder and (path.parent/'.git').exists():
                continue
            if path.resolve().is_relative_to(self.root):
                result.append(path)
        return sorted(result)

    def view(self, path, text=None):
        text = path.read_text() if text is None else text
        title = re.search(r'^# (.+)$', text, re.M)
        result = {'path': str(path.relative_to(self.root)), 'name': title.group(1) if title else path.stem,
                  'version': digest(text), 'status': 'unknown', 'tasks': [], 'error': None}
        goal = re.search(r'^goal: *([^\n]+)$', text, re.M) or re.search(r'^\*\*Goal:\*\* *([^\n]+)$', text, re.M)
        value = goal.group(1).strip() if goal else 'Read the project note for its finish line.'
        try:
            result['goal'] = json.loads(value) if value.startswith('"') else value.strip("'")
        except ValueError:
            result['goal'] = value
        for key, label in (('started', 'Started'), ('due', 'Due'), ('date_type', 'End date type')):
            field = re.search(rf'^{key}: *([^\n]+)$', text, re.M) or re.search(rf'^\*\*{label}:\*\* *([^\n]+)$', text, re.M)
            result[key] = field.group(1).strip().strip('"\'') if field else 'not recorded'
        result['skills'] = []
        if SKILL_START in text and SKILL_END in text:
            try:
                for line in block(text, SKILL_START, SKILL_END).splitlines():
                    entry = re.match(r'- \[\[([^|]+)\|([^\]]+)\]\] — (.+)', line)
                    if entry:
                        result['skills'].append({'name': entry.group(2), 'note': entry.group(3)})
            except ValueError:
                pass  # Legacy/manual skill notes remain untouched by task updates.
        try:
            result['status'] = status_of(text)
        except ValueError as exc:
            result['error'] = str(exc)
        try:
            validate_blocks(text)
            result['tasks'] = read_tasks(text)
            result['summary'] = block(text, STATE_START, STATE_END).strip()
            result['confirmed'] = '**Finish line confirmed:** yes' in result['summary']
        except ValueError as exc:
            result['error'] = result['error'] or str(exc)
        return result

    def listing(self):
        return [self.view(path) for path in self.candidates()]

    def home(self, current, paths, replacements):
        # Replace only the generated Projects line, preserving comments/other buckets/Topics.
        start = current.find('## Status\n')
        if start < 0:
            raise ValueError('Home is missing its Status section.')
        end = current.find('\n## ', start + 3)
        end = len(current) if end < 0 else end
        section = current[start:end]
        entries = []
        inventory = set(paths)
        folder = self.root/'01-projects'
        for child in folder.iterdir():
            if child.is_dir():
                readme = child/'README.md'
                if not child.is_symlink() and not readme.is_symlink() and readme.is_file():
                    inventory.add(readme)  # read status even in an independent repo; no writes granted
                else:
                    label = child.name.replace('[', '').replace(']', '')
                    url = quote(str(child.relative_to(self.root))+'/', safe='/')
                    entries.append(f'[{label}]({url}) — unknown')
        for path in sorted(inventory):
            info = self.view(path, replacements.get(path))
            label = info['name'].replace('[', '').replace(']', '').replace('\n', ' ')
            url = quote(info['path'], safe='/')
            state = info['status']
            entries.append(f'[{label}]({url}) — {state}')
        line = '- **Projects:** ' + ('; '.join(entries) if entries else 'No active projects.')
        updated, count = re.subn(r'^- \*\*Projects:\*\*[^\n]*$', lambda m: line, section, flags=re.M)
        if count != 1:
            raise ValueError('Home needs one generated Projects line; no files were changed.')
        return current[:start] + updated + current[end:]

    def publish(self, changes, expected):
        # Recoverable before/after journal; no git mutation, no source-tree edits.
        folder = self.root/'logs/project-tasks'
        self.confined(folder)
        folder.mkdir(parents=True, exist_ok=True)
        pending = list(folder.glob('*.pending.json'))
        if pending:
            raise Conflict('A previous write needs recovery; inspect ' + str(pending[0]))
        entries = []
        for path, new in changes.items():
            self.confined(path)
            old = expected[path]
            if (path.read_text() if path.exists() else None) != old:
                raise Conflict('Another editor changed ' + str(path.relative_to(self.root)) + '; reload before updating.')
            entries.append({'path': str(path.relative_to(self.root)), 'before': old, 'after': new})
        journal = folder/(uuid.uuid4().hex + '.pending.json')
        journal.write_text(json.dumps(entries, indent=2))
        written = []
        try:
            for entry in entries:
                path = self.root/entry['path']
                actual = path.read_text() if path.exists() else None
                if actual != entry['before']:
                    raise Conflict('Another editor changed ' + entry['path'] + '; reload before updating.')
                self.atomic(path, entry['after'], create=entry['before'] is None)
                written.append(entry)
        except Exception:
            clean = True
            for entry in reversed(written):
                path = self.root/entry['path']
                if path.read_text() != entry['after']:
                    clean = False
                    continue
                if entry['before'] is None:
                    path.unlink()
                else:
                    self.atomic(path, entry['before'])
            if clean:
                journal.rename(journal.with_suffix('.rolled-back'))
            raise
        journal.rename(journal.with_suffix('.completed'))

    @staticmethod
    def atomic(path, text, create=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        name = None
        try:
            with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False, encoding='utf-8') as stream:
                name = stream.name
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            if path.exists():
                os.chmod(name, path.stat().st_mode & 0o777)
            if create:
                os.link(name, path)  # refuses overwrite if a concurrent create won
            else:
                os.replace(name, path)
                name = None
        finally:
            if name:
                Path(name).unlink(missing_ok=True)

    def apply(self, payload, create=False):
        lock_dir = self.root/'logs/project-tasks'
        self.confined(lock_dir)
        lock_dir.mkdir(parents=True, exist_ok=True)
        with vault_write_lock(self.root):
            if create:
                if not isinstance(payload.get('name'), str) or not isinstance(payload.get('goal'), str):
                    raise ValueError('Project name and finish line must be text.')
                title, goal = payload.get('name', '').strip(), payload.get('goal', '').strip()
                task_titles = payload.get('tasks', [])
                if not title or not goal or '\n' in title or len(title) > 150 or not isinstance(task_titles, list):
                    raise ValueError('Enter a project name, a concrete finish line, and actionable tasks.')
                if not task_titles or len(task_titles) > 200 or any(not isinstance(t, str) or not t.strip() or '\n' in t or '<!--' in t for t in task_titles):
                    raise ValueError('Enter 1–200 nonempty, single-line actions.')
                dates = intake_dates(payload)
                slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'project'
                path = self.root/'01-projects'/(slug+'.md')
                if path.exists() or (path.parent/slug).exists():
                    raise Conflict('A project with that filename already exists; choose it from the list.')
                template = (self.root/'templates/project-note.md').read_text()
                validate_blocks(template)
                tokens = {'<Project Name>': title, '<start date>': dates['started'],
                          '<end date>': dates['due'], '<end date type>': dates['date_type'],
                          'goal: <what "done" looks like>': 'goal: ' + json.dumps(goal)}
                token_re = re.compile('|'.join(re.escape(key) for key in tokens))
                scaffold = replace_block(template, TASK_START, TASK_END, 'TASKS')
                scaffold = replace_block(scaffold, STATE_START, STATE_END, 'STATE')
                scaffold = replace_block(scaffold, SKILL_START, SKILL_END, 'SKILLS')
                if re.search(r'<(?![!])[^>]+>', token_re.sub('VALUE', scaffold)):
                    raise ValueError('The project template has custom placeholders. Ask the Librarian to fill them before creating this project.')
                text = token_re.sub(lambda match: tokens[match.group(0)], template)
                text = replace_block(text, TASK_START, TASK_END, '\n'.join(
                    f'- [ ] {action.strip()} <!-- task:t{i+1} -->' for i, action in enumerate(task_titles)))
                text = replace_block(text, STATE_START, STATE_END, '**Finish line confirmed:** no')
                text = replace_block(text, SKILL_START, SKILL_END, render_skill_plan(payload))
                tasks = read_tasks(text)
                states = {t['id']: False for t in tasks}
                original_project = None
            else:
                path = self.root/str(payload.get('path', ''))
                if path not in self.candidates():
                    raise ValueError('Choose a live, Brain-owned project note.')
                text = path.read_text()
                original_project = text
                validate_blocks(text)
                if payload.get('version') != digest(text):
                    raise Conflict('This project changed in another editor. Reload it before updating; your changes were not applied.')
                tasks = read_tasks(text)
                states = payload.get('states')
                if not isinstance(states, dict) or set(states) != {t['id'] for t in tasks} or any(type(v) is not bool for v in states.values()):
                    raise ValueError('Submit one checkbox state for each task.')
                if status_of(text) not in ('active', 'blocked', 'ready-for-review', 'done'):
                    raise ValueError('This project has a custom/paused status. Ask the Librarian to reconcile it before updating tasks.')
                extra = payload.get('new_tasks', [])
                if not isinstance(extra, list) or len(tasks) + len(extra) > 200 or any(not isinstance(t, str) or not t.strip() or '\n' in t or '<!--' in t for t in extra):
                    raise ValueError('New actions must be nonempty single lines; maximum 200 tasks.')
                for title in extra:
                    task_id = 't-' + uuid.uuid4().hex[:12]
                    tasks.append({'id': task_id, 'title': title.strip(), 'done': False, 'after': []})
                    states[task_id] = False
            if any(states[t['id']] and any(not states[dep] for dep in t['after']) for t in tasks):
                raise ValueError('Complete prerequisites before checking dependent tasks.')
            confirmed = payload.get('confirmed', False)
            if type(confirmed) is not bool:
                raise ValueError('Completion confirmation must be a checkbox value.')
            done = sum(states.values())
            available = [t for t in tasks if not states[t['id']] and all(states[d] for d in t['after'])]
            if done < len(tasks):
                confirmed = False
            status = 'done' if confirmed else ('ready-for-review' if done == len(tasks) else ('active' if available else 'blocked'))
            lines = [f'- [{"x" if states[t["id"]] else " "}] {t["title"]} <!-- task:{t["id"]}'
                     + (f' after:{",".join(t["after"])}' if t['after'] else '') + ' -->' for t in tasks]
            text = replace_block(text, TASK_START, TASK_END, '\n'.join(lines))
            now = dt.datetime.now().astimezone().isoformat(timespec='seconds')
            next_action = '; '.join(t['title'] for t in available[:3]) if available else ('Confirm the project finish line.' if not confirmed else 'Project complete; archive only when requested.')
            summary = (f'**Progress:** {done}/{len(tasks)} tasks complete\n'
                       f'**Next available actions:** {next_action}\n'
                       f'**Finish line confirmed:** {"yes" if confirmed else "no"}\n'
                       f'**Librarian review:** pending — reconcile changed task outcomes and any linked-project or specialist follow-up.\n'
                       f'**Tasks updated:** {now}\n'
                       f'<!-- para-task-revision:{digest(json.dumps([(t["id"], t["title"], states[t["id"]], t["after"]) for t in tasks]))} -->\n')
            normalized = lambda s: re.sub(r'^\*\*(?:Tasks updated|Librarian review):\*\*[^\n]*\n?', '', s, flags=re.M).strip()
            if original_project:
                prior = block(original_project, STATE_START, STATE_END)
                prior_tasks = read_tasks(original_project)
                unchanged = not extra and all(t['done'] == states[t['id']] for t in prior_tasks)
                if unchanged and normalized(prior) == normalized(summary):
                    review = re.search(r'^\*\*Librarian review:\*\*[^\n]*$', prior, re.M)
                    if review:
                        summary = re.sub(r'^\*\*Librarian review:\*\*[^\n]*$', lambda m: review.group(0), summary, flags=re.M)
            text = replace_block(text, STATE_START, STATE_END, summary)
            text = set_status(text, status)
            validate_blocks(text)
            read_tasks(text)
            home, activity = self.root/'Home.md', self.root/'03-resources/vault-log.md'
            original_home, original_activity = home.read_text(), activity.read_text()
            paths = self.candidates()
            if path not in paths:
                paths.append(path)
            new_home = self.home(original_home, paths, {path: text})
            # No-op saves do not duplicate audit entries or churn dates.
            if not create:
                old = self.view(path)
                if not extra and all(t['done'] == states[t['id']] for t in old['tasks']) and old.get('confirmed', False) == confirmed and old['status'] == status and normalized(old['summary']) == normalized(summary) and new_home == original_home:
                    return {'project': old, 'message': 'Already up to date. No changes needed.'}
            entry = f'\n- {now} — project tasks {"created" if create else "updated"}: `{path.relative_to(self.root)}`; {done}/{len(tasks)} complete; status `{status}`; project summary and Home refreshed. Completion is user-reported, not an independent delivery check.\n'
            self.publish({path: text, home: new_home, activity: original_activity + entry},
                         {path: original_project, home: original_home, activity: original_activity})
            return {'project': self.view(path), 'message': 'Updated project status, next actions, Home, and activity log.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--open', action='store_true')
    args = parser.parse_args()
    store, token = Store(args.vault), secrets.token_urlsafe(32)
    origin = f'http://127.0.0.1:{args.port}'

    class Handler(BaseHTTPRequestHandler):
        def send(self, code, value, kind='application/json'):
            data = (json.dumps(value) if kind == 'application/json' else value).encode()
            self.send_response(code)
            self.send_header('Content-Type', kind + '; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def allowed_host(self):
            return self.headers.get('Host') == f'127.0.0.1:{args.port}'

        def do_GET(self):
            if not self.allowed_host():
                return self.send(403, {'error': 'Open the 127.0.0.1 address printed by the launcher.'})
            route = urlparse(self.path).path
            if route == '/':
                html = Path(__file__).with_name('project-tasks-ui.html').read_text().replace('__PARA_TOKEN__', token)
                return self.send(200, html, 'text/html')
            if route == '/api/projects':
                return self.send(200, {'projects': store.listing()})
            self.send(404, {'error': 'Not found'})

        def do_POST(self):
            if not self.allowed_host() or self.headers.get('X-PARA-Token') != token or self.headers.get('Origin', origin) != origin:
                return self.send(403, {'error': 'Reload the local task page before updating.'})
            if self.path not in ('/api/update', '/api/create', '/api/intake'):
                return self.send(404, {'error': 'Not found'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 100000:
                    raise ValueError('Request is empty or too large.')
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError('Expected a task update object.')
                if self.path == '/api/intake':
                    self.send(200, {'skills': recommend_skills(payload)})
                else:
                    self.send(200, store.apply(payload, create=self.path == '/api/create'))
            except Conflict as exc:
                self.send(409, {'error': str(exc)})
            except (ValueError, KeyError, TypeError) as exc:
                self.send(400, {'error': str(exc)})
            except OSError as exc:
                self.send(500, {'error': 'Could not save the update: ' + str(exc)})

    server = HTTPServer(('127.0.0.1', args.port), Handler)
    print(f'PARA project tasks: {origin}/  (vault: {store.root})', flush=True)
    if args.open:
        webbrowser.open(origin)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
