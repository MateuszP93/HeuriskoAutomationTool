from __future__ import annotations

import argparse
import code
from pathlib import Path

from heurisko_automation.config import load_config
from heurisko_automation.locators import LocatorRegistry


def main():
    parser = argparse.ArgumentParser(prog="heurisko")
    parser.add_argument("--root", default=None, help="Project root with configs directory.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("shell", help="Open live Python shell with 'heurisko' session object.")

    run_parser = subparsers.add_parser("run", help="Run one workflow.")
    run_parser.add_argument("workflow")
    run_parser.add_argument("--param", action="append", default=[], help="Param in key=value format.")
    run_parser.add_argument("--run-id", default=None)

    queue_parser = subparsers.add_parser("run-queue", help="Run YAML queue.")
    queue_parser.add_argument("path")

    excel_parser = subparsers.add_parser("run-excel", help="Run queue from Excel.")
    excel_parser.add_argument("path")

    inspect_parser = subparsers.add_parser("inspect", help="Print loaded locators and windows.")
    inspect_parser.add_argument("--no-connect", action="store_true")

    args = parser.parse_args()

    if args.command == "inspect":
        if args.no_connect:
            config = load_config(args.root)
            locators = LocatorRegistry(config.locators)
            print("Windows:")
            for name in sorted(config.windows):
                print(f"  - {name}")
            print("Locators:")
            for name in locators.names():
                print(f"  - {name}")
            return

        from heurisko_automation.session import create_session

        session = create_session(args.root, connect=True)
        print("Windows:")
        for name in sorted(session.config.windows):
            print(f"  - {name}")
        print("Locators:")
        for name in session.locators.names():
            print(f"  - {name}")
        return

    from heurisko_automation.session import create_session

    session = create_session(args.root)

    if args.command == "shell":
        banner = (
            "Heurisko live shell\n"
            "Available objects: heurisko, session\n"
            "Example: heurisko.acc.set_irradiance(20)"
        )
        namespace = {"session": session, "heurisko": session.api}
        code.interact(banner=banner, local=namespace)
        return

    if args.command == "run":
        params = _parse_params(args.param)
        if args.run_id:
            params["run_id"] = args.run_id
        session.run_workflow(args.workflow, **params)
        return

    if args.command == "run-queue":
        session.run_queue(_resolve_path(args.path, session.config.root))
        return

    if args.command == "run-excel":
        session.run_excel(_resolve_path(args.path, session.config.root))
        return


def _parse_params(values: list[str]):
    params = {}
    for value in values:
        key, separator, raw = value.partition("=")
        if not separator:
            raise SystemExit(f"Invalid --param value: {value}. Use key=value.")
        params[key] = _coerce_value(raw)
    return params


def _coerce_value(value: str):
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _resolve_path(path: str, root: Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else root / value
