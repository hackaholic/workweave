"""WorkWeave CLI: Command-line interface for WorkWeave dashboard."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from workweave import __version__
from workweave.dashboard import generate_html_dashboard
from workweave.parser import parse_work_directory
from workweave.server import run_server


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workweave",
        description="WorkWeave: Multi-Agent Workflow & Task Coordination Dashboard",
    )
    parser.add_argument(
        "--target",
        "-t",
        default=os.environ.get("WORKWEAVE_TARGET", "."),
        help="Path to project directory containing 'work/' or direct path to 'work/' folder (default: current directory or $WORKWEAVE_TARGET)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.environ.get("WORKWEAVE_PORT", "8088")),
        help="Port to run the HTTP dashboard server on (default: 8088 or $WORKWEAVE_PORT)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("WORKWEAVE_HOST", "0.0.0.0"),
        help="Host interface to bind the server on (default: 0.0.0.0 or $WORKWEAVE_HOST)",
    )
    parser.add_argument(
        "--title",
        default=os.environ.get("WORKWEAVE_TITLE", None),
        help="Custom display title for the project dashboard (default: auto-detected)",
    )
    parser.add_argument(
        "--build",
        "-o",
        metavar="OUTPUT_FILE",
        help="Export static HTML dashboard to specified output file and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output parsed workflow state as JSON to stdout and exit",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"WorkWeave v{__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    target_path = Path(args.target).resolve()

    if args.json:
        state = parse_work_directory(target_path, project_title=args.title)
        try:
            print(json.dumps(asdict(state), indent=2))
        except BrokenPipeError:
            pass
        return 0

    if args.build:
        state = parse_work_directory(target_path, project_title=args.title)
        html_content = generate_html_dashboard(state)
        output_file = Path(args.build).resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding="utf-8")
        print(f"Exported WorkWeave dashboard to: {output_file}")
        return 0

    # Default action: run server
    run_server(
        host=args.host,
        port=args.port,
        target_path=target_path,
        project_title=args.title,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
