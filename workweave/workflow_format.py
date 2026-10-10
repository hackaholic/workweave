"""Read shared Markdown workflow metadata without modifying source records."""
from pathlib import Path
import posixpath
import re

TASK_ID = r'\d+(?:\.\d+)+'
STATUSES = {'pending': 'Pending', 'in progress': 'In Progress', 'blocked': 'Blocked', 'completed': 'Completed'}


def fields(content):
    """Accept scaffold bullets and historical bold labels; report duplicate conflicts."""
    result, warnings = {}, []
    for line in content.splitlines():
        match = re.match(r'^\s*(?:[-*]\s+)?(?:\*\*)?([A-Za-z][A-Za-z /_-]*):(?:\*\*)?\s*(.*?)\s*$', line)
        if match:
            key, value = match.groups(); key = key.lower().replace('_', ' ')
            if key not in {'task id', 'owner', 'status', 'depends on', 'blocked by', 'blocker reason', 'next action', 'current owner', 'active task', 'handoff state', 'active cross-agent handoffs'}:
                continue
            if key in result and result[key] != value:
                warnings.append(f'Conflicting {key} fields; first value retained.')
            else:
                result[key] = value
    return result, warnings


def semantic_id(title):
    match = re.match(r'^(?:Task\s+)?(' + TASK_ID + r')\b', title, re.I)
    if not match:
        match = re.match(r'^[^:]+:\s*(' + TASK_ID + r')\b', title)
    return match.group(1) if match else ''


def dependencies(raw):
    """Only complete ID/link lists become edges; prose stays available verbatim."""
    if raw.strip().lower() == 'none':
        return []
    if not raw.strip() or raw.strip().lower() == 'unknown':
        return []
    token = r'(?:' + TASK_ID + r'|\[[^\]]+\]\([^)]+\.md\))'
    if not re.fullmatch(token + r'(?:\s*[,;]\s*' + token + r')*', raw.strip()):
        return []
    return [m.group() for m in re.finditer(token, raw)]


def enrich(subtasks, contracts, folder, root):
    by_path = {c.path: c for c in contracts}
    for task in subtasks:
        contract = by_path.get(task.contract_path)
        if not contract:
            if task.contract_path:
                task.warnings.append('Linked contract is missing or outside this work folder.')
            continue
        task.warnings.extend(contract.warnings)
        if task.task_id and contract.task_id and task.task_id != contract.task_id:
            task.warnings.append('Checklist and contract task IDs disagree; checklist ID retained.')
        task.task_id = task.task_id or contract.task_id
        if contract.owner:
            if task.owner and task.owner.strip() != contract.owner:
                task.warnings.append('Checklist and contract owners disagree; contract owner displayed.')
            task.owner = contract.owner
        status = STATUSES.get(contract.status.lower())
        if status and (task.section_status or task.completed) and status != task.status:
            task.warnings.append(f'Contract status {status} differs from checklist status {task.status}.')
        if not task.section_status and not task.completed and status:
            task.status = status
        task.depends_on = contract.depends_on
        task.dependencies = list(contract.dependencies)
        task.blocked_by = contract.blocked_by
        task.blocker_reason = contract.blocker_reason
        task.next_action = contract.next_action
        if task.depends_on and task.depends_on.lower() not in ('none', 'unknown') and not task.dependencies:
            task.warnings.append('Dependency prose retained; no structured dependency inferred.')


def check_references(items):
    """Resolve only known task IDs or contained contract links; never read link targets."""
    all_tasks = [(item, task) for item in items if not item.lifecycle.get('managed') for task in item.subtasks]
    by_id, by_path = {}, {}
    for item, task in all_tasks:
        if task.task_id:
            by_id.setdefault(task.task_id, []).append((item, task))
        if task.contract_path:
            by_path.setdefault(task.contract_path, []).append((item, task))
    graph = {}
    for item, task in all_tasks:
        if task.task_id and len(by_id[task.task_id]) > 1:
            task.warnings.append('Duplicate task ID; dependency resolution is ambiguous.')
        edges = []
        for reference in task.dependencies:
            if re.fullmatch(TASK_ID, reference):
                matches = by_id.get(reference, [])
            else:
                target = re.search(r'\]\(([^)]+)\)', reference).group(1)
                base = Path(task.contract_path).parent if task.contract_path else Path(item.relative_path)
                normalized = posixpath.normpath(str(base / target))
                matches = by_path.get(normalized, []) if not Path(target).is_absolute() and '://' not in target else []
            if len(matches) != 1:
                task.warnings.append(f'Unknown or ambiguous dependency: {reference}')
            else:
                other_item, other_task = matches[0]
                task.resolved_dependencies.append({'task_id': other_task.task_id, 'work_id': other_item.id,
                                                  'title': other_task.title, 'completed': other_task.completed})
                edges.append(id(other_task))
        graph[id(task)] = edges
    # Iterative reachability avoids recursion limits on large backlogs.
    for _, task in all_tasks:
        pending, seen = list(graph[id(task)]), set()
        while pending:
            node = pending.pop()
            if node == id(task):
                task.warnings.append('Dependency cycle detected; resolve before pickup.'); break
            if node not in seen:
                seen.add(node); pending.extend(graph.get(node, []))
