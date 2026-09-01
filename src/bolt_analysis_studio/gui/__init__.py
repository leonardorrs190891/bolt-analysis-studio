"""
Bolt Analysis Studio v4.0 - GUI Module

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026

This module provides the PyQt6-based graphical user interface for the
Bolt Analysis Studio, including:

- Main application window with 6-tab structure
- MSD Model Builder visual editor
- Property inspector panels
- Results visualization
- Report generation interface
"""

from .theme import Theme

from .main_window import (
    BoltAnalysisStudio,
    ProjectInfo,
    ProjectTab,
    ModelBuilderTab,
    SolverTab,
    ResultsTab,
    SimilitudeTab,
    ReportsTab,
)

from .msd_builder import (
    MSDBuilderWindow,
    SchematicView,
    ElementPalette,
    PropertyInspector,
    ElementGraphicsItem,
    ConnectionLine,
    ELEMENT_VISUALS,
    ElementVisual,
)


__all__ = [
    # Main Window
    'BoltAnalysisStudio',
    'Theme',
    'ProjectInfo',
    
    # Tab Widgets
    'ProjectTab',
    'ModelBuilderTab',
    'SolverTab',
    'ResultsTab',
    'SimilitudeTab',
    'ReportsTab',
    
    # MSD Builder
    'MSDBuilderWindow',
    'SchematicView',
    'ElementPalette',
    'PropertyInspector',
    'ElementGraphicsItem',
    'ConnectionLine',
    
    # Element Definitions
    'ELEMENT_VISUALS',
    'ElementVisual',
]
