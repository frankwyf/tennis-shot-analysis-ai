"""Public package interface for tennis shot analysis."""

from importlib.metadata import PackageNotFoundError, version

from .config import AnalysisConfig
from .metrics import AnalysisSummary
from .pipeline import analyze_landmarks, run_analysis

try:
    __version__ = version("tennis-shot-analysis-ai")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = ["AnalysisConfig", "AnalysisSummary", "analyze_landmarks", "run_analysis", "__version__"]
