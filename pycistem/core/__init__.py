try:
    from pycistem.core.core import *
except ImportError:
    import warnings
    warnings.warn(
        "pycistem.core C++ extension is not available. "
        "Functionality requiring core (EulerSearch, ParameterMap, Project, etc.) will raise ImportError. "
        "To build with core support, ensure cisTEM, wxWidgets, and FFTW are installed, then reinstall pycistem from source.",
        ImportWarning,
        stacklevel=2,
    )
