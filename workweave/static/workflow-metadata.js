// Values come from parsed Markdown and are always rendered as escaped text.
function workflowWarnings(warnings) {
  if (!warnings?.length) return '';
  return '<div class="text-xs text-amber-300 border border-amber-800 rounded p-2" role="note"><strong>Workflow warnings</strong><ul>' +
    warnings.map(value => '<li>' + escapeHtml(value) + '</li>').join('') + '</ul></div>';
}
function workflowFields(pairs) {
  return '<dl class="text-xs text-gray-400 space-y-1">' + pairs.map(([label, value]) =>
    '<div><dt class="inline font-semibold">' + escapeHtml(label) + ': </dt><dd class="inline">' + escapeHtml(value || 'Unknown / not recorded') + '</dd></div>').join('') + '</dl>';
}
function taskWorkflowMetadata(task) {
  const pairs = [['Task ID', task.task_id], ['Depends on', task.depends_on]];
  if (task.status === 'Blocked' || task.blocked_by || task.blocker_reason || task.next_action) {
    pairs.push(['Blocked by', task.blocked_by], ['Blocker reason', task.blocker_reason], ['Next action', task.next_action]);
  }
  const links = (task.resolved_dependencies || []).map(dep => {
    const label = (dep.task_id || dep.title) + (dep.completed ? ' — completed; reassess readiness' : ' — unfinished');
    return /^work-\d+$/.test(dep.work_id) ? '<button type="button" class="text-xs text-indigo-300 underline" onclick="selectItem(\'' + dep.work_id + '\')">' + escapeHtml(label) + '</button>' : escapeHtml(label);
  }).join(' · ');
  return workflowFields(pairs) + (links ? '<div>' + links + '</div>' : '') + workflowWarnings(task.warnings);
}
