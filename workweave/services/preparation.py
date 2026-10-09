"""Non-destructive structure preparation and explicit legacy enrollment."""
from workweave.repositories import lifecycle as store
from workweave.schemas.lifecycle import LifecycleError
from workweave.services import lifecycle


def preview(folder):
    files = {}
    for name in ('README.md', 'notes.md', 'tasks.md', 'coordination.md'):
        path = store.safe_file(folder, name)
        if path.is_file():
            if path.stat().st_size > 100000:
                raise LifecycleError('Legacy source is too large to enroll automatically.')
            files[name] = path.read_text(encoding='utf-8')
    return {'files': files, 'request_source': 'notes.md' if 'notes.md' in files else 'README.md',
            'notice': 'Legacy files are retained verbatim. Imported notes may not be the original user request. No historical approval is inferred.'}


def enroll(folder, actor, expected_version):
    source = preview(folder)
    request = source['files'].get(source['request_source'], '')
    return lifecycle.initialize(folder, request, actor, expected_version)


def prepare(folder):
    """Only create absent files. This function never claims planning or execution."""
    contents = {'tasks.md': '# Tasks\n\n## Pending\n\n', 'notes.md': '# Notes\n',
                'decisions.md': '# Decisions\n',
                'coordination.md': '# Coordination\n\n**Current owner:** Unassigned\n**Handoff state:** Awaiting planning\n'}
    with store.locked():
        # Validate every target before any write.
        paths = {name: store.safe_file(folder, name) for name in contents}
        tasks = store.safe_file(folder, 'tasks')
        try:
            tasks.mkdir(exist_ok=True)
            for name, content in contents.items():
                if not paths[name].exists():
                    with paths[name].open('x', encoding='utf-8') as file:
                        file.write(content)
        except OSError as exc:
            raise LifecycleError('Preparation could not finish. Existing files are preserved; retry after checking permissions.', 'preparation_failed', 500) from exc
    return True
