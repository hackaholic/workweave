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
class Comment:
    id: str
    author: str
    text: str
    created_at: str
    subtask_id: str = ""


@dataclass
class SubTask:
    id: str
    title: str
    completed: bool
    owner: str = ""
    contract_path: str = ""
    contract_title: str = ""
    comments: list[Comment] = field(default_factory=list)


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
    comments: list[Comment] = field(default_factory=list)
    notes: str = ""
    is_draft: bool = False
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

            comments: list[Comment] = []
            comments_path = folder / "comments.md"
            if comments_path.is_file():
                comm_text = comments_path.read_text(encoding="utf-8", errors="replace")
                comm_matches = re.finditer(
                    r"###\s+(?:Comment\s+([a-zA-Z0-9_-]+)|([^\n]+))\s*\n+(?:\*\*Author:\*\*\s*([^\n]+)\s*\n+)?(?:\*\*Date:\*\*\s*([^\n]+)\s*\n+)?(?:\*\*Subtask:\*\*\s*([^\n]+)\s*\n+)?([\s\S]*?)(?=\n###|\Z)",
                    comm_text,
                )
                for m in comm_matches:
                    cid = m.group(1) or f"c-{len(comments)+1}"
                    author = (m.group(3) or "User").strip()
                    date_str = (m.group(4) or "").strip()
                    st_id = (m.group(5) or "").strip()
                    body = m.group(6).strip()
                    c_obj = Comment(id=cid, author=author, text=body, created_at=date_str, subtask_id=st_id)
                    comments.append(c_obj)
                    if st_id:
                        for st in subtasks:
                            if st.id == st_id:
                                st.comments.append(c_obj)

            notes = ""
            notes_path = folder / "notes.md"
            if notes_path.is_file():
                notes = notes_path.read_text(encoding="utf-8", errors="replace").strip()

            is_draft = "draft" in status.lower() or "[draft]" in title.lower() or "(draft)" in title.lower() or (readme_path.is_file() and "[draft]" in readme_text.lower())

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
                    comments=comments,
                    notes=notes,
                    is_draft=is_draft,
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


def add_work_comment(
    target_path: Path | str,
    work_id: str,
    comment_text: str,
    author: str = "User",
    subtask_id: str = "",
) -> Comment:
    """Append a comment to comments.md in the specified work folder."""
    work_dir, _ = resolve_work_directory(target_path)
    # Find matching work folder
    target_folder = None
    for d in work_dir.iterdir():
        if d.is_dir() and (d.name == work_id or d.name.startswith(f"{work_id}-") or d.name.startswith(f"{work_id}_")):
            target_folder = d
            break

    if not target_folder:
        raise ValueError(f"Work item folder for '{work_id}' not found in {work_dir}")

    comments_file = target_folder / "comments.md"
    cid = f"c-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    subtask_line = f"**Subtask:** {subtask_id}\n" if subtask_id else ""
    entry = f"""
### Comment {cid}
**Author:** {author}
**Date:** {timestamp}
{subtask_line}
{comment_text.strip()}
"""

    if not comments_file.is_file():
        comments_file.write_text(f"# Comments & Feedback\n{entry}\n", encoding="utf-8")
    else:
        existing = comments_file.read_text(encoding="utf-8")
        comments_file.write_text(f"{existing.rstrip()}\n{entry}\n", encoding="utf-8")

    return Comment(id=cid, author=author, text=comment_text.strip(), created_at=timestamp, subtask_id=subtask_id)


def update_subtask(
    target_path: Path | str,
    work_id: str,
    subtask_id: str,
    new_title: str | None = None,
    completed: bool | None = None,
) -> bool:
    """Update a subtask's completion status or title in tasks.md."""
    work_dir, project_root = resolve_work_directory(target_path)
    target_folder = None
    for d in work_dir.iterdir():
        if d.is_dir() and (d.name == work_id or d.name.startswith(f"{work_id}-") or d.name.startswith(f"{work_id}_")):
            target_folder = d
            break

    if not target_folder:
        raise ValueError(f"Work item folder for '{work_id}' not found in {work_dir}")

    tasks_file = target_folder / "tasks.md"
    if not tasks_file.is_file():
        raise ValueError(f"tasks.md not found in {target_folder}")

    lines = tasks_file.read_text(encoding="utf-8").splitlines()
    updated = False
    new_lines = []

    clean_sub_id = re.sub(r"[^a-zA-Z0-9_-]", "-", subtask_id.strip()).strip("-").lower()
    for line in lines:
        st = parse_subtask_line(line, target_folder, project_root)
        if st and (st.id == subtask_id or st.id.lower() == clean_sub_id or re.sub(r"[^a-zA-Z0-9_-]", "-", st.title[:32]).strip("-").lower() == clean_sub_id):
            # Found the target line
            curr_done = completed if completed is not None else st.completed
            check_char = "x" if curr_done else " "
            
            # Format title
            title_to_use = new_title.strip() if new_title is not None else st.title
            
            # Preserve contract link if present in original line
            link_match = re.search(r"(\[[^\]]+\]\([^)]+\.md\))", line)
            contract_suffix = f" {link_match.group(1)}" if link_match and link_match.group(1) not in title_to_use else ""
            
            # Preserve owner prefix if present
            owner_prefix = f"{st.owner}: " if st.owner and not title_to_use.startswith(f"{st.owner}:") else ""

            new_line = f"- [{check_char}] {owner_prefix}{title_to_use}{contract_suffix}".strip()
            new_lines.append(new_line)
            updated = True
        else:
            new_lines.append(line)

    if updated:
        tasks_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    return updated


def create_subtask(
    target_path: Path | str,
    work_id: str,
    title: str,
    owner: str = "",
) -> SubTask:
    """Append a new subtask to tasks.md in the specified work folder."""
    work_dir, project_root = resolve_work_directory(target_path)
    target_folder = None
    for d in work_dir.iterdir():
        if d.is_dir() and (d.name == work_id or d.name.startswith(f"{work_id}-") or d.name.startswith(f"{work_id}_")):
            target_folder = d
            break

    if not target_folder:
        raise ValueError(f"Work item folder for '{work_id}' not found in {work_dir}")

    tasks_file = target_folder / "tasks.md"
    owner_prefix = f"{owner}: " if owner else ""
    clean_title = title.strip()
    new_line = f"- [ ] {owner_prefix}{clean_title}"

    if not tasks_file.is_file():
        tasks_file.write_text(f"# Tasks\n\n## Pending\n\n{new_line}\n", encoding="utf-8")
    else:
        content = tasks_file.read_text(encoding="utf-8")
        # Try to append under ## Pending or ## In Progress or at the end
        if "## Pending" in content:
            parts = content.split("## Pending", 1)
            content = f"{parts[0]}## Pending\n\n{new_line}\n{parts[1].lstrip()}"
        elif "## In Progress" in content:
            parts = content.split("## In Progress", 1)
            content = f"{parts[0]}## In Progress\n\n{new_line}\n{parts[1].lstrip()}"
        else:
            content = f"{content.rstrip()}\n\n{new_line}\n"
        tasks_file.write_text(content, encoding="utf-8")

    st = parse_subtask_line(new_line, target_folder, project_root)
    if not st:
        st_id = re.sub(r"[^a-zA-Z0-9_-]", "-", clean_title[:32]).strip("-")
        st = SubTask(id=st_id, title=clean_title, completed=False, owner=owner)
    return st


def create_work_item(
    target_path: Path | str,
    title: str,
    description: str = "",
    is_draft: bool = True,
    owner: str = "Unassigned",
) -> str:
    """Create a new work item folder and append to INDEX.md.

    Returns the created folder name (e.g. 'work-004-user-draft').
    """
    work_dir, _ = resolve_work_directory(target_path)
    work_dir.mkdir(parents=True, exist_ok=True)

    # Find highest number
    max_num = 0
    for d in work_dir.iterdir():
        if d.is_dir() and d.name.startswith("work-"):
            m = re.match(r"work-(\d+)", d.name)
            if m:
                max_num = max(max_num, int(m.group(1)))

    next_num = max_num + 1
    num_str = f"{next_num:03d}"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")[:30]
    if not slug:
        slug = "draft"
    folder_name = f"work-{num_str}-{slug}"
    work_folder = work_dir / folder_name
    work_folder.mkdir(parents=True, exist_ok=True)
    (work_folder / "tasks").mkdir(exist_ok=True)

    # Status: Draft if user created without AI scaffolding, else Pending
    status = "Pending [Draft]" if is_draft else "Pending"
    clean_title = f"[Draft] {title.strip()}" if is_draft and not title.lower().startswith("[draft]") else title.strip()

    # Create README.md
    readme_content = f"""# Work {num_str} — {title.strip()}

{'**[User Draft — Needs AI Scaffolding]**' if is_draft else ''}

## Goal
{description.strip() or 'User-submitted task backlog item.'}

## Background & Raw Notes
{description.strip() or 'No additional notes provided.'}
"""
    (work_folder / "README.md").write_text(readme_content.strip() + "\n", encoding="utf-8")

    # Create coordination.md
    coord_content = f"""# Work {num_str} Coordination

## Current handoffs
- Current Owner: {owner}
- Status: {'Draft / Needs Scaffolding' if is_draft else 'Pending'}
- Active Task: None

## Return protocol
The assigned agent updates tasks.md, contracts in tasks/, and coordination.md before handoff.
"""
    (work_folder / "coordination.md").write_text(coord_content.strip() + "\n", encoding="utf-8")

    # Create tasks.md
    tasks_content = f"""# Work {num_str} Tasks

## Pending
- [ ] {next_num}.1 Initial review and scoping

## Completed
None.
"""
    (work_folder / "tasks.md").write_text(tasks_content.strip() + "\n", encoding="utf-8")

    # Create decisions.md
    (work_folder / "decisions.md").write_text(f"# Work {num_str} Decisions\n\nNo decisions recorded yet.\n", encoding="utf-8")

    # Create notes.md
    notes_content = f"""# Work {num_str} Notes

## Raw User Input
{description.strip()}
"""
    (work_folder / "notes.md").write_text(notes_content.strip() + "\n", encoding="utf-8")

    # Update work/INDEX.md
    index_file = work_dir / "INDEX.md"
    index_entry = f"- **Work {num_str} — {clean_title}** · {status} · [work folder]({folder_name}/)\n"
    if not index_file.is_file():
        index_file.write_text(f"# Active Work\n\n{index_entry}", encoding="utf-8")
    else:
        existing_index = index_file.read_text(encoding="utf-8")
        index_file.write_text(f"{existing_index.rstrip()}\n{index_entry}", encoding="utf-8")

    return folder_name


def scaffold_draft_work(target_path: Path | str, work_id: str) -> bool:
    """Scaffold a draft user work package into formal multi-agent structure.

    Reads raw user notes and README, generates structured subtasks and contract templates,
    and updates status to 'In Progress' / 'Pending'.
    """
    work_dir, _ = resolve_work_directory(target_path)
    target_folder = None
    for d in work_dir.iterdir():
        if d.is_dir() and (d.name == work_id or d.name.startswith(f"{work_id}-") or d.name.startswith(f"{work_id}_")):
            target_folder = d
            break

    if not target_folder:
        raise ValueError(f"Work item folder for '{work_id}' not found in {work_dir}")

    # Extract number
    m = re.match(r"work-(\d+)", target_folder.name)
    num_str = m.group(1) if m else "001"
    num = int(num_str)

    readme_file = target_folder / "README.md"
    raw_text = readme_file.read_text(encoding="utf-8") if readme_file.is_file() else ""
    goal_match = re.search(r"##\s+(?:Goal|Objective)\s*\n+([^#\n][^\n]+)", raw_text)
    goal = goal_match.group(1).strip() if goal_match else "Implement requested requirements."

    # Extract clean title from README or folder name
    first_line = raw_text.splitlines()[0] if raw_text.splitlines() else target_folder.name
    clean_title = re.sub(r"^#\s*Work\s*\d+\s*[—–-]\s*", "", first_line).replace("[Draft]", "").strip()
    if not clean_title:
        clean_title = target_folder.name.replace("-", " ").title()

    # Write formal README.md
    formal_readme = f"""# Work {num_str} — {clean_title}

## Goal
{goal}

## Scope
- Core architecture and implementation of {clean_title}
- Unit and integration tests
- Verification and documentation

## Non-Goals
- Unrelated feature refactoring

## Architecture & Context
Formally scaffolded from user requirements. Work contracts are maintained in `tasks/`.
"""
    readme_file.write_text(formal_readme.strip() + "\n", encoding="utf-8")

    # Generate task contracts in tasks/
    tasks_dir = target_folder / "tasks"
    tasks_dir.mkdir(exist_ok=True)
    c1_file = tasks_dir / f"task-{num}.1.md"
    c1_content = f"""# Task Contract: {num}.1 Implementation Plan & Core Setup

**Owner:** Antigravity
**Status:** In Progress

## Objective
Design architecture and establish core implementation for {clean_title}.

## Scope
- In scope:
  - Technical design and data schema
  - Implementation of primary modules
- Out of scope:
  - Third-party external deployments

## Acceptance Criteria
- [ ] Core module functions as specified
- [ ] Unit tests pass cleanly
"""
    c1_file.write_text(c1_content.strip() + "\n", encoding="utf-8")

    # Generate tasks.md with contract link
    tasks_file = target_folder / "tasks.md"
    tasks_content = f"""# Work {num_str} Tasks

## In Progress
- [ ] Antigravity: {num}.1 Implementation and core setup [contract](tasks/task-{num}.1.md)

## Pending
- [ ] {num}.2 Automated test coverage and regression checks
- [ ] {num}.3 Final review and documentation signoff

## Completed
None.
"""
    tasks_file.write_text(tasks_content.strip() + "\n", encoding="utf-8")

    # Update coordination.md
    coord_file = target_folder / "coordination.md"
    coord_content = f"""# Work {num_str} Coordination

## Current handoffs
- Current Owner: Antigravity
- Status: Active
- Active Task: tasks/task-{num}.1.md

## Return protocol
Update task contracts, tasks.md, and notes.md before returning or handing off.
"""
    coord_file.write_text(coord_content.strip() + "\n", encoding="utf-8")

    # Update INDEX.md to remove [Draft] and set to 'In Progress'
    index_file = work_dir / "INDEX.md"
    if index_file.is_file():
        index_lines = index_file.read_text(encoding="utf-8").splitlines()
        new_index_lines = []
        for line in index_lines:
            if target_folder.name in line or f"Work {int(num_str)}" in line:
                # Replace with clean title and In Progress
                new_line = f"- **Work {num_str} — {clean_title}** · In Progress · [work folder]({target_folder.name}/)"
                new_index_lines.append(new_line)
            else:
                new_index_lines.append(line)
        index_file.write_text("\n".join(new_index_lines) + "\n", encoding="utf-8")

    return True

