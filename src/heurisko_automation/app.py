from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pyautogui
from pywinauto import Application, Desktop

from heurisko_automation.errors import WindowFocusError, WindowNotFoundError


class AppController:
    def __init__(self, config):
        self.config = config
        self.app_settings = config.app
        self.windows = config.windows
        self.backend = self.app_settings.get("backend", "win32")
        self.click_delay = float(self.app_settings.get("click_delay", 0.2))
        self.path_click_delay = float(self.app_settings.get("path_click_delay", self.click_delay))
        self.typing_delay = float(self.app_settings.get("typing_delay", 0.02))
        self.app: Application | None = None
        pyautogui.FAILSAFE = True

    def connect(self):
        main_window_name = self.app_settings.get("main_window", "main")
        main_definition = self.windows[main_window_name]
        title_regex = main_definition["title_regex"]
        self.app = Application(backend=self.backend).connect(title_re=title_regex)

        if main_definition.get("resize_on_connect", False):
            self.prepare_window(main_window_name)

        return self

    def window(self, name: str):
        if self.app is None:
            raise RuntimeError("Application is not connected. Call connect() first.")

        definition = self.windows[name]
        return self.app.window(title_re=definition["title_regex"])

    def wait_window(self, name: str, timeout: float | None = None, focus: bool = True):
        if self.app is None:
            raise RuntimeError("Application is not connected. Call connect() first.")

        definition = self.windows[name]
        wait_timeout = float(timeout or definition.get("timeout", 5))
        title_regex = definition["title_regex"]
        deadline = time.time() + wait_timeout
        last_error: Exception | None = None

        while time.time() < deadline:
            try:
                handle = self.app.window(title_re=title_regex)
                if handle.exists() and handle.is_visible() and handle.is_enabled():
                    if focus:
                        handle.set_focus()
                        time.sleep(0.15)
                        if definition.get("require_focus", True):
                            self.ensure_focused(handle, name)
                    return handle
            except Exception as exc:  # pywinauto raises several backend-specific exceptions here.
                last_error = exc
            time.sleep(0.15)

        message = f"Window not found or not ready: {name} ({title_regex})"
        if last_error:
            message = f"{message}. Last error: {last_error}"
        raise WindowNotFoundError(message)

    def prepare_window(self, name: str):
        definition = self.windows[name]
        handle = self.wait_window(name, timeout=float(definition.get("timeout", 5)))
        x = int(definition.get("x", 0))
        y = int(definition.get("y", 0))
        width = int(definition["width"])
        height = int(definition["height"])
        handle.move_window(x, y, width, height)
        time.sleep(0.2)

        rect = handle.rectangle()
        actual_width = rect.right - rect.left
        actual_height = rect.bottom - rect.top
        if actual_width != width or actual_height != height:
            raise WindowNotFoundError(
                f"Window {name} has unexpected size {actual_width}x{actual_height}; "
                f"expected {width}x{height}."
            )

        return handle

    def ensure_focused(self, handle: Any, window_name: str):
        focused = self.app.top_window() if self.app is not None else None
        if focused is None or int(focused.handle) != int(handle.handle):
            raise WindowFocusError(f"Window does not have focus: {window_name}")

    def click_coordinate(
        self,
        window_name: str,
        x: int,
        y: int,
        focus: bool = True,
        delay: float | None = None,
        relative_to: str = "window",
        before_delay: float | None = None,
        hover_delay: float | None = None,
        move_duration: float | None = None,
    ):
        if before_delay:
            time.sleep(before_delay)

        if relative_to == "screen":
            if focus:
                self.wait_window(window_name, focus=True)
            click_x = int(x)
            click_y = int(y)
        elif relative_to == "window":
            handle = self.wait_window(window_name, focus=focus)
            rect = handle.rectangle()
            click_x = rect.left + int(x)
            click_y = rect.top + int(y)
        else:
            raise ValueError(f"Unsupported coordinate reference: {relative_to}")

        pyautogui.moveTo(click_x, click_y, duration=0.05 if move_duration is None else move_duration)
        if hover_delay:
            time.sleep(hover_delay)
        pyautogui.click(click_x, click_y)
        time.sleep(self.click_delay if delay is None else delay)

    def mouse_position(self) -> tuple[int, int]:
        position = pyautogui.position()
        return int(position.x), int(position.y)

    def list_windows(self) -> list[dict[str, Any]]:
        windows = []
        for window in Desktop(backend=self.backend).windows():
            try:
                rect = window.rectangle()
                title = window.window_text()
                if not title:
                    continue
                windows.append(
                    {
                        "title": title,
                        "handle": int(window.handle),
                        "left": rect.left,
                        "top": rect.top,
                        "right": rect.right,
                        "bottom": rect.bottom,
                    }
                )
            except Exception:
                continue
        return windows

    def write(self, value: Any):
        pyautogui.write(str(value), interval=self.typing_delay)
        time.sleep(self.click_delay)
        return self

    def hotkey(self, *keys: str):
        pyautogui.hotkey(*keys)
        time.sleep(self.click_delay)
        return self

    def press(self, key: str):
        pyautogui.press(key)
        time.sleep(self.click_delay)
        return self

    def screenshot(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        pyautogui.screenshot(str(path))
