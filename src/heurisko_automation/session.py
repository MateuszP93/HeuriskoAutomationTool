from __future__ import annotations

from pathlib import Path

from heurisko_automation.api.heurisko import HeuriskoApi
from heurisko_automation.app import AppController
from heurisko_automation.config import RuntimeConfig, load_config
from heurisko_automation.locators import LocatorRegistry
from heurisko_automation.monitor import FileDoneMonitor
from heurisko_automation.queue import QueueRunner
from heurisko_automation.windows import WindowRegistry
from heurisko_automation.workflow import WorkflowRunner


class HeuriskoSession:
    def __init__(self, config: RuntimeConfig, connect: bool = True):
        self.config = config
        self.app = AppController(config)
        if connect:
            self.app.connect()

        self.locators = LocatorRegistry(config.locators)
        self.windows = WindowRegistry(self.app, config.windows)
        self.monitor = self._create_monitor()
        self.runner = WorkflowRunner(config, self.app, self.locators, self.windows, self.monitor)
        self.queue = QueueRunner(self.runner)
        self.api = HeuriskoApi(self.runner, self.queue)
        self.acc = self.api.acc

    def _create_monitor(self):
        settings = self.config.status_monitor
        if not settings.get("file"):
            return None
        return FileDoneMonitor(
            path=self.config.root / settings["file"],
            done_marker=settings.get("done_marker", "$$DONE$$"),
            poll_interval=float(settings.get("poll_interval", 0.2)),
            stable_delay=float(settings.get("stable_delay", 0.3)),
        )

    def run_workflow(self, name: str, **params):
        return self.runner.run_workflow(name, params)

    def click(self, locator_name: str):
        return self.runner.click(locator_name)

    def click_path(self, locator_names: list[str] | tuple[str, ...]):
        return self.runner.click_path(locator_names)

    def run_queue(self, path: str | Path):
        return self.queue.run_yaml(Path(path))

    def run_excel(self, path: str | Path):
        return self.queue.run_excel(Path(path))


def create_session(root: str | Path | None = None, connect: bool = True) -> HeuriskoSession:
    return HeuriskoSession(load_config(root), connect=connect)
