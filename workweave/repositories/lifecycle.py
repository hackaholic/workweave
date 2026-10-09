"""Atomic lifecycle snapshots. One app process per workspace; threads are serialized."""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import tempfile
import threading

from workweave.schemas.lifecycle import LifecycleError, PHASES, SCHEMA_VERSION, digest, validate_plan

_LOCK = threading.RLock()
MAX_RECORD_BYTES = 4 * 1024 * 1024


def safe_file(folder, relative):
    root = Path(folder).resolve()
    candidate = root / relative
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(root):
        raise LifecycleError('Workflow files must stay inside their work folder.', 'unsafe_path', 403)
    return candidate


def find_work(target, work_id):
    from workweave.parser import resolve_work_directory
    if not isinstance(work_id, str) or not re.fullmatch(r'work-\d+(?:[-_][A-Za-z0-9_-]+)?', work_id):
        raise LifecycleError('Invalid work ID.')
    work_dir, _ = resolve_work_directory(target)
    matches = [p for p in work_dir.iterdir() if p.is_dir() and
               (p.name == work_id or p.name.startswith(work_id + '-') or p.name.startswith(work_id + '_'))]
    if len(matches) != 1:
        raise LifecycleError('Work item not found or ambiguous.', 'work_not_found', 404)
    folder = matches[0]
    if folder.is_symlink() or not folder.resolve().is_relative_to(work_dir.resolve()):
        raise LifecycleError('Work folder escapes its project.', 'unsafe_path', 403)
    return folder


@contextmanager
def locked():
    with _LOCK:
        yield


def read(folder):
    path = safe_file(folder, 'workflow.json')
    if not path.exists():
        return None
    try:
        if path.stat().st_size > MAX_RECORD_BYTES:
            raise ValueError('oversized')
        data = json.loads(path.read_text(encoding='utf-8'))
        if (data['schema_version'] != SCHEMA_VERSION or data['phase'] not in PHASES
                or type(data['version']) is not int or data['version'] < 1
                or not isinstance(data['request'], str) or not isinstance(data['plans'], list)
                or not isinstance(data['events'], list)):
            raise ValueError('schema')
        if data['request_hash'] != digest(data['request']):
            raise ValueError('request changed')
        if not isinstance(data['progress'], dict) or any(not isinstance(e, dict) for e in data['events']):
            raise ValueError('progress/events')
        for n, plan in enumerate(data['plans'], 1):
            if plan['revision'] != n or plan['hash'] != digest(plan['content']):
                raise ValueError('plan changed')
            validate_plan(plan['content'])
            for key in ('context_hash', 'planner', 'run_id', 'created_at'):
                if not isinstance(plan[key], str):
                    raise ValueError('plan metadata')
            progress = data['progress'][str(n)]
            if not isinstance(progress, dict) or any(type(v) is not bool for v in progress.values()):
                raise ValueError('progress')
        for key in ('approval', 'run', 'executor'):
            if data[key] is not None and not isinstance(data[key], dict):
                raise ValueError('metadata')
        if data['phase'] == 'Planning' and (not data['run'] or not all(isinstance(data['run'][k], str) for k in ('id', 'planner', 'context_hash'))):
            raise ValueError('run')
        if data['phase'] in ('Ready for review', 'Ready to implement', 'In progress', 'Completed') and not data['plans']:
            raise ValueError('missing plan')
        if data['approval'] is not None and not all(k in data['approval'] for k in ('revision', 'hash', 'reviewer', 'at')):
            raise ValueError('approval')
        return data
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise LifecycleError('Lifecycle record is unreadable or changed outside WorkWeave; restore it before continuing.', 'lifecycle_corrupt', 409) from exc


def write(folder, data):
    path = safe_file(folder, 'workflow.json')
    content = json.dumps(data, indent=2, ensure_ascii=True) + '\n'
    if len(content.encode()) > MAX_RECORD_BYTES:
        raise LifecycleError('Lifecycle history exceeds its storage limit.', 'history_limit', 409)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=folder, delete=False) as file:
            temporary = Path(file.name)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        raise LifecycleError('Cannot save lifecycle; the previous record is preserved.', 'storage_error', 500) from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def fingerprint(folder):
    """Plan-bearing Markdown only; checkbox progress, status/owner and notes are excluded."""
    files = [safe_file(folder, 'README.md'), safe_file(folder, 'tasks.md')]
    tasks = safe_file(folder, 'tasks')
    if tasks.is_dir():
        files += sorted(tasks.glob('*.md'))
    content = {}
    for path in files:
        path = safe_file(folder, str(path.relative_to(folder)))
        if not path.is_file():
            continue
        lines = []
        for line in path.read_text(encoding='utf-8').splitlines():
            if re.match(r'^(?:\*\*(?:Status|Owner):\*\*|## (?:Pending|In Progress|Completed)\s*$)', line):
                continue
            line = re.sub(r'^([-*]\s+)\[[ xX]\]', r'\1[ ]', line).rstrip()
            if line.strip():
                lines.append(line)
        content[str(path.relative_to(folder))] = lines
    return digest(content)
