"""Support for writing coroutines."""

def initialized_coroutine(function):
    """Function decorator to automatically initialize a coroutine."""
    def _wrapper(*args, **kw):
        coroutine = function(*args, **kw)
        coroutine.send(None)
        return coroutine
    return _wrapper

