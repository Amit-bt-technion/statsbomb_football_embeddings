"""
Event Validation Module

Provides classes for validating tokenized football event vectors and sequences.
"""

from tokenizer.validation.validator import EventValidator, StrictnessLevel
from tokenizer.validation.report import (
    ValidationReport,
    ValidationIssue,
    IssueSeverity,
    SequenceValidationReport,
)

__all__ = [
    "EventValidator",
    "StrictnessLevel",
    "ValidationReport",
    "ValidationIssue",
    "IssueSeverity",
    "SequenceValidationReport",
]

