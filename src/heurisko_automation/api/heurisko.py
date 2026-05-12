from __future__ import annotations

from pathlib import Path

from heurisko_automation.api.acc import AccApi


class HeuriskoApi:
    def __init__(self, runner, queue_runner):
        self.runner = runner
        self.queue_runner = queue_runner
        self.acc = AccApi(runner)

    def run_workflow(self, name: str, **params):
        return self.runner.run_workflow(name, params)

    def run_queue(self, path: str | Path):
        return self.queue_runner.run_yaml(Path(path))

    def run_excel(self, path: str | Path):
        return self.queue_runner.run_excel(Path(path))
