"""
Validation Report Data Structures

This module defines the data structures used to report validation results.
These structures provide a standardized way to communicate validation outcomes,
including detailed issue descriptions, severity levels, and human-readable explanations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class IssueSeverity(Enum):
    """
    Severity levels for validation issues.

    Used to categorize the importance of detected problems:
    - ERROR: Critical issue that definitely indicates invalid data
    - WARNING: Potential issue that may indicate invalid data depending on context
    - INFO: Informational note that doesn't necessarily indicate a problem
    """
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """
    Represents a single validation issue detected during event analysis.

    Attributes:
        code: A unique identifier for the issue type (e.g., "INVALID_EVENT_TYPE")
        message: Human-readable description of the issue
        severity: The severity level (ERROR, WARNING, INFO)
        field_name: The name of the field/feature that has the issue (if applicable)
        field_index: The index in the 128-dimensional vector (if applicable)
        expected_value: What value was expected (for range/category validation)
        actual_value: What value was actually found
        explanation: Detailed human-readable explanation of why this is an issue
                    and what it means in the context of football events
    """
    code: str
    message: str
    severity: IssueSeverity
    field_name: Optional[str] = None
    field_index: Optional[int] = None
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    explanation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a dictionary representation."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "field_name": self.field_name,
            "field_index": self.field_index,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "explanation": self.explanation,
        }

    def __str__(self) -> str:
        """Return a human-readable string representation of the issue."""
        parts = [f"[{self.severity.value.upper()}] {self.code}: {self.message}"]
        if self.field_name:
            parts.append(f"  Field: {self.field_name} (index {self.field_index})")
        if self.expected_value is not None:
            parts.append(f"  Expected: {self.expected_value}")
        if self.actual_value is not None:
            parts.append(f"  Actual: {self.actual_value}")
        if self.explanation:
            parts.append(f"  Explanation: {self.explanation}")
        return "\n".join(parts)


@dataclass
class ValidationReport:
    """
    A comprehensive report of validation results for a single event or event sequence.

    This report provides:
    - Overall validity status
    - List of all detected issues
    - Summary statistics
    - Validity score (0.0 to 1.0)

    Attributes:
        valid: Whether the event/sequence is considered valid overall
        issues: List of all validation issues detected
        validity_score: A score from 0.0 (completely invalid) to 1.0 (fully valid)
        event_index: For sequence validation, the index of the event (if single event)
        event_type: The detected event type (if identifiable)
        event_type_name: Human-readable name of the event type
        metadata: Additional metadata about the validation
    """
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    validity_score: float = 1.0
    event_index: Optional[int] = None
    event_type: Optional[int] = None
    event_type_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def error_count(self) -> int:
        """Count of ERROR-level issues."""
        return sum(1 for issue in self.issues if issue.severity == IssueSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of WARNING-level issues."""
        return sum(1 for issue in self.issues if issue.severity == IssueSeverity.WARNING)

    @property
    def info_count(self) -> int:
        """Count of INFO-level issues."""
        return sum(1 for issue in self.issues if issue.severity == IssueSeverity.INFO)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue to the report."""
        self.issues.append(issue)
        # Recalculate validity based on errors
        if issue.severity == IssueSeverity.ERROR:
            self.valid = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert the report to a dictionary representation."""
        return {
            "valid": self.valid,
            "validity_score": self.validity_score,
            "event_index": self.event_index,
            "event_type": self.event_type,
            "event_type_name": self.event_type_name,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """Return a human-readable string representation of the report."""
        lines = [
            "=" * 60,
            "VALIDATION REPORT",
            "=" * 60,
            f"Valid: {'YES' if self.valid else 'NO'}",
            f"Validity Score: {self.validity_score:.2%}",
        ]

        if self.event_type_name:
            lines.append(f"Event Type: {self.event_type_name} (ID: {self.event_type})")
        elif self.event_type is not None:
            lines.append(f"Event Type ID: {self.event_type}")

        if self.event_index is not None:
            lines.append(f"Event Index: {self.event_index}")

        lines.extend([
            "-" * 60,
            f"Issues: {len(self.issues)} total "
            f"({self.error_count} errors, {self.warning_count} warnings, {self.info_count} info)",
            "-" * 60,
        ])

        if self.issues:
            for issue in self.issues:
                lines.append(str(issue))
                lines.append("")
        else:
            lines.append("No issues detected.")

        lines.append("=" * 60)
        return "\n".join(lines)


@dataclass
class SequenceValidationReport:
    """
    A comprehensive report of validation results for a sequence of events.

    This extends single-event validation to cover sequence-level concerns like
    chronological ordering, possession continuity, and location plausibility.

    Attributes:
        valid: Whether the entire sequence is considered valid
        event_reports: List of validation reports for each individual event
        sequence_issues: Issues that relate to the sequence as a whole
        validity_score: Overall validity score for the sequence
        total_events: Total number of events in the sequence
        valid_events: Number of individually valid events
        metadata: Additional metadata about the validation
    """
    valid: bool
    event_reports: List[ValidationReport] = field(default_factory=list)
    sequence_issues: List[ValidationIssue] = field(default_factory=list)
    validity_score: float = 1.0
    total_events: int = 0
    valid_events: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def sequence_error_count(self) -> int:
        """Count of ERROR-level sequence issues."""
        return sum(1 for issue in self.sequence_issues if issue.severity == IssueSeverity.ERROR)

    @property
    def sequence_warning_count(self) -> int:
        """Count of WARNING-level sequence issues."""
        return sum(1 for issue in self.sequence_issues if issue.severity == IssueSeverity.WARNING)

    @property
    def total_error_count(self) -> int:
        """Total count of all ERROR-level issues (event + sequence)."""
        event_errors = sum(report.error_count for report in self.event_reports)
        return event_errors + self.sequence_error_count

    @property
    def total_warning_count(self) -> int:
        """Total count of all WARNING-level issues (event + sequence)."""
        event_warnings = sum(report.warning_count for report in self.event_reports)
        return event_warnings + self.sequence_warning_count

    def add_event_report(self, report: ValidationReport) -> None:
        """Add an individual event validation report."""
        self.event_reports.append(report)
        self.total_events = len(self.event_reports)
        self.valid_events = sum(1 for r in self.event_reports if r.valid)

    def add_sequence_issue(self, issue: ValidationIssue) -> None:
        """Add a sequence-level validation issue."""
        self.sequence_issues.append(issue)
        if issue.severity == IssueSeverity.ERROR:
            self.valid = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert the report to a dictionary representation."""
        return {
            "valid": self.valid,
            "validity_score": self.validity_score,
            "total_events": self.total_events,
            "valid_events": self.valid_events,
            "total_error_count": self.total_error_count,
            "total_warning_count": self.total_warning_count,
            "sequence_issues": [issue.to_dict() for issue in self.sequence_issues],
            "event_reports": [report.to_dict() for report in self.event_reports],
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """Return a human-readable string representation of the sequence report."""
        lines = [
            "=" * 70,
            "SEQUENCE VALIDATION REPORT",
            "=" * 70,
            f"Valid: {'YES' if self.valid else 'NO'}",
            f"Validity Score: {self.validity_score:.2%}",
            f"Events: {self.valid_events}/{self.total_events} valid",
            "-" * 70,
            f"Sequence Issues: {len(self.sequence_issues)} "
            f"({self.sequence_error_count} errors, {self.sequence_warning_count} warnings)",
            "-" * 70,
        ]

        if self.sequence_issues:
            lines.append("SEQUENCE-LEVEL ISSUES:")
            for issue in self.sequence_issues:
                lines.append(str(issue))
                lines.append("")

        # Summary of event issues
        events_with_issues = [(i, r) for i, r in enumerate(self.event_reports) if r.issues]
        if events_with_issues:
            lines.append("-" * 70)
            lines.append(f"EVENTS WITH ISSUES ({len(events_with_issues)}):")
            for idx, report in events_with_issues:
                lines.append(f"\n  Event {idx} ({report.event_type_name or 'Unknown'}):")
                for issue in report.issues:
                    lines.append(f"    [{issue.severity.value.upper()}] {issue.code}: {issue.message}")

        lines.append("=" * 70)
        return "\n".join(lines)

