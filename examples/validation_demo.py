#!/usr/bin/env python3
"""
Example script demonstrating the EventValidator functionality.

This script shows how to:
1. Validate a single event
2. Validate a sequence of events
3. Handle different strictness levels
4. Interpret validation reports
"""

import numpy as np
import logging
from tokenizer import EventValidator, StrictnessLevel


def create_sample_valid_event() -> np.ndarray:
    """
    Create a sample valid event vector for demonstration.

    This creates a simplified pass event with reasonable values.
    """
    event = np.zeros(128)

    # Common features (indices 0-14)
    # Pass event ID is 30, which should map to a normalized value
    # The categorical parser normalizes as: category_index / num_categories
    # We'll use a mid-range value that represents a valid event type
    event[0] = 0.88  # type.id (pass event, ID 30, normalized approximately)
    event[1] = 0.4   # play_pattern.id
    event[2] = 0.5   # x location (middle of field)
    event[3] = 0.5   # y location (middle of width)
    event[4] = 0.3   # duration (normalized, ~0.9 seconds)
    event[5] = 0.0   # under_pressure (False)
    event[6] = 0.0   # out (False)
    event[7] = 0.0   # counterpress (False)
    event[8] = 0.4   # period (period 2)
    event[9] = 0.5   # second (30 seconds)
    event[10] = 0.4  # position.id
    event[11] = 0.5  # minute (30 minutes)
    event[12] = 0.5  # team.id
    event[13] = 0.5  # possession_team.id
    event[14] = 0.4  # player position

    # Pass-specific features (starting at index 47)
    event[47] = 0.2  # pass.type.id
    event[48] = 0.3  # pass.length (normalized, ~36m)
    event[49] = 0.5  # pass.angle (normalized)
    event[50] = 0.3  # pass.height.id
    event[51] = 0.6  # pass.end_location[0]
    event[52] = 0.4  # pass.end_location[1]
    event[63] = 0.0  # pass.outcome.id (successful)
    event[64] = 0.3  # pass.recipient position

    return event


def create_sample_invalid_event() -> np.ndarray:
    """
    Create a sample invalid event with several issues.
    """
    event = np.zeros(128)

    # Invalid event type (out of range)
    event[0] = 1.5  # ERROR: Out of [0, 1] range

    # Invalid location
    event[2] = -0.5  # ERROR: Negative location
    event[3] = 1.5   # ERROR: Out of bounds

    # Other features left as zeros or invalid values
    event[4] = 2.0   # duration (too large, but normalized)

    return event


def create_sample_event_sequence() -> np.ndarray:
    """
    Create a sample sequence of events for demonstration.
    """
    n_events = 5
    events = np.zeros((n_events, 128))

    # Random number generator
    rng = np.random.default_rng()

    # Create a sequence of events with chronological progression
    for i in range(n_events):
        # Base on the valid event template
        events[i] = create_sample_valid_event()

        # Progress time
        events[i][11] = 0.4 + i * 0.05  # minute progresses
        events[i][9] = (i * 10) / 60.0  # second progresses

        # Move location slightly
        events[i][2] = 0.4 + i * 0.05  # x progresses down field
        events[i][3] = 0.5 + rng.standard_normal() * 0.05  # y varies slightly

    return events


def example_1_validate_single_event():
    """Example 1: Validate a single event."""
    print("=" * 70)
    print("EXAMPLE 1: Validating a Single Event")
    print("=" * 70)

    # Create validator with INFO logging to see what's happening
    validator = EventValidator(
        strictness=StrictnessLevel.MODERATE,
        logging_level=logging.WARNING  # Change to INFO for detailed logs
    )

    print("\n--- Validating a VALID event ---")
    valid_event = create_sample_valid_event()
    report = validator.validate_event(valid_event)

    print(f"Valid: {report.valid}")
    print(f"Validity Score: {report.validity_score:.2%}")
    print(f"Event Type: {report.event_type_name} (ID: {report.event_type})")
    print(f"Issues: {len(report.issues)} total ({report.error_count} errors, "
          f"{report.warning_count} warnings, {report.info_count} info)")

    if report.issues:
        print("\nIssues found:")
        for issue in report.issues:
            print(f"  [{issue.severity.value.upper()}] {issue.code}: {issue.message}")

    print("\n--- Validating an INVALID event ---")
    invalid_event = create_sample_invalid_event()
    report = validator.validate_event(invalid_event)

    print(f"Valid: {report.valid}")
    print(f"Validity Score: {report.validity_score:.2%}")
    print(f"Issues: {len(report.issues)} total ({report.error_count} errors, "
          f"{report.warning_count} warnings)")

    if report.issues:
        print("\nIssues found:")
        for issue in report.issues[:5]:  # Show first 5 issues
            print(f"\n  [{issue.severity.value.upper()}] {issue.code}")
            print(f"    Message: {issue.message}")
            if issue.explanation:
                print(f"    Explanation: {issue.explanation}")

    print("\n")


def example_2_validate_sequence():
    """Example 2: Validate a sequence of events."""
    print("=" * 70)
    print("EXAMPLE 2: Validating an Event Sequence")
    print("=" * 70)

    validator = EventValidator(
        strictness=StrictnessLevel.MODERATE,
        max_time_gap=30.0,
        max_location_jump=50.0,
        logging_level=logging.WARNING
    )

    events = create_sample_event_sequence()
    seq_report = validator.validate_sequence(events)

    print(f"\nTotal Events: {seq_report.total_events}")
    print(f"Valid Events: {seq_report.valid_events}/{seq_report.total_events}")
    print(f"Overall Valid: {seq_report.valid}")
    print(f"Validity Score: {seq_report.validity_score:.2%}")
    print(f"Total Errors: {seq_report.total_error_count}")
    print(f"Total Warnings: {seq_report.total_warning_count}")

    if seq_report.sequence_issues:
        print(f"\nSequence-level issues ({len(seq_report.sequence_issues)}):")
        for issue in seq_report.sequence_issues:
            print(f"  [{issue.severity.value.upper()}] {issue.code}: {issue.message}")

    # Show individual event reports
    print("\nIndividual Event Reports:")
    for i, event_report in enumerate(seq_report.event_reports):
        status = "✓" if event_report.valid else "✗"
        print(f"  Event {i}: {status} {event_report.event_type_name} "
              f"(score: {event_report.validity_score:.2%}, "
              f"issues: {len(event_report.issues)})")

    print("\n")


def example_3_strictness_levels():
    """Example 3: Compare different strictness levels."""
    print("=" * 70)
    print("EXAMPLE 3: Comparing Strictness Levels")
    print("=" * 70)

    # Create an event with a minor issue
    event = create_sample_valid_event()
    # Make shot start from own half (unusual but not impossible)
    # Shot event ID is 16, approximately 0.47 normalized
    event[0] = 0.47  # shot event
    event[2] = 0.2  # x location in own half

    # Add shot-specific features at index 71
    event[71] = 0.5  # shot.type.id
    event[72] = 0.9  # shot.end_location[0] (towards goal)
    event[73] = 0.5  # shot.end_location[1]
    event[74] = 0.2  # shot.end_location[2] (height)
    event[82] = 0.15 # shot.statsbomb_xg (low xG from own half)
    event[84] = 0.5  # shot.outcome.id

    for strictness in [StrictnessLevel.LENIENT, StrictnessLevel.MODERATE, StrictnessLevel.STRICT]:
        validator = EventValidator(
            strictness=strictness,
            logging_level=logging.WARNING
        )

        report = validator.validate_event(event)

        print(f"\n{strictness.value.upper()} mode:")
        print(f"  Valid: {report.valid}")
        print(f"  Score: {report.validity_score:.2%}")
        print(f"  Errors: {report.error_count}, Warnings: {report.warning_count}")


def example_4_export_report():
    """Example 4: Export validation report to dictionary."""
    print("=" * 70)
    print("EXAMPLE 4: Exporting Validation Report")
    print("=" * 70)

    validator = EventValidator()
    event = create_sample_valid_event()
    report = validator.validate_event(event)

    # Convert to dictionary for JSON export
    report_dict = report.to_dict()

    print("\nReport as dictionary (for JSON export):")
    import json
    print(json.dumps(report_dict, indent=2))

    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("█" * 70)
    print("  StatsBomb Football Event Validator - Examples")
    print("█" * 70)
    print("\n")

    example_1_validate_single_event()
    example_2_validate_sequence()
    example_3_strictness_levels()
    example_4_export_report()

    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\nFor more information, see VALIDATION_QUICKSTART.md")
    print("\n")


if __name__ == "__main__":
    main()

