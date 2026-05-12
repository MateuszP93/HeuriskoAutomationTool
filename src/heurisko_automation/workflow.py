from __future__ import annotations

from pathlib import Path
from typing import Any

from heurisko_automation.config import read_yaml
from heurisko_automation.errors import WorkflowError


class WorkflowRunner:
    def __init__(self, config, app, locators, windows, monitor=None):
        self.config = config
        self.app = app
        self.locators = locators
        self.windows = windows
        self.monitor = monitor

    def run_workflow(self, name: str, params: dict[str, Any] | None = None):
        workflow = self._load_workflow(name)
        context: dict[str, Any] = dict(params or {})
        context.setdefault("run_id", name)

        for index, step in enumerate(workflow.get("steps", []), start=1):
            try:
                self._run_step(step, context)
            except Exception as exc:
                if step.get("optional"):
                    continue
                self._capture_error(name, index)
                raise WorkflowError(f"Workflow {name} failed at step {index}: {step}") from exc

        return context

    def click(self, locator_name: str):
        self._click_locator(locator_name)

    def click_path(self, locator_names: list[str] | tuple[str, ...]):
        for index, locator_name in enumerate(locator_names):
            self._click_locator(
                locator_name,
                focus=index == 0,
                delay=None,
            )

    def _load_workflow(self, name: str) -> dict[str, Any]:
        path = self.config.workflows_dir / f"{name}.yaml"
        workflow = read_yaml(path)
        if workflow.get("name") and workflow["name"] != name:
            raise WorkflowError(f"Workflow name mismatch in {path}: {workflow['name']} != {name}")
        return workflow

    def _run_step(self, step: dict[str, Any], context: dict[str, Any]):
        action = step["action"]

        if action == "click_path":
            self.click_path(step["path"])
            return

        if action == "click":
            window = self._resolve_window(step["window"], context)
            window.click(step["target"])
            return

        if action == "write":
            self.app.write(self._resolve_value(step, context))
            return

        if action == "wait_window":
            window_name = step["window"]
            window = self.windows.get(window_name).wait_until_ready(step.get("timeout"))
            if step.get("as"):
                context[step["as"]] = window
            return

        if action == "wait_done":
            if self.monitor is None:
                if step.get("optional"):
                    return
                raise WorkflowError("Workflow requires status monitor, but monitor is not configured.")
            run_id = context[str(step["run_id_from"])]
            self.monitor.wait_done(str(run_id), float(step.get("timeout", 300)))
            return

        raise WorkflowError(f"Unsupported action: {action}")

    def _click_locator(self, name: str, focus: bool = True, delay: float | None = None):
        locator = self.locators.get(name)
        if locator.type != "coordinate":
            raise WorkflowError(f"Unsupported locator type for {name}: {locator.type}")
        if locator.x is None or locator.y is None:
            raise WorkflowError(f"Coordinate locator {name} requires x and y")
        self.app.click_coordinate(
            locator.window,
            locator.x,
            locator.y,
            focus=focus,
            delay=locator.after_delay if locator.after_delay is not None else delay,
            relative_to=locator.relative_to,
            before_delay=locator.before_delay,
        )

        if locator.opens_window:
            self.windows.get(locator.opens_window).wait_until_ready()

    def _resolve_window(self, window_ref: str, context: dict[str, Any]):
        if window_ref in context:
            return context[window_ref]
        return self.windows.get(window_ref).wait_until_ready()

    def _resolve_value(self, step: dict[str, Any], context: dict[str, Any]):
        if "value" in step:
            return step["value"]
        if "value_from" in step:
            return context[str(step["value_from"])]
        raise WorkflowError(f"Write step requires value or value_from: {step}")

    def _capture_error(self, workflow_name: str, step_index: int):
        if not self.config.app.get("screenshot_on_error", True):
            return
        path = (
            self.config.root
            / "data"
            / "output"
            / "screenshots"
            / f"{workflow_name}_step_{step_index}_error.png"
        )
        self.app.screenshot(path)
