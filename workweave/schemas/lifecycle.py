"""Lifecycle schema and plan validation, independent of HTTP and filesystem I/O."""
from __future__ import annotations

import hashlib
import json

SCHEMA_VERSION = 1
PHASES = ('Draft', 'Planning', 'Ready for review', 'Ready to implement', 'In progress', 'Completed')
STATUS = {phase: 'Pending' for phase in PHASES}
STATUS.update({'In progress': 'In Progress', 'Completed': 'Completed'})
MAX_TEXT = 12000
MAX_TASKS = 50


class LifecycleError(ValueError):
    def __init__(self, message, code='invalid_lifecycle', status=400):
        super().__init__(message)
        self.code, self.status = code, status


def text(value, label, optional=False, limit=MAX_TEXT):
    if not isinstance(value, str) or len(value) > limit or '\x00' in value or (not optional and not value.strip()):
        raise LifecycleError(f'{label} must be text' + ('.' if optional else ' and cannot be blank.'))
    return value.strip()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def validate_plan(value):
    keys = {'objective', 'scope', 'non_goals', 'architecture', 'assumptions', 'questions', 'tasks'}
    if not isinstance(value, dict) or set(value) != keys:
        raise LifecycleError('Plan must contain objective, scope, non_goals, architecture, assumptions, questions and tasks.')
    result = {key: text(value[key], key, optional=(key == 'architecture')) for key in ('objective', 'architecture')}
    for key in ('scope', 'non_goals', 'assumptions', 'questions'):
        if not isinstance(value[key], list) or len(value[key]) > MAX_TASKS:
            raise LifecycleError(f'{key} must be a list of at most {MAX_TASKS} strings.')
        result[key] = [text(item, key) for item in value[key]]
    if not result['scope']:
        raise LifecycleError('Define at least one in-scope requirement.')
    tasks = value['tasks']
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= MAX_TASKS:
        raise LifecycleError(f'Plan needs 1–{MAX_TASKS} tasks.')
    result['tasks'] = []
    for task in tasks:
        if not isinstance(task, dict) or set(task) != {'id', 'title', 'objective', 'acceptance', 'dependencies'}:
            raise LifecycleError('Each task needs id, title, objective, acceptance and dependencies.')
        clean = {key: text(task[key], key, limit=200 if key in ('id', 'title') else MAX_TEXT) for key in ('id', 'title', 'objective')}
        import re
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,39}', clean['id']):
            raise LifecycleError('Task IDs must use letters, numbers, dots, underscores or hyphens.')
        for key in ('acceptance', 'dependencies'):
            if not isinstance(task[key], list) or len(task[key]) > MAX_TASKS:
                raise LifecycleError(f'{key} must be a bounded list.')
            clean[key] = [text(item, key) for item in task[key]]
        if not clean['acceptance']:
            raise LifecycleError('Every task needs acceptance checks.')
        result['tasks'].append(clean)
    ids = {task['id'] for task in result['tasks']}
    if len(ids) != len(tasks):
        raise LifecycleError('Task IDs must be unique.')
    graph = {t['id']: t['dependencies'] for t in result['tasks']}
    done, visiting = set(), set()
    def visit(key):
        if key not in ids or key in visiting:
            raise LifecycleError('Task dependencies must exist and cannot form cycles.')
        if key in done:
            return
        visiting.add(key)
        for dep in graph[key]:
            visit(dep)
        visiting.remove(key)
        done.add(key)
    for key in graph:
        visit(key)
    return result
