"""Runtime helpers."""

import warnings


def suppress_warnings():
    """Suppress warnings for cleaner app output."""
    warnings.filterwarnings("ignore")

