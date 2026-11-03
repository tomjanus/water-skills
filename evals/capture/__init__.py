"""Capture adapters for recording eval trials.

Capture adapters write artifacts and metadata. They do not grade results;
``evals.runner`` remains the grading interface.
"""

from .base import CaptureAdapter
from .cli import CLICaptureAdapter
from .manual import ManualCaptureAdapter

__all__ = ["CaptureAdapter", "CLICaptureAdapter", "ManualCaptureAdapter"]
