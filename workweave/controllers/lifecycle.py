"""Lifecycle transport adapter; server handles request origin/content/size checks."""
from workweave.repositories.lifecycle import find_work
from workweave.schemas.lifecycle import LifecycleError
from workweave.services import lifecycle
from workweave.services.planning import handoff
from workweave.services.preparation import enroll, preview


def selected_project(registry, project_id):
    if not isinstance(project_id, str) or not project_id:
        raise LifecycleError('Select an explicit project.', 'project_required')
    project = registry.get(project_id)
    work_dir, _ = registry.resolve(project['path'])
    return work_dir


def get(registry, project_id, work_id):
    folder = find_work(selected_project(registry, project_id), work_id)
    data = lifecycle.state(folder)
    return {'lifecycle': data, 'legacy_preview': preview(folder) if not data['managed'] else None,
            'handoff': handoff(folder, project_id, work_id)}


def post(registry, payload):
    allowed = {'project_id', 'work_id', 'action', 'expected_version', 'actor', 'plan', 'run_id', 'feedback'}
    if set(payload) - allowed:
        raise LifecycleError('Unknown lifecycle fields.')
    folder = find_work(selected_project(registry, payload.get('project_id')), payload.get('work_id'))
    action, version = payload.get('action'), payload.get('expected_version')
    if type(version) is not int:
        raise LifecycleError('expected_version must be an integer.')
    if action == 'enroll':
        return {'lifecycle': enroll(folder, payload.get('actor'), version)}
    return {'lifecycle': lifecycle.transition(folder, action, version, payload.get('actor'),
                                             plan=payload.get('plan'), run_id=payload.get('run_id'),
                                             feedback=payload.get('feedback', ''))}
