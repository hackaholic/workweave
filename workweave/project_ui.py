"""Project library and navigation, without frontend build dependencies."""

from html import escape


STYLE = """
:root {color-scheme:dark;--bg:#090d16;--surface:#111827;--border:#334155;--muted:#aab7ca;--accent:#818cf8}
* {box-sizing:border-box} body {margin:0;background:var(--bg);color:#f3f4f6;font:16px/1.5 system-ui,sans-serif}
main {max-width:1100px;margin:0 auto;padding:48px 24px} h1 {font-size:32px;margin:8px 0} h2 {margin:0 0 12px;font-size:20px}
p {color:var(--muted)} .brand {color:var(--accent);font-weight:700;letter-spacing:.08em} .layout {display:grid;grid-template-columns:1fr 360px;gap:24px;margin-top:32px;align-items:start}
.panel,.project {background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px} .project {display:block;color:inherit;text-decoration:none;margin-bottom:12px;overflow-wrap:anywhere}
.project:hover {border-color:var(--accent);background:#182238} .project strong {font-size:19px;display:block}.project span {display:block;color:var(--muted);font-size:14px;margin-top:8px}
label {display:block;margin:16px 0 6px;font-size:14px;font-weight:600} input,button {font:inherit;border:1px solid var(--border);border-radius:8px;padding:10px 12px} input {width:100%;background:var(--bg);color:inherit} button {background:#4f46e5;color:white;cursor:pointer;font-weight:600;margin-top:20px} button:hover {background:#4338ca} button:active {transform:translateY(1px)} button:disabled {opacity:.6;cursor:wait}
a:focus-visible,button:focus-visible,input:focus-visible {outline:3px solid var(--accent);outline-offset:3px} .hint {font-size:13px;margin:8px 0;overflow-wrap:anywhere}.error {color:#fda4af}.status {min-height:24px;font-size:14px}.empty {border:1px dashed var(--border);border-radius:12px;padding:40px 24px;text-align:center}.empty p {margin-bottom:0} [hidden] {display:none!important}
.path-row {display:flex;gap:8px}.path-row input {min-width:0}.path-row button {margin:0}
dialog {color:inherit;background:var(--surface);border:1px solid var(--border);border-radius:12px;width:min(640px,calc(100% - 24px));max-height:85vh;padding:24px}dialog::backdrop {background:rgba(0,0,0,.7)}
.picker-heading,.picker-actions,.picker-toolbar {display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}.picker-heading h2 {margin:0}.picker-heading button,.picker-toolbar button,.picker-actions button {margin:0}
.picker-toolbar {justify-content:flex-start;margin-top:20px}.secondary {background:#1e293b}.secondary:hover {background:#334155}#folder-path {overflow-wrap:anywhere;font-size:14px}#folder-list {list-style:none;padding:0;margin:12px 0;max-height:32vh;overflow:auto}#folder-list button {display:block;width:100%;text-align:left;margin:4px 0;background:#182238;overflow-wrap:anywhere}#folder-list button:hover {background:#26344b}
.picker-actions {margin-top:20px;justify-content:flex-end}
@media(max-width:760px){main{padding:24px 16px}.layout{grid-template-columns:1fr}.panel{order:-1}h1{font-size:28px}}
"""


def project_library(projects_root=None) -> str:
    hint = (f"Use a folder under {projects_root}, for example {projects_root}/my-project. Docker paths refer to folders inside the container."
            if projects_root else "Use an absolute path on this computer, such as /home/you/git/my-project.")
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Projects — WorkWeave</title><style>""" + STYLE + """</style></head>
<body><main><div class="brand">WORKWEAVE</div><h1>Your projects</h1>
<p>Keep your local workflows together. Choose a project to explore its tasks, progress, and handoffs.</p>
<div class="layout"><section aria-label="Saved projects"><div id="list-status" class="status" role="status">Loading projects…</div>
<button id="retry" hidden>Retry loading projects</button><div id="projects"></div></section>
<aside class="panel"><h2>Add a project</h2><p class="hint">Connect a project with a <code>work/</code> folder. Your project files stay unchanged.</p>
<form id="add-project"><label for="path">Project folder</label><div class="path-row"><input id="path" name="path" required autocomplete="off" placeholder="/path/to/my-project" aria-describedby="path-hint"><button id="browse" type="button" aria-haspopup="dialog">Browse…</button></div>
<p id="path-hint" class="hint">""" + escape(hint) + """</p>
<label for="name">Display name <span style="font-weight:400">(optional)</span></label><input id="name" name="name" maxlength="120" placeholder="My project" autocomplete="off">
<button id="add" type="submit">Add project</button><p id="form-status" class="status" role="status" aria-live="polite"></p></form></aside></div></main>
<dialog id="folder-picker" aria-labelledby="picker-title">
<div class="picker-heading"><h2 id="picker-title">Choose a project folder</h2><button id="close-picker" class="secondary" type="button" aria-label="Close folder browser">Close</button></div>
<p class="hint">Open folders below, then select the project folder you want to add.</p>
<div class="picker-toolbar"><button id="folder-start" class="secondary" type="button">Starting folder</button><button id="folder-up" class="secondary" type="button" disabled>Up one level</button></div>
<p id="folder-path"></p><p id="folder-status" class="status" role="status" aria-live="polite"></p>
<button id="folder-retry" class="secondary" type="button" hidden>Retry</button>
<ul id="folder-list" aria-label="Folders"></ul>
<p id="folder-reason" class="hint"></p>
<div class="picker-actions"><button id="cancel-picker" class="secondary" type="button">Cancel</button><button id="select-folder" type="button" disabled>Select this folder</button></div>
</dialog>
<script>
const projects = document.getElementById('projects');
const listStatus = document.getElementById('list-status');
const retry = document.getElementById('retry');
async function loadProjects() {
  listStatus.textContent = 'Loading projects…'; listStatus.className = 'status'; retry.hidden = true;
  try {
    const response = await fetch('/api/projects'); const data = await response.json();
    if (!response.ok) throw new Error(data.error.message);
    projects.replaceChildren();
    listStatus.textContent = data.projects.length ? `${data.projects.length} saved project${data.projects.length === 1 ? '' : 's'}` : '';
    if (!data.projects.length) {
      const empty = document.createElement('div'); empty.className = 'empty';
      const title = document.createElement('h2'); title.textContent = 'No projects yet';
      const text = document.createElement('p'); text.textContent = 'Add your first project to start exploring its workflow.';
      empty.append(title, text); projects.append(empty);
    }
    for (const project of data.projects) {
      const card = document.createElement('a'); card.className = 'project'; card.href = '/projects/' + encodeURIComponent(project.id);
      const title = document.createElement('strong'); title.textContent = project.name;
      const path = document.createElement('span'); path.textContent = project.path;
      const action = document.createElement('span'); action.textContent = 'Open workflow →';
      card.append(title, path, action); projects.append(card);
    }
  } catch (error) {
    listStatus.textContent = 'Could not load projects. ' + error.message;
    listStatus.className = 'status error'; retry.hidden = false;
  }
}
retry.addEventListener('click', loadProjects);
document.getElementById('add-project').addEventListener('submit', async event => {
  event.preventDefault();
  const button = document.getElementById('add'), status = document.getElementById('form-status');
  button.disabled = true; button.textContent = 'Adding…'; status.className = 'status'; status.textContent = '';
  try {
    const response = await fetch('/api/projects', {method:'POST', headers:{'Content-Type':'application/json','X-WorkWeave-Request':'1'},
      body:JSON.stringify({path:document.getElementById('path').value, name:document.getElementById('name').value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error.message);
    window.location.assign('/projects/' + encodeURIComponent(data.project.id));
  } catch (error) {
    status.textContent = error.message; status.className = 'status error';
    button.disabled = false; button.textContent = 'Add project';
  }
});
const picker = document.getElementById('folder-picker');
const folderList = document.getElementById('folder-list');
const folderStatus = document.getElementById('folder-status');
const folderSelect = document.getElementById('select-folder');
const folderUp = document.getElementById('folder-up');
const folderRetry = document.getElementById('folder-retry');
let folderData = null, folderRequest = null, folderGeneration = 0, requestedPath;
async function browseFolder(path) {
  if (folderRequest) folderRequest.abort();
  folderRequest = new AbortController();
  const generation = ++folderGeneration;
  requestedPath = path; folderData = null;
  folderSelect.disabled = true; folderUp.disabled = true; folderRetry.hidden = true;
  folderList.replaceChildren(); folderStatus.className = 'status'; folderStatus.textContent = 'Loading folders…';
  document.getElementById('folder-path').textContent = path || 'Starting folder';
  document.getElementById('folder-reason').textContent = '';
  try {
    const url = '/api/folders' + (path === undefined ? '' : '?path=' + encodeURIComponent(path));
    const response = await fetch(url, {signal:folderRequest.signal});
    const data = await response.json();
    if (generation !== folderGeneration || !picker.open) return;
    if (!response.ok) throw new Error(data.error.message);
    folderData = data;
    document.getElementById('folder-path').textContent = data.path;
    document.getElementById('folder-reason').textContent = data.reason;
    folderSelect.disabled = !data.selectable; folderUp.disabled = !data.parent;
    folderStatus.textContent = data.truncated ? 'Showing the first 1000 folders. You can enter an exact path in the form for other folders.' : data.directories.length ? 'Choose a folder to open.' : 'No subfolders here.';
    for (const entry of data.directories) {
      const li = document.createElement('li'), button = document.createElement('button');
      button.type = 'button'; button.textContent = entry.name + ' →';
      button.addEventListener('click', () => browseFolder(entry.path));
      li.append(button); folderList.append(li);
    }
  } catch (error) {
    if (generation !== folderGeneration || error.name === 'AbortError' || !picker.open) return;
    folderStatus.className = 'status error'; folderStatus.textContent = error.message;
    folderRetry.hidden = false;
  }
}
document.getElementById('browse').addEventListener('click', () => {
  picker.showModal();
  browseFolder(document.getElementById('path').value.trim() || undefined);
});
document.getElementById('folder-start').addEventListener('click', () => browseFolder());
folderUp.addEventListener('click', () => {if (folderData && folderData.parent) browseFolder(folderData.parent);});
folderRetry.addEventListener('click', () => browseFolder(requestedPath));
for (const id of ['close-picker', 'cancel-picker']) document.getElementById(id).addEventListener('click', () => picker.close());
picker.addEventListener('close', () => {++folderGeneration; if (folderRequest) folderRequest.abort();});
folderSelect.addEventListener('click', () => {
  if (!folderData || !folderData.selectable) return;
  document.getElementById('path').value = folderData.path;
  document.getElementById('form-status').textContent = '';
  picker.close(); document.getElementById('path').focus();
});
loadProjects();
</script></body></html>"""


def project_navigation(projects: list[dict], selected_id: str) -> str:
    options = "".join(f'<option value="{escape(p["id"], quote=True)}"'
                      + (' selected' if p['id'] == selected_id else '')
                      + f'>{escape(p["name"])}</option>' for p in projects)
    return ('<nav aria-label="Project navigation" style="padding:12px 24px;background:#111827;color:#f3f4f6;display:flex;gap:16px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #334155">'
            '<a href="/" style="color:#a5b4fc">← All projects / Add project</a>'
            '<label for="project-switch">Project</label>'
            '<select id="project-switch" style="background:#090d16;color:#f3f4f6;border:1px solid #64748b;padding:8px;border-radius:6px;max-width:100%" '
            'onchange="location.href=\'/projects/\'+encodeURIComponent(this.value)">'
            + options + '</select></nav>')


def project_error(message: str) -> str:
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Project unavailable — WorkWeave</title><style>' + STYLE + '</style></head><body><main>'
            '<h1>Project unavailable</h1><p>' + escape(message) + '</p>'
            '<a href="/" style="color:#a5b4fc">Return to Projects</a></main></body></html>')
