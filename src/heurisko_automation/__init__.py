__all__ = ["create_session"]


def create_session(*args, **kwargs):
    from heurisko_automation.session import create_session as _create_session

    return _create_session(*args, **kwargs)
