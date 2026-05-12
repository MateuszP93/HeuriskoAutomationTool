from __future__ import annotations

from pathlib import Path

from heurisko_automation.api.acc import AccApi
from heurisko_automation.api.locators import LocatorTree


class HeuriskoApi:
    def __init__(self, runner, queue_runner):
        self.runner = runner
        self.queue_runner = queue_runner
        self.acc = AccApi(runner)
        self._locator_tree = LocatorTree(runner, runner.locators.names())

    def run_workflow(self, name: str, **params):
        return self.runner.run_workflow(name, params)

    def open_set_irradiance(self):
        return self.acc.open_set_irradiance()

    def open_set_irradiance_dialog(self):
        return self.acc.open_set_irradiance()

    def click(self, locator_name: str):
        return self.runner.click(locator_name)

    def click_no_focus(self, locator_name: str):
        return self.runner.click_no_focus(locator_name)

    def click_path(self, locator_names: list[str] | tuple[str, ...]):
        return self.runner.click_path(locator_names)

    def mouse_position(self) -> tuple[int, int]:
        return self.runner.app.mouse_position()

    def list_windows(self):
        return self.runner.app.list_windows()

    def wait_window(self, name: str, timeout: float | None = None):
        return self.runner.windows.get(name).wait_until_ready(timeout=timeout)

    def write(self, value):
        return self.runner.app.write(value)

    def press(self, key: str):
        return self.runner.app.press(key)

    def hotkey(self, *keys: str):
        return self.runner.app.hotkey(*keys)

    def clear(self):
        self.hotkey("ctrl", "a")
        return self.press("backspace")

    def run_queue(self, path: str | Path):
        return self.queue_runner.run_yaml(Path(path))

    def run_excel(self, path: str | Path):
        return self.queue_runner.run_excel(Path(path))

    def __getattr__(self, name: str):
        return getattr(self._locator_tree, name)

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(dir(self._locator_tree)))
