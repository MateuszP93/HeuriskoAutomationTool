from __future__ import annotations


class LocatorNode:
    def __init__(self, runner, name: str, full_name: str | None = None, parent=None):
        self._runner = runner
        self._name = name
        self._full_name = full_name
        self._parent = parent
        self._children: dict[str, LocatorNode] = {}

    def add_child(self, name: str, full_name: str | None = None):
        child = self._children.get(name)
        if child is None:
            child = LocatorNode(self._runner, name, full_name=full_name, parent=self)
            self._children[name] = child
        elif full_name is not None:
            child._full_name = full_name
        return child

    def click(self):
        return self.path()

    def click_self(self):
        if self._full_name is None:
            raise AttributeError(f"Locator group cannot be clicked directly: {self._name}")
        return self._runner.click(self._full_name)

    def click_no_focus(self):
        if self._full_name is None:
            raise AttributeError(f"Locator group cannot be clicked directly: {self._name}")
        return self._runner.click_no_focus(self._full_name)

    def path(self):
        names = []
        node = self
        while node is not None:
            if node._full_name is not None:
                names.append(node._full_name)
            node = node._parent
        return self._runner.click_path(list(reversed(names)))

    def children(self):
        return sorted(self._children)

    def __call__(self):
        return self.path()

    def __getattr__(self, name: str):
        try:
            return self._children[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(self._children))

    def __repr__(self):
        return f"LocatorNode(name={self._name!r}, full_name={self._full_name!r})"


class LocatorTree:
    def __init__(self, runner, locator_names: list[str]):
        self.root = LocatorNode(runner, "root")
        for locator_name in locator_names:
            self._add(locator_name)

    def _add(self, locator_name: str):
        node = self.root
        parts = locator_name.split(".")
        for index, part in enumerate(parts):
            full_name = ".".join(parts[: index + 1])
            node = node.add_child(part, full_name=full_name)

    def __getattr__(self, name: str):
        return getattr(self.root, name)

    def __dir__(self):
        return dir(self.root)
