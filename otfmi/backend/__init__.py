# Copyright 2016-2026 EDF Phimeca

"""FMI backend abstraction layer.

This subpackage provides a common interface for different FMU simulation
backends. pyfmi is preferred if available, otherwise fmpy is used as a
fallback, similar to matplotlib backends.

Each backend module (``pyfmi_backend``, ``fmpy_backend``) exposes the same
API. The best available backend is selected at import time and re-exported
here.

Use ``use_backend`` to switch between backends at runtime.
"""

import importlib

# Available backends, in order of preference: pyfmi is preferred over fmpy.
_BACKEND_MODULES = {
    "pyfmi": ".pyfmi_backend",
    "fmpy": ".fmpy_backend",
}

# The active backend module, resolved on first use.
_backend = None


def _auto_select_backend():
    """Select the first available backend, preferring pyfmi over fmpy."""
    global _backend
    if _backend is not None:
        return
    errors = []
    for name, module in _BACKEND_MODULES.items():
        try:
            _backend = importlib.import_module(module, __name__)
        except ImportError as exc:
            errors.append(f"{name}: {exc}")
        else:
            return
    raise ImportError(
        "otfmi requires an FMI backend, but none could be imported. "
        "Install either pyfmi or fmpy.\n" + "\n".join(errors)
    )


def get_backend(name=None):
    """Get a backend module without switching the active backend.

    Parameters
    ----------
    name : str or None
        Backend name, either "pyfmi" or "fmpy". The active backend is
        returned when None.
    """
    if name is None:
        _auto_select_backend()
        return _backend
    if name not in _BACKEND_MODULES:
        raise ValueError(
            f"Unknown backend: {name}. "
            f"Available backends: {', '.join(map(repr, _BACKEND_MODULES))}"
        )
    try:
        return importlib.import_module(_BACKEND_MODULES[name], __name__)
    except ImportError as exc:
        raise ImportError(f"The {name} backend is not available: {exc}")


def use_backend(name):
    """Switch the FMI backend.

    Similar to matplotlib's ``matplotlib.use()``, this function allows
    switching between available FMI backends at runtime.

    Parameters
    ----------
    name : str
        Backend name, either "pyfmi" or "fmpy".

    Raises
    ------
    ValueError
        If the backend name is not recognized.
    ImportError
        If the requested backend is not available.

    Examples
    --------
    >>> import otfmi
    >>> otfmi.use_backend("fmpy")  # doctest: +SKIP
    >>> otfmi.backend.BACKEND  # doctest: +SKIP
    'fmpy'
    """
    global _backend
    if name not in _BACKEND_MODULES:
        raise ValueError(
            f"Unknown backend: {name}. "
            f"Available backends: {', '.join(map(repr, _BACKEND_MODULES))}"
        )
    try:
        _backend = importlib.import_module(_BACKEND_MODULES[name], __name__)
    except ImportError as exc:
        raise ImportError(f"The {name} backend is not available: {exc}")


def __getattr__(name):
    """Dynamically access attributes from the current backend."""
    _auto_select_backend()
    return getattr(_backend, name)


def __dir__():
    """Return the attributes of the current backend."""
    _auto_select_backend()
    return dir(_backend)
