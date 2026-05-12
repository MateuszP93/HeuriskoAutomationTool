from __future__ import annotations

from typing import Any

from heurisko_automation.errors import LocatorError


class ManagedWindow:
    def __init__(self, name: str, app, definition: dict[str, Any]):
        self.name = name
        self.app = app
        self.definition = definition
        self.handle = None

    def wait_until_ready(self, timeout: float | None = None):
        self.handle = self.app.wait_window(self.name, timeout=timeout)
        return self

    def click(self, target: str):
        locator = self.definition.get("locators", {}).get(target)
        if not locator:
            raise LocatorError(f"Window {self.name} has no locator named {target}")
        if locator.get("type", "coordinate") != "coordinate":
            raise LocatorError(f"Unsupported window locator type: {locator.get('type')}")
        self.app.click_coordinate(self.name, int(locator["x"]), int(locator["y"]))
        return self

    def write(self, value: Any):
        self.app.write(value)
        return self


class WindowRegistry:
    def __init__(self, app, definitions: dict[str, Any]):
        self.app = app
        self.definitions = definitions

    def get(self, name: str) -> ManagedWindow:
        return ManagedWindow(name, self.app, self.definitions[name])
