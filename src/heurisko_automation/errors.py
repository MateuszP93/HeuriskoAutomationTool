class HeuriskoAutomationError(Exception):
    """Base exception for framework errors."""


class ConfigError(HeuriskoAutomationError):
    pass


class WindowNotFoundError(HeuriskoAutomationError):
    pass


class WindowFocusError(HeuriskoAutomationError):
    pass


class LocatorError(HeuriskoAutomationError):
    pass


class WorkflowError(HeuriskoAutomationError):
    pass


class MonitorTimeoutError(HeuriskoAutomationError):
    pass
