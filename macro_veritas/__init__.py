from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path

__all__ = ["__version__"]
__version__ = "0.16.0"

__path__ = extend_path(__path__, __name__)

SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "macro_veritas"
if SRC_PACKAGE.is_dir():
    __path__.append(str(SRC_PACKAGE))
