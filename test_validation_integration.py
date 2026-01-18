#!/usr/bin/env python3
"""
Integration test for EventValidator with real tokenized data.

This script validates that the validator works correctly with actual
tokenized events from the StatsBomb dataset loaded from CSV files.

Workflow:
1. Searches for CSV files in ../football_events_generation/csv/
2. Each CSV file contains tokenized events for one match (rows = events, cols = 128 features)
3. Loads the CSV into a numpy array
4. Validates the events using EventValidator
5. Reports validation results and statistics

CSV Format:
- First column: index (event number)
- Columns 1-128: tokenized features (normalized values 0-1)
- Each row represents one event in the match
"""

import sys
import logging
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tokenizer import EventValidator, StrictnessLevel


def test_with_real_data():
    """Test validator with real tokenized data from CSV files."""
    print("=" * 70)
    print("Testing EventValidator with Real Tokenized Data from CSV")
    print("=" * 70)

    # Try to find CSV files with tokenized events
    csv_search_paths = [
        "../football_events_generation/csv",
        "../../football_events_generation/csv",
    ]

    csv_dir = None
    for path in csv_search_paths:
        if Path(path).exists() and Path(path).is_dir():
            csv_dir = Path(path)
            print(f"\nFound CSV directory: {path}")
            break

    if csv_dir is None:
        print("\nNo CSV directory found. Skipping integration test.")
        print("Expected location: ../football_events_generation/csv/")
        print("CSV files should contain tokenized match events (128 features per event)")
        return True  # Don't fail the test

    # Find available CSV files
    csv_files = sorted(csv_dir.glob("*.csv"))
    if not csv_files:
        print(f"\nNo CSV files found in {csv_dir}")
        return True

    print(f"Found {len(csv_files)} CSV files: {[f.stem for f in csv_files]}")

    # Use the first CSV file for testing
    csv_file = csv_files[0]
    print(f"\nLoading tokenized events from: {csv_file.name}")
    print("This may take a moment...")

    try:
        # Load the CSV file into a numpy array
        # The first column is the index, columns 1-128 are the token features
        df = pd.read_csv(csv_file, index_col=0)
        events = df.values  # Convert to numpy array

        print(f"✓ Successfully loaded {len(events)} events with {events.shape[1]} features")

        # Create validator
        validator = EventValidator(
            strictness=StrictnessLevel.MODERATE,
            max_time_gap=30.0,
            max_location_jump=70.0,
            logging_level=logging.WARNING
        )

        print("\n" + "-" * 70)
        print("Validating Individual Events")
        print("-" * 70)

        # Validate first 10 events individually
        for i in range(min(10, len(events))):
            report = validator.validate_event(events[i])
            status = "✓" if report.valid else "✗"
            print(f"Event {i}: {status} {report.event_type_name or 'Unknown'} "
                  f"(score: {report.validity_score:.2%})")

            if not report.valid and report.issues:
                for issue in report.issues[:3]:  # Show first 3 issues
                    print(f"    - [{issue.severity.value.upper()}] {issue.message}")

        print("\n" + "-" * 70)
        print("Validating Entire Sequence")
        print("-" * 70)

        # Validate the entire sequence
        seq_report = validator.validate_sequence(events)

        print(f"\nTotal Events: {seq_report.total_events}")
        print(f"Valid Events: {seq_report.valid_events}/{seq_report.total_events} "
              f"({seq_report.valid_events/seq_report.total_events*100:.1f}%)")
        print(f"Overall Valid: {seq_report.valid}")
        print(f"Validity Score: {seq_report.validity_score:.2%}")
        print(f"Total Errors: {seq_report.total_error_count}")
        print(f"Total Warnings: {seq_report.total_warning_count}")

        if seq_report.sequence_issues:
            print(f"\nSequence-level issues ({len(seq_report.sequence_issues)}):")
            for issue in seq_report.sequence_issues[:5]:  # Show first 5
                print(f"  [{issue.severity.value.upper()}] {issue.code}: {issue.message}")

        # Summary of event types
        event_types = {}
        for report in seq_report.event_reports:
            event_type = report.event_type_name or "Unknown"
            if event_type not in event_types:
                event_types[event_type] = {"valid": 0, "invalid": 0}
            if report.valid:
                event_types[event_type]["valid"] += 1
            else:
                event_types[event_type]["invalid"] += 1

        print("\n" + "-" * 70)
        print("Validation Summary by Event Type")
        print("-" * 70)
        for event_type, counts in sorted(event_types.items()):
            total = counts["valid"] + counts["invalid"]
            pct = counts["valid"] / total * 100 if total > 0 else 0
            print(f"  {event_type:20s}: {counts['valid']:3d}/{total:3d} valid ({pct:5.1f}%)")

        print("\n" + "=" * 70)
        print("✓ Integration test completed successfully!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_with_real_data()
    sys.exit(0 if success else 1)

