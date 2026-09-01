"""
Project I/O Module
File save/load operations for Bolt Analysis Studio v4.0

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026

Handles:
- .bap (Bolt Analysis Project) files - JSON format with all project data
- .msd (MSD Model) files - JSON format for standalone models
- Export to CSV, XLSX for results

File Format:
.bap files are gzipped JSON with structure:
{
    "version": "4.0",
    "type": "bolt_analysis_project",
    "project": {...},      # ProjectInfo
    "model": {...},        # MSDModel
    "results": {...},      # AnalysisResult (optional)
    "config": {...}        # AnalysisConfig (optional)
}
"""

import json
import gzip
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import shutil

from bolt_analysis_studio.core.app_state import (
    ProjectInfo, AnalysisResult, PreloadAnalysisResult, TimeIntegrationResult
)
from bolt_analysis_studio.core.models.model import MSDModel


# =============================================================================
# FILE FORMAT CONSTANTS
# =============================================================================

FILE_VERSION = "4.0"
FILE_TYPE_PROJECT = "bolt_analysis_project"
FILE_TYPE_MODEL = "msd_model"

FILE_EXTENSION_PROJECT = ".bap"
FILE_EXTENSION_MODEL = ".msd"

# Magic bytes for identifying compressed files
GZIP_MAGIC = b'\x1f\x8b'


# =============================================================================
# PROJECT I/O CLASS
# =============================================================================

class ProjectIO:
    """
    Handles file I/O for Bolt Analysis Studio projects.

    Supports:
    - save_project: Save complete project state to .bap file
    - load_project: Load project state from .bap file
    - save_model: Save model only to .msd file
    - load_model: Load model from .msd file
    - export_results: Export results to CSV/Excel
    """

    @staticmethod
    def save_project(
        path: str,
        project: ProjectInfo,
        model: Optional[MSDModel] = None,
        results: Optional[AnalysisResult] = None,
        config: Optional[Dict[str, Any]] = None,
        compress: bool = True
    ) -> bool:
        """
        Save complete project to .bap file.

        Args:
            path: File path (will add .bap extension if not present)
            project: ProjectInfo with project metadata
            model: Optional MSDModel
            results: Optional AnalysisResult
            config: Optional analysis configuration dict
            compress: Whether to gzip the output

        Returns:
            True if successful
        """
        try:
            # Ensure correct extension
            path = Path(path)
            if path.suffix.lower() != FILE_EXTENSION_PROJECT:
                path = path.with_suffix(FILE_EXTENSION_PROJECT)

            # Build file content
            data = {
                "version": FILE_VERSION,
                "type": FILE_TYPE_PROJECT,
                "saved": datetime.now().isoformat(),
                "project": project.to_dict() if project else {},
                "model": model.to_dict() if model else None,
                "results": results.to_dict() if results else None,
                "config": config
            }

            # Convert to JSON string
            json_str = json.dumps(data, indent=2, default=str)

            # Write file
            if compress:
                with gzip.open(path, 'wt', encoding='utf-8') as f:
                    f.write(json_str)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(json_str)

            # Update project filepath
            project.filepath = str(path)
            project.touch()

            return True

        except Exception as e:
            print(f"Error saving project: {e}")
            return False

    @staticmethod
    def load_project(
        path: str
    ) -> Tuple[Optional[ProjectInfo], Optional[MSDModel], Optional[AnalysisResult]]:
        """
        Load project from .bap file.

        Args:
            path: File path

        Returns:
            Tuple of (ProjectInfo, MSDModel, AnalysisResult) - any may be None
        """
        try:
            path = Path(path)

            if not path.exists():
                print(f"File not found: {path}")
                return None, None, None

            # Try to detect if file is gzipped
            with open(path, 'rb') as f:
                magic = f.read(2)

            if magic == GZIP_MAGIC:
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    json_str = f.read()
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    json_str = f.read()

            data = json.loads(json_str)

            # Validate file type
            if data.get("type") != FILE_TYPE_PROJECT:
                print(f"Invalid file type: {data.get('type')}")
                return None, None, None

            # Load project info
            project = None
            if data.get("project"):
                project = ProjectInfo.from_dict(data["project"])
                project.filepath = str(path)

            # Load model
            model = None
            if data.get("model"):
                model = MSDModel.from_dict(data["model"])

            # Load results (basic - full restoration is complex)
            results = None
            if data.get("results"):
                results = ProjectIO._restore_results(data["results"])

            return project, model, results

        except Exception as e:
            print(f"Error loading project: {e}")
            return None, None, None

    @staticmethod
    def _restore_results(data: Dict[str, Any]) -> Optional[AnalysisResult]:
        """Restore AnalysisResult from dictionary."""
        try:
            import numpy as np

            result = AnalysisResult(
                analysis_type=data.get("analysis_type", "none"),
                started=data.get("started", ""),
                completed=data.get("completed", "")
            )

            # Restore preload result
            if data.get("preload_result"):
                pr = data["preload_result"]
                result.preload_result = PreloadAnalysisResult(
                    cycles=np.array(pr.get("cycles", [])),
                    results={k: np.array(v) for k, v in pr.get("results", {}).items()},
                    final_preload_ratio=pr.get("final_preload_ratio", 1.0),
                    preload_loss_percent=pr.get("preload_loss_percent", 0.0),
                    cycles_to_50_percent_loss=pr.get("cycles_to_50_percent_loss"),
                    initial_preload=pr.get("initial_preload", 0.0),
                    n_cycles=pr.get("n_cycles", 0),
                    selected_models=pr.get("selected_models", [])
                )

            # Restore time integration result
            if data.get("time_result"):
                tr = data["time_result"]
                result.time_result = TimeIntegrationResult(
                    time=np.array(tr.get("time", [])),
                    displacement=np.array(tr.get("displacement", [])),
                    velocity=np.array(tr.get("velocity", [])),
                    acceleration=np.array(tr.get("acceleration", [])),
                    max_displacement=tr.get("max_displacement", 0.0),
                    max_velocity=tr.get("max_velocity", 0.0),
                    max_acceleration=tr.get("max_acceleration", 0.0),
                    method=tr.get("method", ""),
                    dt=tr.get("dt", 0.001),
                    t_end=tr.get("t_end", 1.0)
                )

            # Natural frequencies
            if data.get("natural_frequencies"):
                result.natural_frequencies = data["natural_frequencies"]

            return result

        except Exception as e:
            print(f"Error restoring results: {e}")
            return None

    @staticmethod
    def save_model(
        path: str,
        model: MSDModel,
        compress: bool = False
    ) -> bool:
        """
        Save standalone model to .msd file.

        Args:
            path: File path
            model: MSDModel to save
            compress: Whether to gzip

        Returns:
            True if successful
        """
        try:
            path = Path(path)
            if path.suffix.lower() != FILE_EXTENSION_MODEL:
                path = path.with_suffix(FILE_EXTENSION_MODEL)

            data = {
                "version": FILE_VERSION,
                "type": FILE_TYPE_MODEL,
                "saved": datetime.now().isoformat(),
                "model": model.to_dict()
            }

            json_str = json.dumps(data, indent=2, default=str)

            if compress:
                with gzip.open(path, 'wt', encoding='utf-8') as f:
                    f.write(json_str)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(json_str)

            model.filename = str(path)
            return True

        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    @staticmethod
    def load_model(path: str) -> Optional[MSDModel]:
        """
        Load model from .msd file.

        Args:
            path: File path

        Returns:
            MSDModel or None if failed
        """
        try:
            path = Path(path)

            if not path.exists():
                print(f"File not found: {path}")
                return None

            # Detect compression
            with open(path, 'rb') as f:
                magic = f.read(2)

            if magic == GZIP_MAGIC:
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    json_str = f.read()
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    json_str = f.read()

            data = json.loads(json_str)

            if data.get("type") == FILE_TYPE_MODEL:
                # Wrapped format with type field
                model = MSDModel.from_dict(data["model"])
                model.filename = str(path)
                return model
            elif data.get("type") == FILE_TYPE_PROJECT:
                # Also accept project files
                if data.get("model"):
                    model = MSDModel.from_dict(data["model"])
                    model.filename = str(path)
                    return model
            elif "elements" in data and "version" in data:
                # Direct model format (saved via MSDModel.save())
                # No wrapper, just the model data itself
                model = MSDModel.from_dict(data)
                model.filename = str(path)
                return model

            return None

        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    @staticmethod
    def export_results_csv(
        path: str,
        results: AnalysisResult
    ) -> bool:
        """
        Export results to CSV file.

        Args:
            path: Output file path
            results: AnalysisResult to export

        Returns:
            True if successful
        """
        try:
            import numpy as np
            path = Path(path)

            lines = []

            # Header
            lines.append(f"# Bolt Analysis Studio Results Export")
            lines.append(f"# Generated: {datetime.now().isoformat()}")
            lines.append(f"# Analysis Type: {results.analysis_type}")
            lines.append("")

            if results.preload_result:
                pr = results.preload_result
                lines.append("# PRELOAD LOSS ANALYSIS")
                lines.append(f"# Initial Preload: {pr.initial_preload} N")
                lines.append(f"# Final Loss: {pr.preload_loss_percent:.2f}%")
                lines.append("")

                # Header row
                model_names = list(pr.results.keys())
                lines.append("Cycle," + ",".join(model_names))

                # Data rows
                for i, N in enumerate(pr.cycles):
                    values = [str(pr.results[m][i]) for m in model_names]
                    lines.append(f"{N},{','.join(values)}")

            elif results.time_result:
                tr = results.time_result
                lines.append("# TIME INTEGRATION RESULTS")
                lines.append(f"# Method: {tr.method}")
                lines.append(f"# dt: {tr.dt} s")
                lines.append("")

                # Determine number of DOFs
                n_dof = tr.displacement.shape[1] if len(tr.displacement.shape) > 1 else 1

                # Header row
                headers = ["Time"]
                for i in range(n_dof):
                    headers.extend([f"u{i}", f"v{i}", f"a{i}"])
                lines.append(",".join(headers))

                # Data rows
                for i, t in enumerate(tr.time):
                    values = [str(t)]
                    for j in range(n_dof):
                        if n_dof == 1:
                            values.extend([
                                str(tr.displacement[i]),
                                str(tr.velocity[i]),
                                str(tr.acceleration[i])
                            ])
                        else:
                            values.extend([
                                str(tr.displacement[i, j]),
                                str(tr.velocity[i, j]),
                                str(tr.acceleration[i, j])
                            ])
                    lines.append(",".join(values))

            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))

            return True

        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False

    @staticmethod
    def get_recent_projects(max_count: int = 10) -> list:
        """
        Get list of recent project files.

        This is a stub - implementation would track recently opened files
        in a settings file.
        """
        # TODO: Implement recent files tracking
        return []

    @staticmethod
    def create_backup(path: str) -> bool:
        """
        Create backup of existing file before overwriting.

        Args:
            path: File to backup

        Returns:
            True if backup created (or file didn't exist)
        """
        try:
            path = Path(path)
            if path.exists():
                backup_path = path.with_suffix(path.suffix + ".bak")
                shutil.copy2(path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def save_project(
    path: str,
    project: ProjectInfo,
    model: Optional[MSDModel] = None,
    results: Optional[AnalysisResult] = None
) -> bool:
    """Convenience function for saving projects."""
    return ProjectIO.save_project(path, project, model, results)


def load_project(
    path: str
) -> Tuple[Optional[ProjectInfo], Optional[MSDModel], Optional[AnalysisResult]]:
    """Convenience function for loading projects."""
    return ProjectIO.load_project(path)


def save_model(path: str, model: MSDModel) -> bool:
    """Convenience function for saving models."""
    return ProjectIO.save_model(path, model)


def load_model(path: str) -> Optional[MSDModel]:
    """Convenience function for loading models."""
    return ProjectIO.load_model(path)
