from __future__ import annotations


class AccApi:
    def __init__(self, runner):
        self.runner = runner

    def open_set_irradiance(self):
        context = self.runner.run_workflow("acc_open_set_irradiance", {"run_id": "manual_open"})
        return context.get("input")

    def set_irradiance(self, value, run_id: str | None = None, wait_done: bool = False):
        params = {
            "irradiance": value,
            "run_id": run_id or f"manual_set_irradiance_{value}",
        }
        original_monitor = self.runner.monitor
        if not wait_done:
            self.runner.monitor = None
        try:
            return self.runner.run_workflow("acc_set_irradiance", params)
        finally:
            self.runner.monitor = original_monitor
