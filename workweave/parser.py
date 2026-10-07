"""WorkWeave Parser: Discovers, parses, and aggregates multi-agent work folders."""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class TaskContract:
    path: str
    filename: str
    title: str = ""
    owner: str = ""
    status: str = ""
    objective: str = ""
    scope_in: list[str] = field(default_factory=list)
    scope_out: list[str] = field(default_factory=list)
    acceptance_checks: list[str] = field(default_factory=list)


@dataclass
class SubTask:
    id: str
    title: str
    completed: bool
    owner: str = ""
    contract_path: str = ""
    contract_title: str = ""


@dataclass
class WorkItem:
    id: str
    number: int
    title: str
    status: str  # "Completed", "In Progress", "Pending", "Blocked"
    folder_name: str
    relative_path: str
    goal: str = ""
    current_owner: str = ""
    active_handoffs: str = ""
    handoff_state: str = ""
    subtasks: list[SubTask] = field(default_factory=list)
    decisions: list[dict[str, str]] = field(default_factory=list)
    contracts: list[TaskContract] = field(default_factory=list)
    total_subtasks: int = 0
    completed_subtasks: int = 0
    progress_percent: int = 0


@dataclass
class WorkflowState:
    project_name: str
    target_path: str
    generated_at: str
    total_work_items: int
    completed_items: int
    in_progress_items: int
    pending_items: int
    blocked_items: int
    total_subtasks: int
    completed_subtasks: int
    overall_progress_percent: int
    items: list[WorkItem] = field(default_factory=list)


def resolve_work_directory(target_path: Path | str) -> tuple[Path, Path]:
    """Resolve the working directory and effective project root.

    Returns:
        tuple[Path, Path]: (resolved_work_dir, project_root)
    """
    path = Path(target_path).resolve()
    if not path.exists():
        return path, path

    # Case 1: Pointed directly at a work directory with INDEX.md or work-* folders or named 'work'
    if (
        (path / "INDEX.md").is_file()
        or any(d.is_dir() and d.name.startswith("work-") for d in path.iterdir() if d.is_dir())
        or path.name == "work"
    ):
        return path, path.parent

    # Case 2: Pointed at a project root with a ./work subdirectory
    work_subdir = path / "work"
    if work_subdir.is_dir():
        return work_subdir, path

    # Fallback: treat path as work dir
    return path, path


def parse_subtask_line(line: str, work_folder: Path, project_root: Path) -> SubTask | None:
    match = re.match(r"^[-*]\s+\[([ xX])\]\s*(.*)$", line.strip())
    if not match:
        return None

    completed = match.group(1).lower() == "x"
    raw_text = match.group(2).strip()

    contract_path = ""
    contract_title = ""
    link_match = re.search(r"\[([^\]]+)\]\(([^)]+\.md)\)", raw_text)
    if link_match:
        contract_title = link_match.group(1)
        rel_contract = link_match.group(2)
        resolved_contract = (work_folder / rel_contract).resolve()
        try:
            contract_path = str(resolved_contract.relative_to(project_root))
        except ValueError:
            contract_path = rel_contract

    # Extract owner if specified (e.g. Gemini, Codex, Claude, GPT, Owner)
    owner = ""
    owner_match = re.search(r"(?:^|\s)(Gemini|Codex|Claude|GPT|Owner|Antigravity)(?:\s*\+\s*(Gemini|Codex|Claude|GPT|Owner|Antigravity))?:", raw_text)
    if owner_match:
        owner = owner_match.group(0).rstrip(":")

    display_title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw_text).strip()
    subtask_id = re.sub(r"[^a-zA-Z0-9_-]", "-", display_title[:32]).strip("-")

    return SubTask(
        id=subtask_id,
        title=display_title,
        completed=completed,
        owner=owner,
        contract_path=contract_path,
        contract_title=contract_title,
    )


def parse_task_contract(contract_file: Path, project_root: Path) -> TaskContract:
    try:
        rel_path = str(contract_file.relative_to(project_root))
    except ValueError:
        rel_path = contract_file.name

    contract = TaskContract(
        path=rel_path,
        filename=contract_file.name,
    )
    if not contract_file.is_file():
        return contract

    content = contract_file.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    current_section = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            contract.title = stripped[2:].strip()
            continue

        if stripped.startswith("**Owner:**"):
            contract.owner = stripped.replace("**Owner:**", "").strip()
            continue

        if stripped.startswith("**Status:**"):
            contract.status = stripped.replace("**Status:**", "").strip()
            continue

        if stripped.startswith("## "):
            current_section = stripped[3:].strip().lower()
            continue

        if current_section == "objective" and stripped and not stripped.startswith("#"):
            if not contract.objective:
                contract.objective = stripped
            else:
                contract.objective += " " + stripped

        if current_section == "scope":
            if stripped.startswith("- In scope:") or stripped.startswith("- In scope"):
                continue
            elif stripped.startswith("- Out of scope:") or stripped.startswith("- Out of scope"):
                current_section = "scope_out"
            elif stripped.startswith("- ") or stripped.startswith("* "):
                contract.scope_in.append(stripped[2:].strip())

        if current_section == "scope_out":
            if stripped.startswith("- ") or stripped.startswith("* "):
                contract.scope_out.append(stripped[2:].strip())

        if "acceptance" in current_section:
            if stripped.startswith("- [ ]") or stripped.startswith("- [x]"):
                contract.acceptance_checks.append(stripped)

    return contract


def parse_work_directory(target_path: Path | str, project_title: str | None = None) -> WorkflowState:
    work_dir, project_root = resolve_work_directory(target_path)

    # Determine display project name
    if project_title:
        project_name = project_title
    else:
        project_name = project_root.name.replace("-", " ").replace("_", " ").title()
        if project_name.lower() in ("work", ".", ""):
            project_name = "Workflow"

    index_file = work_dir / "INDEX.md"
    index_items: dict[str, dict[str, Any]] = {}

    if index_file.is_file():
        index_content = index_file.read_text(encoding="utf-8", errors="replace")
        for line in index_content.splitlines():
            match = re.search(
                r"-\s+\*\*Work\s+(\d+)\s+[—–-]\s+([^*]+)\*\*\s+·\s+([^·]+?)\s+·\s+\[work folder\]\(([^)]+)\)",
                line,
            )
            if match:
                num_str, title, status_raw, folder = match.groups()
                item_id = f"work-{int(num_str):03d}"
                status = "Pending"
                if "Completed" in status_raw:
                    status = "Completed"
                elif "In Progress" in status_raw:
                    status = "In Progress"
                elif "Blocked" in status_raw:
                    status = "Blocked"

                index_items[item_id] = {
                    "number": int(num_str),
                    "title": title.strip(),
                    "status": status,
                    "folder": folder.strip("/"),
                }

    work_items: list[WorkItem] = []
    if work_dir.is_dir():
        discovered_dirs = sorted([d for d in work_dir.iterdir() if d.is_dir() and d.name.startswith("work-")])

        for folder in discovered_dirs:
            folder_match = re.match(r"work-(\d+)", folder.name)
            if not folder_match:
                continue
            num = int(folder_match.group(1))
            item_id = f"work-{num:03d}"

            index_info = index_items.get(item_id, {})
            title = index_info.get("title", folder.name.replace("-", " ").title())
            status = index_info.get("status", "Pending")

            goal = ""
            readme_path = folder / "README.md"
            if readme_path.is_file():
                readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
                goal_match = re.search(r"##\s+(?:Goal|Objective)\s*\n+([^#\n][^\n]+)", readme_text)
                if goal_match:
                    goal = goal_match.group(1).strip()
                else:
                    first_lines = [l.strip() for l in readme_text.splitlines() if l.strip() and not l.startswith("#")]
                    if first_lines:
                        goal = first_lines[0]

            current_owner = ""
            active_handoffs = ""
            handoff_state = ""
            coord_path = folder / "coordination.md"
            if coord_path.is_file():
                coord_text = coord_path.read_text(encoding="utf-8", errors="replace")
                owner_m = re.search(r"\*\*Current owner:\*\*\s*([^\n]+)", coord_text)
                if owner_m:
                    current_owner = owner_m.group(1).strip()
                handoff_m = re.search(r"\*\*Active cross-agent handoffs:\*\*\s*([^\n]+)", coord_text)
                if handoff_m:
                    active_handoffs = handoff_m.group(1).strip()
                state_m = re.search(r"\*\*Handoff state:\*\*\s*([^\n]+)", coord_text)
                if state_m:
                    handoff_state = state_m.group(1).strip()

            subtasks: list[SubTask] = []
            tasks_path = folder / "tasks.md"
            if tasks_path.is_file():
                tasks_text = tasks_path.read_text(encoding="utf-8", errors="replace")
                for line in tasks_text.splitlines():
                    subtask = parse_subtask_line(line, folder, project_root)
                    if subtask:
                        subtasks.append(subtask)

            decisions: list[dict[str, str]] = []
            decisions_path = folder / "decisions.md"
            if decisions_path.is_file():
                dec_text = decisions_path.read_text(encoding="utf-8", errors="replace")
                dec_matches = re.findall(r"##\s+([^\n]+)\n+([\s\S]*?)(?=\n##|\Z)", dec_text)
                for d_title, d_body in dec_matches:
                    decisions.append({
                        "title": d_title.strip(),
                        "body": d_body.strip()[:300] + ("..." if len(d_body.strip()) > 300 else ""),
                    })

            contracts: list[TaskContract] = []
            tasks_subdir = folder / "tasks"
            if tasks_subdir.is_dir():
                for c_file in sorted(tasks_subdir.glob("*.md")):
                    if c_file.name != "README.md":
                        contracts.append(parse_task_contract(c_file, project_root))

            total_sub = len(subtasks)
            completed_sub = sum(1 for st in subtasks if st.completed)
            progress_pct = round((completed_sub / total_sub * 100)) if total_sub > 0 else (100 if status == "Completed" else 0)

            try:
                rel_folder = str(folder.relative_to(project_root))
            except ValueError:
                rel_folder = folder.name

            work_items.append(
                WorkItem(
                    id=item_id,
                    number=num,
                    title=title,
                    status=status,
                    folder_name=folder.name,
                    relative_path=rel_folder,
                    goal=goal,
                    current_owner=current_owner,
                    active_handoffs=active_handoffs,
                    handoff_state=handoff_state,
                    subtasks=subtasks,
                    decisions=decisions,
                    contracts=contracts,
                    total_subtasks=total_sub,
                    completed_subtasks=completed_sub,
                    progress_percent=progress_pct,
                )
            )

    total_items = len(work_items)
    completed_items = sum(1 for item in work_items if item.status == "Completed")
    in_progress_items = sum(1 for item in work_items if item.status == "In Progress")
    pending_items = sum(1 for item in work_items if item.status == "Pending")
    blocked_items = sum(1 for item in work_items if item.status == "Blocked")

    global_total_sub = sum(item.total_subtasks for item in work_items)
    global_completed_sub = sum(item.completed_subtasks for item in work_items)
    overall_progress = (
        round((global_completed_sub / global_total_sub * 100))
        if global_total_sub > 0
        else round((completed_items / total_items * 100) if total_items > 0 else 0)
    )

    return WorkflowState(
        project_name=project_name,
        target_path=str(work_dir),
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        total_work_items=total_items,
        completed_items=completed_items,
        in_progress_items=in_progress_items,
        pending_items=pending_items,
        blocked_items=blocked_items,
        total_subtasks=global_total_sub,
        completed_subtasks=global_completed_sub,
        overall_progress_percent=overall_progress,
        items=work_items,
    )
