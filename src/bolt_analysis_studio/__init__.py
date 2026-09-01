"""
Bolt Analysis Studio v4.0
=========================

Comprehensive engineering software for analyzing bolted flange joints
in oil and gas applications.

Prof. Leonardo Rosa Ribeiro da Silva, PhD | January 2026

Modules:
--------
- core: MSD models, materials database, similitude analysis
- numerical: Preload loss models, friction models, time integration
- visualization: Loosening plots, dashboards
- gui: PyQt6 application interface
"""

__version__ = "4.0.0"
__author__ = "Prof. Leonardo Rosa Ribeiro da Silva, PhD"
__license__ = "Proprietary"

from . import core
from . import numerical
from . import visualization
from . import gui
