"""Explicit planning, review and execution transitions; no AI execution is simulated."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import uuid

from workweave.repositories import lifecycle as store
from workweave.schemas.lifecycle import LifecycleError, SCHEMA_VERSION, digest, text, validate_plan


def now():
    return datetime.now(timezone.utc).isoformat()


def approval_valid(folder, data):
    if not data['approval'] or not data['plans']:
        return False
    plan, approval = data['plans'][-1], data['approval']
    return (approval.get('revision') == plan['revision'] and approval.get('hash') == plan['hash']
            and plan['context_hash'] == store.fingerprint(folder) and not plan['content']['questions'])


def state(folder):
    with store.locked():
        data = store.read(folder)
        if data is None:
            return {'phase': 'Legacy / needs review', 'version': 0, 'approval_valid': False, 'managed': False}
        data['approval_valid'] = approval_valid(folder, data)
        data['managed'] = True
        data['context_changed'] = bool(data['plans'] and data['plans'][-1]['context_hash'] != store.fingerprint(folder))
        return data


def initialize(folder, request, actor='User', expected_version=0):
    actor = text(actor, 'Actor', limit=120)
    if not isinstance(request, str) or len(request) > 100000 or '\x00' in request:
        raise LifecycleError('Request must be text of at most 100000 characters.')
    with store.locked():
        existing = store.read(folder)
        if existing is not None:
            raise LifecycleError('Work already uses the lifecycle.', 'version_conflict', 409)
        if expected_version != 0:
            raise LifecycleError('Reload before initializing.', 'version_conflict', 409)
        data = {'schema_version': SCHEMA_VERSION, 'version': 1, 'phase': 'Draft',
                'request': request, 'request_hash': digest(request), 'plans': [], 'approval': None,
                'run': None, 'executor': None, 'progress': {}, 'events': [{'action': 'initialize', 'actor': actor, 'at': now()}]}
        store.write(folder, data)
    return state(folder)


def transition(folder, action, expected_version, actor, *, plan=None, run_id=None, feedback=''):
    actor = text(actor, 'Actor', limit=120)
    feedback = text(feedback, 'Feedback', optional=True)
    with store.locked():
        data = store.read(folder)
        if data is None:
            raise LifecycleError('Enroll this legacy work item before planning or starting.', 'review_required', 409)
        if type(expected_version) is not int or expected_version != data['version']:
            raise LifecycleError('This work changed. Reload and review the latest revision.', 'version_conflict', 409)
        data = deepcopy(data)
        phase = data['phase']
        if action == 'accept_planning':
            if phase not in ('Draft', 'Ready for review', 'Ready to implement'):
                raise LifecycleError('Request changes or cancel the current run first.', 'invalid_transition', 409)
            data.update(phase='Planning', approval=None, executor=None,
                        run={'id': uuid.uuid4().hex, 'planner': actor, 'started_at': now(), 'context_hash': store.fingerprint(folder)})
        elif action == 'submit_plan':
            if phase != 'Planning' or not data['run'] or run_id != data['run']['id'] or actor != data['run']['planner']:
                raise LifecycleError('Plan return does not match the active planner/run.', 'stale_run', 409)
            if data['run']['context_hash'] != store.fingerprint(folder):
                raise LifecycleError('Planning context changed. Cancel and restart planning with current files.', 'stale_context', 409)
            content = validate_plan(plan)
            data['plans'].append({'revision': len(data['plans']) + 1, 'content': content,
                                  'hash': digest(content), 'context_hash': store.fingerprint(folder),
                                  'planner': actor, 'run_id': run_id, 'created_at': now()})
            data['progress'][str(len(data['plans']))] = {}
            data.update(phase='Ready for review', run=None, approval=None)
        elif action in ('cancel_planning', 'fail_planning'):
            if phase != 'Planning' or not data['run'] or run_id != data['run']['id']:
                raise LifecycleError('No matching active planning run.', 'stale_run', 409)
            data.update(phase='Draft', run=None, approval=None)
        elif action == 'request_changes':
            if phase not in ('Ready for review', 'Ready to implement', 'In progress', 'Completed') or not feedback:
                raise LifecycleError('Review feedback is required for a submitted plan.', 'invalid_transition', 409)
            # Return to Draft awaiting an actual planner claim, rather than inventing active work.
            data.update(phase='Draft', run=None, approval=None, executor=None)
        elif action == 'approve':
            if phase != 'Ready for review' or not data['plans']:
                raise LifecycleError('Only a submitted plan can be approved.', 'invalid_transition', 409)
            current = data['plans'][-1]
            if current['content']['questions'] or current['context_hash'] != store.fingerprint(folder):
                raise LifecycleError('Resolve required questions or changed scope in a new plan before approval.', 'review_required', 409)
            data.update(phase='Ready to implement', approval={'revision': current['revision'], 'hash': current['hash'],
                                                             'reviewer': actor, 'at': now()})
        elif action == 'start':
            if phase != 'Ready to implement' or not approval_valid(folder, data):
                raise LifecycleError('A current approved plan is required before starting.', 'review_required', 409)
            data.update(phase='In progress', executor={'name': actor, 'started_at': now()})
        elif action == 'complete':
            if phase != 'In progress' or not approval_valid(folder, data) or not feedback:
                raise LifecycleError('Completion needs an active approved plan and verification evidence.', 'review_required', 409)
            current = data['plans'][-1]
            progress = data['progress'].get(str(current['revision']), {})
            if not all(progress.get(task['id'], False) for task in current['content']['tasks']):
                raise LifecycleError('Complete the approved tasks before completing the work.', 'tasks_incomplete', 409)
            data['phase'] = 'Completed'
        else:
            raise LifecycleError('Unknown lifecycle action.')
        data['version'] += 1
        data['events'].append({'action': action, 'actor': actor, 'at': now(), 'feedback': feedback})
        store.write(folder, data)
    return state(folder)


def require_execution(folder):
    data = state(folder)
    if data['phase'] != 'In progress' or not data['approval_valid']:
        raise LifecycleError('Implementation requires a current approved plan and an executor start. Use Plan & review first.', 'review_required', 409)
    return data


def toggle_task(folder, task_id, completed, expected_version):
    if type(completed) is not bool or not isinstance(task_id, str):
        raise LifecycleError('A task ID and boolean completed value are required.')
    with store.locked():
        data = store.read(folder)
        require_execution(folder)
        if type(expected_version) is not int or expected_version != data['version']:
            raise LifecycleError('Reload the latest work revision before updating.', 'version_conflict', 409)
        current = data['plans'][-1]
        tasks = {task['id']: task for task in current['content']['tasks']}
        if task_id not in tasks:
            raise LifecycleError('Task is not in the approved plan.', 'task_not_found', 404)
        progress = data['progress'][str(current['revision'])]
        if completed and any(not progress.get(dep, False) for dep in tasks[task_id]['dependencies']):
            raise LifecycleError('Complete this task’s dependencies first.', 'dependency_incomplete', 409)
        if not completed and any(task_id in t['dependencies'] and progress.get(t['id'], False) for t in tasks.values()):
            raise LifecycleError('Reopen dependent tasks first.', 'dependency_incomplete', 409)
        progress[task_id] = completed
        data['version'] += 1
        data['events'].append({'action': 'task_progress', 'task_id': task_id, 'completed': completed, 'at': now()})
        store.write(folder, data)
    return state(folder)
