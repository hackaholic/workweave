'use strict';
(() => {
  const project = document.body.dataset.project, work = document.body.dataset.work;
  const byId = id => document.getElementById(id);
  let current = null, busy = false;
  function element(tag, text, parent) {
    const node = document.createElement(tag); node.textContent = text; parent.append(node); return node;
  }
  function list(title, items, parent) {
    element('h3', title, parent);
    if (!items.length) { element('p', 'None.', parent); return; }
    const ul = document.createElement('ul'); parent.append(ul);
    for (const item of items) element('li', item, ul);
  }
  function setBusy(value) {
    busy = value;
    document.querySelectorAll('button').forEach(button => { button.disabled = value || button.dataset.unavailable === 'true'; });
  }
  function action(label, name, unavailable = false) {
    const button = element('button', label, byId('actions'));
    button.dataset.unavailable = String(unavailable); button.disabled = unavailable;
    button.addEventListener('click', () => mutate(name));
  }
  function render(data) {
    current = data.lifecycle;
    byId('controls').hidden = false;
    byId('phase').textContent = current.phase + (current.version ? ' · version ' + current.version : '');
    byId('request').textContent = current.request ?? data.legacy_preview?.files[data.legacy_preview.request_source] ?? 'No original request recorded.';
    byId('legacy-notice').textContent = data.legacy_preview?.notice || '';
    byId('handoff').value = data.handoff.prompt;
    byId('notice').textContent = current.context_changed ? 'Plan-bearing files changed since submission. Request changes and submit a fresh plan before approving or implementing.' :
      current.managed ? 'Approval authorizes only this plan revision. Starting implementation is a separate action.' :
      'This is a legacy record with no recorded approval. Enrollment preserves its files and starts a new Draft review cycle. Historical work is not treated as approved.';
    byId('actions').replaceChildren();
    if (!current.managed) action('Enroll legacy work for review', 'enroll');
    if (current.phase === 'Draft') action('Record planner pickup', 'accept_planning');
    if (current.phase === 'Planning') {
      element('p', 'Active planner: ' + current.run.planner + ' · run ' + current.run.id, byId('actions'));
      action('Cancel planning run', 'cancel_planning');
      action('Record planning failure', 'fail_planning');
    }
    byId('import-section').hidden = current.phase !== 'Planning';
    const latest = current.plans?.at(-1);
    if (current.phase === 'Ready for review') action('Approve this plan', 'approve', current.context_changed || Boolean(latest?.content.questions.length));
    if (['Ready for review', 'Ready to implement', 'In progress', 'Completed'].includes(current.phase)) action('Request changes', 'request_changes');
    if (current.phase === 'Ready to implement') action('Claim and start implementation', 'start', !current.approval_valid);
    if (current.phase === 'In progress') action('Mark work completed', 'complete', !current.approval_valid);
    byId('plan').replaceChildren();
    if (!latest) element('p', 'No plan submitted yet. Give the handoff instructions to your chosen agent.', byId('plan'));
    else {
      const plan = latest.content, parent = byId('plan');
      element('p', 'Revision ' + latest.revision + ' · Planner: ' + latest.planner, parent);
      element('h3', 'Objective', parent); element('p', plan.objective, parent);
      list('In scope', plan.scope, parent); list('Out of scope', plan.non_goals, parent);
      element('h3', 'Architecture and context', parent); element('p', plan.architecture || 'No additional design notes.', parent);
      list('Assumptions', plan.assumptions, parent); list('Unresolved required questions', plan.questions, parent);
      for (const task of plan.tasks) {
        const box = document.createElement('div'); box.className = 'task'; parent.append(box);
        element('h3', task.id + ' · ' + task.title, box); element('p', task.objective, box);
        list('Acceptance checks', task.acceptance, box); list('Dependencies', task.dependencies, box);
      }
      if (current.approval) element('p', 'Reviewed by ' + current.approval.reviewer + ' at ' + current.approval.at +
        (current.approval_valid ? ' · Current approval' : ' · Approval is no longer valid'), parent);
      if (current.executor) element('p', 'Executor: ' + current.executor.name, parent);
    }
    byId('history').replaceChildren();
    for (const plan of (current.plans || []).slice(0, -1)) {
      element('h3', 'Plan revision ' + plan.revision, byId('history'));
      element('pre', JSON.stringify(plan.content, null, 2), byId('history'));
    }
    for (const event of current.events || []) element('p', event.at + ' · ' + event.action + ' · ' + (event.actor || '') +
      (event.feedback ? ' — ' + event.feedback : ''), byId('history'));
  }
  async function load() {
    const response = await fetch('/api/lifecycle?project=' + encodeURIComponent(project) + '&work=' + encodeURIComponent(work));
    const data = await response.json();
    if (!response.ok) throw new Error(data.error.message);
    render(data);
  }
  async function reload() {
    if (busy) return;
    setBusy(true); byId('status').className = ''; byId('status').textContent = 'Loading latest state…';
    try { await load(); byId('status').textContent = ''; }
    catch (error) { current = null; byId('controls').hidden = true; byId('status').className = 'error'; byId('status').textContent = error.message; }
    finally { setBusy(false); }
  }
  async function mutate(name, envelope = null) {
    if (busy || !current) return;
    const actor = byId('actor').value.trim();
    const feedback = byId('feedback').value.trim();
    if (!envelope && !actor) { byId('status').textContent = 'Enter the actual acting person or agent name.'; byId('actor').focus(); return; }
    const payload = envelope || {project_id:project, work_id:work, action:name, expected_version:current.version, actor,
                                run_id:current.run?.id, feedback};
    setBusy(true); byId('status').className = ''; byId('status').textContent = 'Saving…';
    try {
      const response = await fetch('/api/lifecycle', {method:'POST', headers:{'Content-Type':'application/json','X-WorkWeave-Request':'1'}, body:JSON.stringify(payload)});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error.message);
      await load(); byId('status').textContent = 'Saved. ' + current.phase + '.';
      byId('feedback').value = ''; if (name === 'submit_plan') byId('plan-return').value = '';
    } catch (error) { byId('status').className = 'error'; byId('status').textContent = error.message + ' Reload latest state if it changed.'; }
    finally { setBusy(false); }
  }
  byId('reload').addEventListener('click', reload);
  byId('import').addEventListener('click', () => {
    try {
      const envelope = JSON.parse(byId('plan-return').value);
      if (!envelope || envelope.action !== 'submit_plan' || envelope.project_id !== project || envelope.work_id !== work) throw new Error('Return must target this project/work and use action submit_plan.');
      mutate('submit_plan', envelope);
    } catch (error) { byId('status').className = 'error'; byId('status').textContent = 'Invalid return: ' + error.message; }
  });
  reload();
})();
