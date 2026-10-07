"""WorkWeave Dashboard: Generates modern, interactive HTML/JS dashboard."""

from __future__ import annotations

import json
from dataclasses import asdict
from workweave.parser import WorkflowState


def generate_html_dashboard(state: WorkflowState) -> str:
    """Generate standalone interactive HTML dashboard."""
    state_json = json.dumps(asdict(state), indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{state.project_name} — WorkWeave Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --background: #090d16;
      --card: #111827;
      --card-hover: #1f2937;
      --border: #1f2937;
      --foreground: #f3f4f6;
      --muted-foreground: #9ca3af;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scrollbar::-webkit-scrollbar-track {{
      background: rgba(0, 0, 0, 0.1);
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: rgba(156, 163, 175, 0.3);
      border-radius: 3px;
    }}
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] min-h-screen antialiased flex flex-col">

  <!-- Header Banner -->
  <header class="bg-[var(--card)] border-b border-[var(--border)] sticky top-0 z-30 shadow-md">
    <div class="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-inner">
          ⚡
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-[var(--foreground)] flex items-center gap-2">
            <span>{state.project_name}</span>
            <span class="text-xs font-normal text-indigo-400">WorkWeave</span>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700/50">Live</span>
          </h1>
          <p class="text-xs text-[var(--muted-foreground)]">Tracking {state.total_work_items} work items across multi-agent workspace</p>
        </div>
      </div>

      <!-- Overall Progress Stat -->
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-3">
          <div class="text-right">
            <div class="text-xs font-medium text-[var(--muted-foreground)]">Overall Progress</div>
            <div class="text-sm font-bold text-indigo-400">{state.overall_progress_percent}% ({state.completed_subtasks}/{state.total_subtasks} subtasks)</div>
          </div>
          <div class="w-24 bg-gray-800 rounded-full h-2.5 overflow-hidden border border-gray-700">
            <div class="bg-indigo-500 h-2.5 rounded-full transition-all duration-500" style="width: {state.overall_progress_percent}%;"></div>
          </div>
        </div>

        <button onclick="location.reload()" title="Refresh live data" class="px-3 py-1.5 rounded-md bg-[var(--card-hover)] hover:bg-gray-700 text-xs font-medium border border-[var(--border)] transition flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          Sync
        </button>
      </div>
    </div>
  </header>

  <!-- Metrics Bar -->
  <div class="bg-[var(--card)]/50 border-b border-[var(--border)] py-2.5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 text-center">
      <div class="p-2 rounded-lg bg-[var(--card)] border border-[var(--border)]">
        <div class="text-xs text-[var(--muted-foreground)]">Total Items</div>
        <div class="text-lg font-bold text-white">{state.total_work_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-emerald-950/40 border border-emerald-800/40">
        <div class="text-xs text-emerald-400">Completed</div>
        <div class="text-lg font-bold text-emerald-300">{state.completed_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-blue-950/40 border border-blue-800/40">
        <div class="text-xs text-blue-400">In Progress</div>
        <div class="text-lg font-bold text-blue-300">{state.in_progress_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-amber-950/40 border border-amber-800/40">
        <div class="text-xs text-amber-400">Pending</div>
        <div class="text-lg font-bold text-amber-300">{state.pending_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-gray-900 border border-[var(--border)] col-span-2 sm:col-span-4 lg:col-span-1">
        <div class="text-xs text-[var(--muted-foreground)]">Completed Subtasks</div>
        <div class="text-lg font-bold text-gray-200">{state.completed_subtasks} / {state.total_subtasks}</div>
      </div>
    </div>
  </div>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex-1 flex flex-col w-full">
    
    <!-- Controls Toolbar (Search & Filter Pills) -->
    <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 mb-5">
      <!-- Filter Pills -->
      <div class="flex items-center gap-1.5 flex-wrap">
        <button onclick="setFilter('ALL')" id="filter-ALL" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-indigo-600 text-white transition shadow-sm">
          All ({state.total_work_items})
        </button>
        <button onclick="setFilter('IN_PROGRESS')" id="filter-IN_PROGRESS" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-[var(--card)] hover:bg-[var(--card-hover)] text-[var(--muted-foreground)] border border-[var(--border)] transition">
          In Progress ({state.in_progress_items})
        </button>
        <button onclick="setFilter('COMPLETED')" id="filter-COMPLETED" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-[var(--card)] hover:bg-[var(--card-hover)] text-[var(--muted-foreground)] border border-[var(--border)] transition">
          Completed ({state.completed_items})
        </button>
        <button onclick="setFilter('PENDING')" id="filter-PENDING" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-[var(--card)] hover:bg-[var(--card-hover)] text-[var(--muted-foreground)] border border-[var(--border)] transition">
          Pending ({state.pending_items})
        </button>
      </div>

      <!-- Search Input -->
      <div class="relative w-full md:w-72">
        <input
          type="text"
          id="search-input"
          oninput="handleSearch(this.value)"
          placeholder="Search work, subtasks, agent..."
          class="w-full bg-[var(--card)] border border-[var(--border)] rounded-lg px-3 py-1.5 pl-9 text-xs text-[var(--foreground)] placeholder-[var(--muted-foreground)] focus:outline-none focus:border-indigo-500 transition"
        />
        <svg class="w-4 h-4 text-gray-500 absolute left-2.5 top-2.5 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>

    <!-- 2-Column Responsive Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 flex-1 min-h-0">
      
      <!-- Left Column: Work Items List (5 cols) -->
      <div class="lg:col-span-5 flex flex-col h-[750px] bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="px-4 py-3 border-b border-[var(--border)] bg-gray-900/40 flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">Work Items</span>
          <span id="items-count-badge" class="text-xs bg-gray-800 px-2 py-0.5 rounded text-gray-300">Showing {state.total_work_items}</span>
        </div>
        <div id="work-items-list" class="flex-1 overflow-y-auto divide-y divide-[var(--border)] custom-scrollbar">
          <!-- Dynamically populated by JS -->
        </div>
      </div>

      <!-- Right Column: Detail Pane (7 cols) -->
      <div class="lg:col-span-7 flex flex-col h-[750px] bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div id="detail-header" class="px-5 py-4 border-b border-[var(--border)] bg-gray-900/40 flex items-center justify-between">
          <!-- Dynamically populated header -->
        </div>
        <div id="detail-body" class="flex-1 overflow-y-auto p-5 custom-scrollbar space-y-6">
          <!-- Dynamically populated content -->
        </div>
      </div>

    </div>

  </main>

  <!-- Contract Modal -->
  <div id="contract-modal" class="fixed inset-0 z-50 hidden bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-5 py-3.5 border-b border-[var(--border)] bg-gray-900/50 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-base">📄</span>
          <h3 id="modal-title" class="text-sm font-bold text-white truncate max-w-md">Task Contract</h3>
        </div>
        <button onclick="closeModal()" class="text-gray-400 hover:text-white p-1 rounded-md hover:bg-gray-800 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      <div id="modal-body" class="p-5 overflow-y-auto space-y-4 custom-scrollbar text-xs text-gray-300">
        <!-- Contract contents -->
      </div>
      <div class="px-5 py-3 border-t border-[var(--border)] bg-gray-900/30 flex justify-end">
        <button onclick="closeModal()" class="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium transition">Close</button>
      </div>
    </div>
  </div>

  <footer class="border-t border-[var(--border)] py-3 text-center text-xs text-[var(--muted-foreground)]">
    WorkWeave Multi-Agent Coordination • Target: <code class="text-gray-400">{state.target_path}</code> • Scanned: {state.generated_at}
  </footer>

  <script>
    const DATA = {state_json};
    let currentFilter = 'ALL';
    let searchQuery = '';
    let selectedItemId = DATA.items.length > 0 ? DATA.items[0].id : null;

    function getStatusBadge(status) {{
      switch(status) {{
        case 'Completed':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950 text-emerald-300 border border-emerald-700/50">Completed</span>';
        case 'In Progress':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-950 text-blue-300 border border-blue-700/50">In Progress</span>';
        case 'Pending':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-950 text-amber-300 border border-amber-700/50">Pending</span>';
        case 'Blocked':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-950 text-rose-300 border border-rose-700/50">Blocked</span>';
        default:
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-gray-800 text-gray-300 border border-gray-700">' + escapeHtml(status) + '</span>';
      }}
    }}

    function getOwnerBadge(owner) {{
      if (!owner) return '';
      let colorClass = 'bg-gray-800 text-gray-300 border-gray-700';
      if (owner.includes('Gemini')) colorClass = 'bg-purple-950 text-purple-300 border-purple-800/60';
      else if (owner.includes('Codex')) colorClass = 'bg-cyan-950 text-cyan-300 border-cyan-800/60';
      else if (owner.includes('Owner')) colorClass = 'bg-amber-950 text-amber-300 border-amber-800/60';
      else if (owner.includes('Claude') || owner.includes('GPT')) colorClass = 'bg-emerald-950 text-emerald-300 border-emerald-800/60';
      return '<span class="px-2 py-0.5 rounded-md text-[10px] font-medium border ' + colorClass + '">' + escapeHtml(owner) + '</span>';
    }}

    function filterItems() {{
      return DATA.items.filter(item => {{
        if (currentFilter === 'IN_PROGRESS' && item.status !== 'In Progress') return false;
        if (currentFilter === 'COMPLETED' && item.status !== 'Completed') return false;
        if (currentFilter === 'PENDING' && item.status !== 'Pending') return false;
        if (currentFilter === 'BLOCKED' && item.status !== 'Blocked') return false;

        if (searchQuery) {{
          const q = searchQuery.toLowerCase();
          const matchTitle = item.title.toLowerCase().includes(q);
          const matchId = item.id.toLowerCase().includes(q);
          const matchGoal = item.goal.toLowerCase().includes(q);
          const matchOwner = (item.current_owner || '').toLowerCase().includes(q);
          const matchSubtask = item.subtasks.some(s => s.title.toLowerCase().includes(q) || (s.owner || '').toLowerCase().includes(q));
          if (!matchTitle && !matchId && !matchGoal && !matchOwner && !matchSubtask) return false;
        }}
        return true;
      }});
    }}

    function renderList() {{
      const listEl = document.getElementById('work-items-list');
      const filtered = filterItems();
      document.getElementById('items-count-badge').textContent = `Showing ${{filtered.length}} of ${{DATA.items.length}}`;

      if (filtered.length === 0) {{
        listEl.innerHTML = `
          <div class="p-8 text-center text-xs text-[var(--muted-foreground)]">
            <div class="text-2xl mb-2">🔍</div>
            No work items match your current filter.
          </div>
        `;
        return;
      }}

      listEl.innerHTML = filtered.map(item => {{
        const isSelected = item.id === selectedItemId;
        return `
          <div
            onclick="selectItem('${{item.id}}')"
            class="p-4 cursor-pointer transition flex flex-col gap-2 ${{
              isSelected
                ? 'bg-gray-800/80 border-l-4 border-indigo-500 pl-3'
                : 'hover:bg-[var(--card-hover)]'
            }}"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="text-xs font-mono font-semibold text-gray-400">#${{String(item.number).padStart(3, '0')}}</span>
              <div class="flex items-center gap-1.5">
                ${{getStatusBadge(item.status)}}
              </div>
            </div>
            
            <div class="text-xs font-semibold text-white line-clamp-1 leading-snug">
              ${{escapeHtml(item.title)}}
            </div>

            <div class="flex items-center justify-between text-[11px] text-[var(--muted-foreground)] pt-1">
              <div class="flex items-center gap-2">
                ${{item.current_owner ? getOwnerBadge(item.current_owner) : ''}}
                <span>${{item.completed_subtasks}}/${{item.total_subtasks}} tasks</span>
              </div>
              <span class="font-medium text-gray-300">${{item.progress_percent}}%</span>
            </div>

            <!-- Mini Progress Bar -->
            <div class="w-full bg-gray-800 rounded-full h-1 overflow-hidden">
              <div
                class="${{item.status === 'Completed' ? 'bg-emerald-500' : 'bg-indigo-500'}} h-1 transition-all"
                style="width: ${{item.progress_percent}}%;"
              ></div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function renderDetail() {{
      const headerEl = document.getElementById('detail-header');
      const bodyEl = document.getElementById('detail-body');

      const item = DATA.items.find(i => i.id === selectedItemId);
      if (!item) {{
        headerEl.innerHTML = '<span class="text-xs text-gray-400">Select a work item</span>';
        bodyEl.innerHTML = '<div class="text-center text-xs text-gray-500 py-10">Select an item from the list to inspect details.</div>';
        return;
      }}

      // Render Header
      headerEl.innerHTML = `
        <div class="flex items-center gap-3">
          <span class="text-xs font-mono px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-bold">#${{String(item.number).padStart(3, '0')}}</span>
          <h2 class="text-sm font-bold text-white truncate max-w-sm sm:max-w-md">${{escapeHtml(item.title)}}</h2>
        </div>
        <div class="flex items-center gap-2">
          ${{getStatusBadge(item.status)}}
        </div>
      `;

      // Render Body
      let html = '';

      // Metadata card
      html += `
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs bg-gray-900/60 p-3.5 rounded-lg border border-[var(--border)]">
          <div>
            <span class="text-[var(--muted-foreground)] block mb-1">Current Owner:</span>
            <div class="font-medium text-white">${{item.current_owner ? getOwnerBadge(item.current_owner) : '<span class="text-gray-500">Unassigned</span>'}}</div>
          </div>
          <div>
            <span class="text-[var(--muted-foreground)] block mb-1">Directory:</span>
            <code class="text-gray-300 font-mono text-[11px]">${{escapeHtml(item.relative_path)}}</code>
          </div>
          ${{item.handoff_state ? `
            <div class="sm:col-span-2 mt-1">
              <span class="text-[var(--muted-foreground)] block mb-1">Handoff State:</span>
              <span class="text-blue-300 font-medium">${{escapeHtml(item.handoff_state)}}</span>
            </div>
          ` : ''}}
          ${{item.active_handoffs ? `
            <div class="sm:col-span-2">
              <span class="text-[var(--muted-foreground)] block mb-1">Active Handoffs:</span>
              <span class="text-gray-300">${{escapeHtml(item.active_handoffs)}}</span>
            </div>
          ` : ''}}
        </div>
      `;

      // Goal / Objective
      if (item.goal) {{
        html += `
          <div>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-1.5">
              <span>🎯</span> Objective & Goal
            </h3>
            <div class="bg-[var(--card)] p-3.5 rounded-lg border border-[var(--border)] text-xs text-gray-200 leading-relaxed">
              ${{escapeHtml(item.goal)}}
            </div>
          </div>
        `;
      }}

      // Subtasks Checklist
      html += `
        <div>
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
              <span>☑️</span> Subtasks & Checklist
            </h3>
            <span class="text-xs font-mono text-gray-400">${{item.completed_subtasks}} of ${{item.total_subtasks}} completed (${{item.progress_percent}}%)</span>
          </div>

          <div class="bg-[var(--card)] rounded-lg border border-[var(--border)] divide-y divide-[var(--border)] overflow-hidden">
      `;

      if (item.subtasks.length === 0) {{
        html += `
          <div class="p-4 text-xs text-center text-gray-500">No subtasks found in tasks.md</div>
        `;
      }} else {{
        item.subtasks.forEach((st, idx) => {{
          const isDone = st.completed;
          html += `
            <div class="p-3 flex items-start gap-3 hover:bg-gray-800/40 transition">
              <div class="mt-0.5">
                <span class="inline-flex items-center justify-center w-4 h-4 rounded text-[10px] ${{
                  isDone ? 'bg-emerald-600 text-white font-bold' : 'border border-gray-600 text-transparent'
                }}">✓</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-xs leading-snug ${{isDone ? 'line-through text-gray-500' : 'text-gray-200 font-medium'}}">
                  ${{escapeHtml(st.title)}}
                </div>
                ${{st.owner ? `<div class="mt-1">${{getOwnerBadge(st.owner)}}</div>` : ''}}
              </div>
              ${{st.contract_path ? `
                <button
                  onclick="openContract('${{item.id}}', '${{escapeHtml(st.contract_path)}}')"
                  class="shrink-0 px-2 py-1 rounded text-[11px] bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-700/60 transition"
                  title="View Contract"
                >
                  Contract
                </button>
              ` : ''}}
            </div>
          `;
        }});
      }}

      html += `
          </div>
        </div>
      `;

      // Task Contracts
      if (item.contracts && item.contracts.length > 0) {{
        html += `
          <div>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-1.5">
              <span>📄</span> Task Contracts (${{item.contracts.length}})
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        `;
        item.contracts.forEach(c => {{
          html += `
            <div
              onclick="openContractObj('${{item.id}}', '${{escapeHtml(c.filename)}}')"
              class="p-3 bg-[var(--card)] hover:bg-[var(--card-hover)] border border-[var(--border)] rounded-lg cursor-pointer transition flex flex-col justify-between"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-bold text-white truncate">${{escapeHtml(c.title || c.filename)}}</span>
                ${{c.status ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 font-medium">${{escapeHtml(c.status)}}</span>` : ''}}
              </div>
              <p class="text-[11px] text-[var(--muted-foreground)] line-clamp-2">${{escapeHtml(c.objective || 'No objective stated.')}}</p>
              ${{c.owner ? `<div class="mt-2">${{getOwnerBadge(c.owner)}}</div>` : ''}}
            </div>
          `;
        }});
        html += `
            </div>
          </div>
        `;
      }}

      // Decisions
      if (item.decisions && item.decisions.length > 0) {{
        html += `
          <div>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-1.5">
              <span>⚖️</span> Recorded Decisions (${{item.decisions.length}})
            </h3>
            <div class="space-y-2">
        `;
        item.decisions.forEach(d => {{
          html += `
            <div class="p-3 bg-[var(--card)] rounded-lg border border-[var(--border)]">
              <div class="text-xs font-semibold text-white mb-1">${{escapeHtml(d.title)}}</div>
              <p class="text-[11px] text-[var(--muted-foreground)] leading-relaxed">${{escapeHtml(d.body)}}</p>
            </div>
          `;
        }});
        html += `
            </div>
          </div>
        `;
      }}

      bodyEl.innerHTML = html;
    }}

    function selectItem(id) {{
      selectedItemId = id;
      renderList();
      renderDetail();
    }}

    function setFilter(filter) {{
      currentFilter = filter;
      document.querySelectorAll('.filter-btn').forEach(btn => {{
        btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-sm');
        btn.classList.add('bg-[var(--card)]', 'text-[var(--muted-foreground)]');
      }});
      const activeBtn = document.getElementById('filter-' + filter);
      if (activeBtn) {{
        activeBtn.classList.remove('bg-[var(--card)]', 'text-[var(--muted-foreground)]');
        activeBtn.classList.add('bg-indigo-600', 'text-white', 'shadow-sm');
      }}
      renderList();
    }}

    function handleSearch(val) {{
      searchQuery = val.trim();
      renderList();
    }}

    function openContract(itemId, contractPath) {{
      const item = DATA.items.find(i => i.id === itemId);
      if (!item) return;
      const contract = item.contracts.find(c => c.path.includes(contractPath) || contractPath.includes(c.filename));
      if (contract) {{
        showContractModal(contract);
      }} else {{
        alert('Contract file: ' + contractPath);
      }}
    }}

    function openContractObj(itemId, filename) {{
      const item = DATA.items.find(i => i.id === itemId);
      if (!item) return;
      const contract = item.contracts.find(c => c.filename === filename);
      if (contract) {{
        showContractModal(contract);
      }}
    }}

    function showContractModal(contract) {{
      document.getElementById('modal-title').textContent = contract.title || contract.filename;
      let bodyHtml = `
        <div class="space-y-3">
          <div class="flex items-center gap-2">
            ${{contract.owner ? getOwnerBadge(contract.owner) : ''}}
            ${{contract.status ? `<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-800 text-gray-300">${{escapeHtml(contract.status)}}</span>` : ''}}
          </div>
          <div>
            <h4 class="font-bold text-white uppercase text-[11px] mb-1">Objective</h4>
            <p class="leading-relaxed bg-gray-900/60 p-2.5 rounded border border-[var(--border)]">${{escapeHtml(contract.objective || 'N/A')}}</p>
          </div>
      `;

      if (contract.scope_in.length > 0) {{
        bodyHtml += `
          <div>
            <h4 class="font-bold text-emerald-400 uppercase text-[11px] mb-1">In Scope</h4>
            <ul class="list-disc list-inside space-y-1 bg-gray-900/40 p-2.5 rounded border border-[var(--border)]">
              ${{contract.scope_in.map(s => `<li>${{escapeHtml(s)}}</li>`).join('')}}
            </ul>
          </div>
        `;
      }}

      if (contract.scope_out.length > 0) {{
        bodyHtml += `
          <div>
            <h4 class="font-bold text-rose-400 uppercase text-[11px] mb-1">Out of Scope</h4>
            <ul class="list-disc list-inside space-y-1 bg-gray-900/40 p-2.5 rounded border border-[var(--border)]">
              ${{contract.scope_out.map(s => `<li>${{escapeHtml(s)}}</li>`).join('')}}
            </ul>
          </div>
        `;
      }}

      if (contract.acceptance_checks.length > 0) {{
        bodyHtml += `
          <div>
            <h4 class="font-bold text-blue-400 uppercase text-[11px] mb-1">Acceptance Checks</h4>
            <ul class="space-y-1 bg-gray-900/40 p-2.5 rounded border border-[var(--border)] font-mono text-[11px]">
              ${{contract.acceptance_checks.map(a => `<li>${{escapeHtml(a)}}</li>`).join('')}}
            </ul>
          </div>
        `;
      }}

      bodyHtml += '</div>';
      document.getElementById('modal-body').innerHTML = bodyHtml;
      document.getElementById('contract-modal').classList.remove('hidden');
    }}

    function closeModal() {{
      document.getElementById('contract-modal').classList.add('hidden');
    }}

    function escapeHtml(text) {{
      return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }}

    window.addEventListener('keydown', e => {{
      if (e.key === 'Escape') closeModal();
    }});

    renderList();
    renderDetail();
  </script>
</body>
</html>
"""
