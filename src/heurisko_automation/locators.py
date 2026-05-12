from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from heurisko_automation.errors import LocatorError


@dataclass(frozen=True)
class Locator:
    name: str
    window: str
    type: str
    x: int | None = None
    y: int | None = None
    opens_window: str | None = None


class LocatorRegistry:
    def __init__(self, definitions: dict[str, Any]):
        self._locators = {
            name: Locator(
                name=name,
                window=str(definition.get("window", "main")),
                type=str(definition.get("type", "coordinate")),
                x=definition.get("x"),
                y=definition.get("y"),
                opens_window=definition.get("opens_window"),
            )
            for name, definition in definitions.items()
        }

    def get(self, name: str) -> Locator:
        try:
            return self._locators[name]
        except KeyError as exc:
            raise LocatorError(f"Unknown locator: {name}") from exc

    def names(self) -> list[str]:
        return sorted(self._locators)
