"""WorkWeave: Multi-Agent Workflow & Task Coordination Dashboard."""

__version__ = "1.0.0"
__all__ = [
    "WorkflowState",
    "WorkItem",
    "SubTask",
    "TaskContract",
    "parse_work_directory",
    "generate_html_dashboard",
    "run_server",
]

from workweave.dashboard import generate_html_dashboard
from workweave.parser import (
    SubTask,
    TaskContract,
    WorkItem,
    WorkflowState,
    parse_work_directory,
)
from workweave.server import run_server
