"""
Event Validator Module

This module provides the EventValidator class for validating tokenized football event vectors
and sequences. It performs comprehensive validation including:

1. Single Event Validation:
   - Common features (time, location, team, possession)
   - Event-specific features matching event type
   - Value ranges and categorical constraints
   - Football domain constraints

2. Sequence Validation:
   - Chronological ordering of timestamps
   - Possession continuity and valid transitions
   - Location plausibility between consecutive events
   - Time gap constraints

The validator supports configurable strictness levels and detailed logging.
"""

import logging
import numpy as np
import pandas as pd
from typing import Union, List, Optional, Tuple
from enum import Enum

from tokenizer.validation.report import (
    ValidationReport,
    ValidationIssue,
    IssueSeverity,
    SequenceValidationReport,
)
from tokenizer.config import event_types_mapping, event_ids


class StrictnessLevel(Enum):
    """
    Validation strictness levels.

    STRICT: All features must be in valid ranges, all constraints enforced
    MODERATE: Small deviations allowed, main constraints enforced
    LENIENT: Only major violations flagged, flexible constraints
    """
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class EventValidator:
    """
    Comprehensive validator for tokenized football event vectors and sequences.

    This class provides methods to validate:
    1. Single events - validate individual 128-dimensional event vectors
    2. Event sequences - validate series of events for temporal and logical consistency

    The validator can be configured with different strictness levels, time gap thresholds,
    and logging verbosity to suit different use cases.

    Attributes:
        strictness: Validation strictness level (STRICT, MODERATE, or LENIENT)
        max_time_gap: Maximum allowed time gap between consecutive events (seconds)
        max_location_jump: Maximum plausible location jump between events (meters)
        logger: Logger instance for detailed validation messages

    Example:
        >>> validator = EventValidator(
        ...     strictness=StrictnessLevel.MODERATE,
        ...     max_time_gap=30.0,
        ...     logging_level=logging.INFO
        ... )
        >>> report = validator.validate_event(event_vector)
        >>> print(report)
    """

    # Field indices in the 128-dimensional vector (based on config.py)
    EVENT_TYPE_IDX = 0  # type.id
    PLAY_PATTERN_IDX = 1  # play_pattern.id
    X_LOCATION_IDX = 2  # location[0]
    Y_LOCATION_IDX = 3  # location[1]
    DURATION_IDX = 4  # duration
    UNDER_PRESSURE_IDX = 5  # under_pressure
    OUT_IDX = 6  # out
    COUNTERPRESS_IDX = 7  # counterpress
    PERIOD_IDX = 8  # period
    SECOND_IDX = 9  # second
    POSITION_IDX = 10  # position.id
    # Special parsers occupy indices 11-14
    MINUTE_IDX = 11  # minute (special parser)
    TEAM_IDX = 12  # team.id (special parser)
    POSSESSION_TEAM_IDX = 13  # possession_team.id (special parser)
    PLAYER_POSITION_IDX = 14  # player.id (special parser)

    # Event-specific regions start at index 15

    # Shot event indices (starting_index = 71, 13 features + freeze frame)
    SHOT_START_IDX = 71
    SHOT_TYPE_IDX = 71          # shot.type.id
    SHOT_END_X_IDX = 72         # shot.end_location[0]
    SHOT_END_Y_IDX = 73         # shot.end_location[1]
    SHOT_END_Z_IDX = 74         # shot.end_location[2]
    SHOT_AERIAL_WON_IDX = 75    # shot.aerial_won
    SHOT_FOLLOWS_DRIBBLE_IDX = 76  # shot.follows_dribble
    SHOT_FIRST_TIME_IDX = 77    # shot.first_time
    SHOT_OPEN_GOAL_IDX = 78     # shot.open_goal
    SHOT_XG_IDX = 79            # shot.statsbomb_xg
    SHOT_DEFLECTED_IDX = 80     # shot.deflected
    SHOT_TECHNIQUE_IDX = 81     # shot.technique.id
    SHOT_BODY_PART_IDX = 82     # shot.body_part.id
    SHOT_OUTCOME_IDX = 83       # shot.outcome.id
    SHOT_FREEZE_FRAME_START = 84  # 22 players * 2 features = 44 indices (84-127)

    # Pass event indices (starting_index = 47)
    PASS_START_IDX = 47
    PASS_TYPE_IDX = 47          # pass.type.id
    PASS_LENGTH_IDX = 48        # pass.length
    PASS_ANGLE_IDX = 49         # pass.angle
    PASS_HEIGHT_IDX = 50        # pass.height.id
    PASS_END_X_IDX = 51         # pass.end_location[0]
    PASS_END_Y_IDX = 52         # pass.end_location[1]
    PASS_OUTCOME_IDX = 62       # pass.outcome.id
    PASS_TECHNIQUE_IDX = 63     # pass.technique.id
    PASS_RECIPIENT_IDX = 64     # pass.recipient.id (special parser)

    # Possession-changing event types (events that can change possession)
    POSSESSION_CHANGE_EVENTS = {
        event_ids['interception'],
        event_ids['duel'],
        event_ids['50_50'],
        event_ids['pass'],  # if unsuccessful
        event_ids['shot'],  # if saved/missed
        event_ids['clearance'],
        event_ids['miscontrol'],
        event_ids['dispossessed'],
        event_ids['dribbled_past'],
        event_ids['error'],
        event_ids['foul_won'],
        event_ids['foul_committed'],
        event_ids['goalkeeper'],
    }

    def __init__(
        self,
        strictness: StrictnessLevel = StrictnessLevel.MODERATE,
        max_time_gap: float = 30.0,
        max_location_jump: float = 70.0,
        logging_level: int = logging.WARNING,
    ):
        """
        Initialize the EventValidator.

        Args:
            strictness: Validation strictness level (STRICT, MODERATE, LENIENT)
            max_time_gap: Maximum allowed time gap between events in seconds
            max_location_jump: Maximum plausible distance between consecutive event locations in meters
            logging_level: Python logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.strictness = strictness
        self.max_time_gap = max_time_gap
        self.max_location_jump = max_location_jump

        # Set up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging_level)

        # Add handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Reverse mapping from event ID to name
        self.event_id_to_name = {v: k for k, v in event_ids.items()}

        self.logger.info(
            f"EventValidator initialized with strictness={strictness.value}, "
            f"max_time_gap={max_time_gap}s, max_location_jump={max_location_jump}m"
        )

    def align_generated_embedding(self, event: np.ndarray) -> np.ndarray:
        """
        Align generated embeddings to valid tokenized values.

        This function preprocesses embeddings that come from a generative model
        (e.g., diffusion model) and have been decoded through an autoencoder.
        Such embeddings may have values that are close to, but not exactly equal to,
        the expected categorical or boolean values.

        Processing:
        1. Clip all values to [0, 1] range
        2. Round boolean features to nearest valid value (0 or 0.5)
        3. Snap categorical features to nearest valid categorical value
        4. Keep continuous (range) features as-is (already clipped)

        Args:
            event: 128-dimensional event vector (numpy array)

        Returns:
            Aligned event vector with values adjusted to match expected discretization
        """
        from tokenizer.feature_parsers import CategoricalFeatureParser

        aligned = event.copy()

        # First, clip all values to [0, 1]
        aligned = np.clip(aligned, 0, 1)

        self.logger.debug("Aligning generated embedding to valid tokenized values")

        # Mapping from config dict_path to vector index
        # Only includes categorical features that need alignment
        # Range features (location, duration, minute) are kept as-is after clipping
        COMMON_FEATURE_INDEX_MAP = {
            "type.id": self.EVENT_TYPE_IDX,
            "play_pattern.id": self.PLAY_PATTERN_IDX,
            "under_pressure": self.UNDER_PRESSURE_IDX,
            "out": self.OUT_IDX,
            "counterpress": self.COUNTERPRESS_IDX,
            "period": self.PERIOD_IDX,
            "second": self.SECOND_IDX,
            "position.id": self.POSITION_IDX,
        }

        # Get common features configuration
        common_config = event_types_mapping["common"]

        # Align categorical common features
        for dict_path, feature_parser in common_config["feature_parsers"].items():
            # Skip range features (they're already clipped)
            if dict_path not in COMMON_FEATURE_INDEX_MAP:
                continue

            # Only align categorical features
            if not isinstance(feature_parser, CategoricalFeatureParser):
                continue

            idx = COMMON_FEATURE_INDEX_MAP[dict_path]
            aligned[idx] = self._snap_to_nearest_categorical(
                aligned[idx],
                feature_parser.categories,
                feature_parser.num_categories
            )

        # Special parsers (minute, team IDs, player position) are handled:
        # - minute: range feature, already clipped
        # - team.id, possession_team.id: already clipped to [0,1]
        # - player.id: already clipped to [0,1]

        # Determine event type to align event-specific features
        event_type_id = self._denormalize_categorical(
            aligned[self.EVENT_TYPE_IDX],
            common_config["feature_parsers"]["type.id"].categories,
            common_config["feature_parsers"]["type.id"].num_categories
        )

        # Align event-specific categorical features
        if event_type_id and event_type_id in event_types_mapping:
            event_config = event_types_mapping[event_type_id]

            if not event_config.get("ignore_event_type", False):
                starting_index = event_config.get("starting_index", -1)

                if starting_index >= 0:
                    # Iterate through event-specific features and align categorical ones
                    feature_offset = 0
                    for dict_path, feature_parser in event_config.get("feature_parsers", {}).items():
                        if isinstance(feature_parser, CategoricalFeatureParser):
                            idx = starting_index + feature_offset
                            aligned[idx] = self._snap_to_nearest_categorical(
                                aligned[idx],
                                feature_parser.categories,
                                feature_parser.num_categories
                            )
                        feature_offset += 1

        self.logger.debug("Embedding alignment complete")
        return aligned

    def _snap_to_nearest_categorical(
        self,
        value: float,
        categories_map: dict,
        num_categories: int
    ) -> float:
        """
        Snap a value to the nearest valid categorical normalized value.

        Args:
            value: The value to snap (0-1)
            categories_map: Mapping from category to index
            num_categories: Total number of categories

        Returns:
            Nearest valid normalized categorical value
        """
        if value == 0:
            return 0  # Missing value

        # Calculate what category index this would be closest to
        category_index = round(value * num_categories)

        # Clamp to valid range
        category_index = max(1, min(num_categories, category_index))

        # Return normalized value
        return category_index / num_categories

    def validate_event(self, event: Union[List[float], np.ndarray], align_embedding: bool = False) -> ValidationReport:
        """
        Validate a single tokenized event vector.

        This method performs comprehensive validation including:
        - Vector structure (dimension check)
        - Common features (time, location, team, possession, etc.)
        - Event-specific features based on event type
        - Football domain constraints

        Args:
            event: A 128-dimensional event vector (list or numpy array)
            align_embedding: If True, align generated embeddings before validation.
                           This is useful for embeddings from generative models that
                           may have values close to but not exactly matching expected
                           categorical/boolean values. Default is False.

        Returns:
            ValidationReport: Detailed validation report with issues and validity score

        Example:
            >>> event_vector = [0.5, 0.3, 0.4, ...]  # 128 values
            >>> report = validator.validate_event(event_vector)
            >>> if report.valid:
            ...     print("Event is valid!")
            >>> else:
            ...     for issue in report.issues:
            ...         print(issue)

            >>> # For generated embeddings
            >>> generated = model.generate()
            >>> report = validator.validate_event(generated, align_embedding=True)
        """
        # Convert to numpy array
        event_array = self._to_numpy_array(event)

        # Align embedding if requested (for generated embeddings from autoencoders)
        if align_embedding:
            self.logger.info("Aligning generated embedding before validation")
            event_array = self.align_generated_embedding(event_array)

        # Initialize report
        report = ValidationReport(valid=True)

        # Step 1: Validate vector structure
        self.logger.info("Step 1: Validating vector structure")
        self._validate_vector_structure(event_array, report)
        if not report.valid:
            return report

        # Step 2: Extract and validate event type
        self.logger.info("Step 2: Extracting and validating event type")
        event_type_id = self._extract_event_type(event_array, report)
        if event_type_id is not None:
            report.event_type = event_type_id
            report.event_type_name = self.event_id_to_name.get(event_type_id, "Unknown")
            self.logger.info(f"Event type identified: {report.event_type_name} (ID: {event_type_id})")

        # Step 3: Validate common features
        self.logger.info("Step 3: Validating common features")
        self._validate_common_features(event_array, report)

        # Step 4: Validate event-specific features
        if event_type_id is not None:
            self.logger.info(f"Step 4: Validating {report.event_type_name}-specific features")
            self._validate_event_specific_features(event_array, event_type_id, report)

        # Step 5: Calculate validity score
        report.validity_score = self._calculate_validity_score(report)

        self.logger.info(
            f"Validation complete: valid={report.valid}, score={report.validity_score:.2%}, "
            f"errors={report.error_count}, warnings={report.warning_count}"
        )

        return report

    def validate_sequence(
        self,
        events: Union[List[List[float]], np.ndarray, pd.DataFrame],
        align_embedding: bool = False
    ) -> SequenceValidationReport:
        """
        Validate a sequence of tokenized events.

        This method validates both individual events and sequence-level constraints:
        - Each event is validated individually
        - Timestamps are checked for chronological ordering
        - Possession changes are validated for correctness
        - Location transitions are checked for plausibility
        - Time gaps between events are validated

        Args:
            events: Sequence of events, can be:
                - List of lists: [[event1], [event2], ...]
                - NumPy array: shape (n_events, 128)
                - Pandas DataFrame: each row is an event
            align_embedding: If True, align generated embeddings before validation.
                           Useful for sequences from generative models. Default is False.

        Returns:
            SequenceValidationReport: Comprehensive sequence validation report

        Example:
            >>> events = np.array([event1, event2, event3])  # shape (3, 128)
            >>> report = validator.validate_sequence(events)
            >>> print(f"Valid events: {report.valid_events}/{report.total_events}")
            >>> if report.sequence_issues:
            ...     print("Sequence-level issues detected!")

            >>> # For generated sequences
            >>> generated = model.generate_sequence(n=100)
            >>> report = validator.validate_sequence(generated, align_embedding=True)
        """
        # Convert to numpy array
        events_array = self._to_numpy_2d_array(events)

        # Align embeddings if requested
        if align_embedding:
            self.logger.info(f"Aligning {len(events_array)} generated embeddings before validation")
            events_array = np.array([self.align_generated_embedding(event) for event in events_array])

        # Initialize sequence report
        seq_report = SequenceValidationReport(
            valid=True,
            total_events=len(events_array)
        )

        self.logger.info(f"Validating sequence of {len(events_array)} events")

        # Step 1: Validate each individual event
        # Note: We don't pass align_embedding here because we already aligned above
        self.logger.info("Step 1: Validating individual events")
        for i, event in enumerate(events_array):
            self.logger.info(f"Validating event {i+1}/{len(events_array)}")
            event_report = self.validate_event(event, align_embedding=False)
            event_report.event_index = i
            seq_report.add_event_report(event_report)

        # Step 2: Validate sequence-level constraints
        self.logger.info("Step 2: Validating sequence-level constraints")
        self._validate_chronological_order(events_array, seq_report)
        self._validate_possession_continuity(events_array, seq_report)
        self._validate_location_plausibility(events_array, seq_report)
        self._validate_time_gaps(events_array, seq_report)

        # Step 3: Calculate overall validity score
        seq_report.validity_score = self._calculate_sequence_validity_score(seq_report)

        self.logger.info(
            f"Sequence validation complete: valid={seq_report.valid}, "
            f"score={seq_report.validity_score:.2%}, "
            f"valid_events={seq_report.valid_events}/{seq_report.total_events}, "
            f"sequence_errors={seq_report.sequence_error_count}"
        )

        return seq_report

    # ==================== Private Helper Methods ====================

    def _to_numpy_array(self, event: Union[List[float], np.ndarray]) -> np.ndarray:
        """Convert event to numpy array."""
        if isinstance(event, np.ndarray):
            return event
        elif isinstance(event, list):
            return np.array(event)
        else:
            raise TypeError(f"Event must be list or numpy array, got {type(event)}")

    def _to_numpy_2d_array(
        self,
        events: Union[List[List[float]], np.ndarray, pd.DataFrame]
    ) -> np.ndarray:
        """Convert events sequence to 2D numpy array."""
        if isinstance(events, np.ndarray):
            return events
        elif isinstance(events, pd.DataFrame):
            return events.values
        elif isinstance(events, list):
            return np.array(events)
        else:
            raise TypeError(
                f"Events must be list, numpy array, or DataFrame, got {type(events)}"
            )

    def _validate_vector_structure(
        self,
        event: np.ndarray,
        report: ValidationReport
    ) -> None:
        """
        Validate that the event vector has the correct structure.

        Checks:
        - Vector has exactly 128 dimensions
        - All values are numeric (not NaN)
        - All values are in the normalized range [0, 1]
        """
        if len(event) != 128:
            issue = ValidationIssue(
                code="INVALID_VECTOR_SIZE",
                message=f"Event vector must have 128 dimensions, got {len(event)}",
                severity=IssueSeverity.ERROR,
                expected_value=128,
                actual_value=len(event),
                explanation=(
                    "The tokenizer outputs 128-dimensional vectors. This vector has "
                    f"{len(event)} dimensions, indicating it's not a valid tokenized event."
                )
            )
            report.add_issue(issue)
            self.logger.error(f"Vector dimension mismatch: expected 128, got {len(event)}")
            return

        # Check for NaN values
        if np.any(np.isnan(event)):
            nan_indices = np.where(np.isnan(event))[0]
            issue = ValidationIssue(
                code="NAN_VALUES",
                message=f"Event vector contains NaN values at indices: {nan_indices.tolist()}",
                severity=IssueSeverity.ERROR,
                explanation=(
                    "NaN (Not a Number) values indicate missing or corrupted data. "
                    "All 128 values must be valid numbers."
                )
            )
            report.add_issue(issue)
            self.logger.error(f"NaN values found at indices: {nan_indices.tolist()}")

        # Check for values outside [0, 1] range
        out_of_range = np.where((event < 0) | (event > 1))[0]
        if len(out_of_range) > 0:
            # Group consecutive indices for cleaner reporting
            if len(out_of_range) > 10:
                # Too many to list individually
                out_of_range_str = f"{len(out_of_range)} indices"
            else:
                out_of_range_str = f"indices {out_of_range.tolist()}"

            issue = ValidationIssue(
                code="VALUES_OUT_OF_RANGE",
                message=f"Event vector contains {len(out_of_range)} values outside [0, 1] at {out_of_range_str}",
                severity=IssueSeverity.ERROR,
                explanation=(
                    "All tokenized features are normalized to the range [0, 1]. "
                    "Values outside this range indicate the vector was not properly normalized "
                    "or may have been corrupted during generation/processing."
                )
            )
            report.add_issue(issue)
            self.logger.error(f"Values outside [0, 1] range at {len(out_of_range)} indices")

        self.logger.debug("Vector structure validation passed")

    def _extract_event_type(
        self,
        event: np.ndarray,
        report: ValidationReport
    ) -> Optional[int]:
        """
        Extract and validate the event type from the vector.

        The event type is stored at index 0 as a normalized categorical value.
        We need to denormalize it to get the actual event ID.
        """
        event_type_normalized = event[self.EVENT_TYPE_IDX]

        self.logger.debug(f"Event type (normalized): {event_type_normalized}")

        # Get categorical parser for event type
        common_config = event_types_mapping["common"]
        type_parser = common_config["feature_parsers"]["type.id"]

        # Reverse the normalization to get the actual event ID
        event_id = self._denormalize_categorical(
            event_type_normalized,
            type_parser.categories,
            type_parser.num_categories
        )

        if event_id is None or event_id == 0:
            issue = ValidationIssue(
                code="INVALID_EVENT_TYPE",
                message=f"Could not determine event type from normalized value {event_type_normalized}",
                severity=IssueSeverity.ERROR,
                field_name="type.id",
                field_index=self.EVENT_TYPE_IDX,
                actual_value=event_type_normalized,
                explanation=(
                    "The event type field (index 0) contains an invalid value. "
                    "This should be a normalized categorical value representing one of the "
                    f"{len(event_ids)} valid event types."
                )
            )
            report.add_issue(issue)
            self.logger.error(f"Invalid event type: normalized value = {event_type_normalized}")
            return None

        # Check if event type is in valid range
        if event_id not in event_types_mapping:
            issue = ValidationIssue(
                code="UNKNOWN_EVENT_TYPE",
                message=f"Event type ID {event_id} is not recognized",
                severity=IssueSeverity.ERROR,
                field_name="type.id",
                field_index=self.EVENT_TYPE_IDX,
                actual_value=event_id,
                expected_value=f"One of {list(event_ids.values())}",
                explanation=(
                    f"Event type ID {event_id} is not in the list of known event types. "
                    "This indicates corrupted data or an unsupported event type."
                )
            )
            report.add_issue(issue)
            self.logger.error(f"Unknown event type ID: {event_id}")
            return None

        self.logger.debug(f"Event type ID: {event_id} ({self.event_id_to_name.get(event_id, 'Unknown')})")
        return event_id

    def _denormalize_categorical(
        self,
        normalized_value: float,
        categories_map: dict,
        num_categories: int
    ) -> Optional[int]:
        """
        Reverse the categorical normalization to get the original category value.

        The normalization formula is: normalized = category_index / num_categories
        Where category_index = position in sorted categories + 1
        """
        if normalized_value == 0:
            return 0  # Missing value

        # Reverse: category_index = normalized * num_categories
        category_index = round(normalized_value * num_categories)

        # Find the category with this index
        for category, idx in categories_map.items():
            if idx == category_index:
                return category

        return None

    def _validate_common_features(
        self,
        event: np.ndarray,
        report: ValidationReport
    ) -> None:
        """
        Validate common features present in all events.

        Common features (indices 0-14):
        - type.id (0): Event type
        - play_pattern.id (1): Play pattern (1-9)
        - location (2-3): X,Y coordinates (0-120, 0-80)
        - duration (4): Event duration (0-3 seconds)
        - under_pressure (5): Boolean (0 or 1)
        - out (6): Boolean (0 or 1)
        - counterpress (7): Boolean (0 or 1)
        - period (8): Period (1-5)
        - second (9): Second (0-59)
        - position.id (10): Player position (1-25)
        - minute (11): Minute (0-60)
        - team.id (12): Team identifier
        - possession_team.id (13): Possession team identifier
        - player.id (14): Player position
        """
        self.logger.debug("Validating common features")

        # Validate play pattern (index 1)
        self._validate_categorical_feature(
            event[self.PLAY_PATTERN_IDX],
            "play_pattern.id",
            self.PLAY_PATTERN_IDX,
            list(range(1, 10)),
            "Play Pattern",
            report
        )

        # Validate location (indices 2-3)
        self._validate_location(
            event[self.X_LOCATION_IDX],
            event[self.Y_LOCATION_IDX],
            "location",
            self.X_LOCATION_IDX,
            report
        )

        # Validate duration (index 4)
        self._validate_range_feature(
            event[self.DURATION_IDX],
            "duration",
            self.DURATION_IDX,
            0.0,
            3.0,
            "seconds",
            report
        )

        # Validate boolean features
        for idx, name in [
            (self.UNDER_PRESSURE_IDX, "under_pressure"),
            (self.OUT_IDX, "out"),
            (self.COUNTERPRESS_IDX, "counterpress")
        ]:
            self._validate_boolean_feature(event[idx], name, idx, report)

        # Validate period (index 8)
        self._validate_categorical_feature(
            event[self.PERIOD_IDX],
            "period",
            self.PERIOD_IDX,
            list(range(1, 6)),
            "Period",
            report,
            explanation="Football matches have 2 regular periods, with up to 3 additional periods for extra time"
        )

        # Validate second (index 9)
        self._validate_categorical_feature(
            event[self.SECOND_IDX],
            "second",
            self.SECOND_IDX,
            list(range(0, 60)),
            "Second",
            report,
            explanation="Seconds within a minute, must be 0-59"
        )

        # Validate position (index 10)
        self._validate_categorical_feature(
            event[self.POSITION_IDX],
            "position.id",
            self.POSITION_IDX,
            list(range(1, 26)),
            "Player Position",
            report,
            explanation="StatsBomb defines 25 player positions"
        )

        # Validate minute (index 11) - special parser, normalized as range
        self._validate_range_feature(
            event[self.MINUTE_IDX],
            "minute",
            self.MINUTE_IDX,
            0.0,
            60.0,
            "minutes",
            report,
            explanation="Minute within the period (0-60, where 60+ indicates stoppage time)"
        )

        # Validate team and possession team (indices 12-13)
        # These are normalized identifiers, should be between 0 and 1
        for idx, name in [(self.TEAM_IDX, "team.id"), (self.POSSESSION_TEAM_IDX, "possession_team.id")]:
            if not (0 <= event[idx] <= 1):
                issue = ValidationIssue(
                    code="INVALID_TEAM_ID",
                    message=f"{name} value {event[idx]} is outside normalized range [0, 1]",
                    severity=IssueSeverity.ERROR,
                    field_name=name,
                    field_index=idx,
                    expected_value="0.0 to 1.0",
                    actual_value=event[idx],
                    explanation=f"{name} is normalized to range [0, 1] to represent team identifiers"
                )
                report.add_issue(issue)
                self.logger.error(f"{name} out of range: {event[idx]}")

        self.logger.debug("Common features validation complete")

    def _validate_event_specific_features(
        self,
        event: np.ndarray,
        event_type_id: int,
        report: ValidationReport
    ) -> None:
        """
        Validate features specific to the event type.

        Different event types have different feature sets starting at different indices.
        This method routes to type-specific validators.
        """
        event_config = event_types_mapping.get(event_type_id, {})

        if event_config.get("ignore_event_type", False):
            self.logger.debug(f"Event type {event_type_id} is ignored, skipping specific validation")
            return

        # Route to specific validators based on event type
        if event_type_id == event_ids['shot']:
            self._validate_shot_event(event, report)
        elif event_type_id == event_ids['pass']:
            self._validate_pass_event(event, report)
        elif event_type_id == event_ids['carry']:
            self._validate_carry_event(event, report)
        elif event_type_id == event_ids['goalkeeper']:
            self._validate_goalkeeper_event(event, report)
        else:
            # Generic validation for other event types
            self._validate_generic_event_features(event, event_type_id, report)

    def _validate_shot_event(self, event: np.ndarray, report: ValidationReport) -> None:
        """
        Validate shot-specific features.

        Shot features (starting at index 71):
        - shot.type.id (71)
        - shot.end_location (72-74): x, y, z coordinates
        - shot.statsbomb_xg (82): Expected goals (0-1)
        - shot.outcome.id (84)
        - shot.freeze_frame (85-128): 22 players * 2 features
        """
        self.logger.debug("Validating shot-specific features")

        # Validate shot end location
        shot_end_x = event[self.SHOT_END_X_IDX]
        shot_end_y = event[self.SHOT_END_Y_IDX]
        shot_end_z = event[self.SHOT_END_Z_IDX]

        self._validate_range_feature(
            shot_end_x, "shot.end_location[0]", self.SHOT_END_X_IDX,
            0.0, 120.0, "meters", report,
            explanation="Shot end X location on the pitch (0-120m)"
        )
        self._validate_range_feature(
            shot_end_y, "shot.end_location[1]", self.SHOT_END_Y_IDX,
            0.0, 80.0, "meters", report,
            explanation="Shot end Y location on the pitch (0-80m)"
        )
        self._validate_range_feature(
            shot_end_z, "shot.end_location[2]", self.SHOT_END_Z_IDX,
            0.0, 5.0, "meters", report,
            explanation="Shot end Z location (height), max 5m based on data exploration"
        )

        # Validate xG (expected goals)
        self._validate_range_feature(
            event[self.SHOT_XG_IDX], "shot.statsbomb_xg", self.SHOT_XG_IDX,
            0.0, 1.0, "probability", report,
            explanation="Expected goals (xG) is a probability between 0 and 1"
        )

        # Validate that shot starts from a reasonable location
        # Shots should typically originate from opponent's half
        shot_start_x = event[self.X_LOCATION_IDX]
        if shot_start_x < 0.3:  # Less than 30% of field (own half)
            severity = IssueSeverity.WARNING if self.strictness != StrictnessLevel.STRICT else IssueSeverity.ERROR
            issue = ValidationIssue(
                code="UNUSUAL_SHOT_LOCATION",
                message=f"Shot originates from own half (x={shot_start_x:.3f})",
                severity=severity,
                field_name="location[0]",
                field_index=self.X_LOCATION_IDX,
                actual_value=shot_start_x,
                explanation=(
                    "Shots typically originate from the opponent's half of the field. "
                    "A shot from your own half is unusual (though possible in rare cases like long-range efforts)."
                )
            )
            report.add_issue(issue)
            self.logger.warning(f"Unusual shot location: x={shot_start_x:.3f}")

        # Validate that end location is different from start location
        if abs(shot_end_x - shot_start_x) < 0.01 and abs(shot_end_y - event[self.Y_LOCATION_IDX]) < 0.01:
            issue = ValidationIssue(
                code="SHOT_NO_MOVEMENT",
                message="Shot end location is the same as start location",
                severity=IssueSeverity.WARNING,
                explanation="Shots should travel some distance from origin to end location"
            )
            report.add_issue(issue)
            self.logger.warning("Shot has no movement from start to end")

        # Validate freeze frame features (indices 85-128: 44 values = 22 players * 2 features)
        freeze_frame_start = self.SHOT_FREEZE_FRAME_START
        freeze_frame_data = event[freeze_frame_start:freeze_frame_start + 44]

        # Check if freeze frame data is present (not all zeros)
        if np.all(freeze_frame_data == 0):
            severity = IssueSeverity.INFO if self.strictness == StrictnessLevel.LENIENT else IssueSeverity.WARNING
            issue = ValidationIssue(
                code="MISSING_FREEZE_FRAME",
                message="Shot event has no freeze frame data",
                severity=severity,
                explanation=(
                    "Shot events typically include freeze frame data (positions of all 22 players). "
                    "Missing freeze frame data might indicate incomplete event data."
                )
            )
            report.add_issue(issue)
            self.logger.info("Shot has no freeze frame data")
        else:
            # Validate that freeze frame positions are within field bounds
            # Each pair represents (x, y) normalized positions
            for i in range(22):
                x_idx = freeze_frame_start + i * 2
                y_idx = freeze_frame_start + i * 2 + 1
                if event[x_idx] > 0 or event[y_idx] > 0:  # If player data exists
                    if not (0 <= event[x_idx] <= 1 and 0 <= event[y_idx] <= 1):
                        issue = ValidationIssue(
                            code="INVALID_FREEZE_FRAME_POSITION",
                            message=f"Player {i} freeze frame position out of bounds",
                            severity=IssueSeverity.ERROR,
                            field_index=x_idx,
                            actual_value=(event[x_idx], event[y_idx]),
                            explanation=f"Player positions in freeze frame must be normalized to [0, 1]"
                        )
                        report.add_issue(issue)
                        self.logger.error(
                            f"Invalid freeze frame position for player {i}: "
                            f"({event[x_idx]}, {event[y_idx]})"
                        )

        self.logger.debug("Shot validation complete")

    def _validate_pass_event(self, event: np.ndarray, report: ValidationReport) -> None:
        """
        Validate pass-specific features.

        Pass features (starting at index 47):
        - pass.length (48): Distance of pass
        - pass.angle (49): Angle of pass (-π to π)
        - pass.end_location (51-52): x, y coordinates
        - pass.recipient.id (64): Recipient player position
        """
        self.logger.debug("Validating pass-specific features")

        # Validate pass length
        self._validate_range_feature(
            event[self.PASS_LENGTH_IDX], "pass.length", self.PASS_LENGTH_IDX,
            0.0, 120.0, "meters", report,
            explanation="Pass length is the distance the ball travels (0-120m, the length of the pitch)"
        )

        # Validate pass angle
        self._validate_range_feature(
            event[self.PASS_ANGLE_IDX], "pass.angle", self.PASS_ANGLE_IDX,
            -3.15, 3.15, "radians", report,
            explanation="Pass angle in radians (-π to π, representing all directions)"
        )

        # Validate pass end location
        self._validate_range_feature(
            event[self.PASS_END_X_IDX], "pass.end_location[0]", self.PASS_END_X_IDX,
            0.0, 120.0, "meters", report,
            explanation="Pass end X location on the pitch"
        )
        self._validate_range_feature(
            event[self.PASS_END_Y_IDX], "pass.end_location[1]", self.PASS_END_Y_IDX,
            0.0, 80.0, "meters", report,
            explanation="Pass end Y location on the pitch"
        )

        # Validate that pass end location is different from start location
        start_x = event[self.X_LOCATION_IDX]
        start_y = event[self.Y_LOCATION_IDX]
        end_x = event[self.PASS_END_X_IDX]
        end_y = event[self.PASS_END_Y_IDX]

        distance = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        if distance < 0.01:  # Less than 1cm
            issue = ValidationIssue(
                code="PASS_NO_MOVEMENT",
                message="Pass end location is the same as start location",
                severity=IssueSeverity.ERROR,
                explanation="Passes must travel some distance. A pass to the same location is invalid."
            )
            report.add_issue(issue)
            self.logger.error("Pass has zero distance")

        # Validate pass length consistency with locations
        # Denormalize locations (multiply by field dimensions)
        actual_distance = distance * max(120, 80)  # Approximate denormalization
        pass_length_normalized = event[self.PASS_LENGTH_IDX]
        pass_length = pass_length_normalized * 120  # Denormalize

        if abs(actual_distance - pass_length) > 10:  # More than 10m discrepancy
            severity = IssueSeverity.WARNING if self.strictness == StrictnessLevel.LENIENT else IssueSeverity.ERROR
            issue = ValidationIssue(
                code="PASS_LENGTH_MISMATCH",
                message=f"Pass length ({pass_length:.1f}m) doesn't match location distance ({actual_distance:.1f}m)",
                severity=severity,
                field_name="pass.length",
                field_index=self.PASS_LENGTH_IDX,
                expected_value=f"~{actual_distance:.1f}m",
                actual_value=f"{pass_length:.1f}m",
                explanation=(
                    "The pass.length field should match the distance between start and end locations. "
                    "A significant mismatch suggests data inconsistency."
                )
            )
            report.add_issue(issue)
            self.logger.warning(f"Pass length mismatch: length={pass_length:.1f}m, distance={actual_distance:.1f}m")

        self.logger.debug("Pass validation complete")

    def _validate_carry_event(self, event: np.ndarray, report: ValidationReport) -> None:
        """
        Validate carry-specific features.

        Carry features (starting at index 69):
        - carry.end_location (69-70): x, y coordinates
        """
        self.logger.debug("Validating carry-specific features")

        carry_end_x_idx = 69
        carry_end_y_idx = 70

        # Validate carry end location
        self._validate_range_feature(
            event[carry_end_x_idx], "carry.end_location[0]", carry_end_x_idx,
            0.0, 120.0, "meters", report,
            explanation="Carry end X location on the pitch"
        )
        self._validate_range_feature(
            event[carry_end_y_idx], "carry.end_location[1]", carry_end_y_idx,
            0.0, 80.0, "meters", report,
            explanation="Carry end Y location on the pitch"
        )

        # Validate that carry moved the ball
        start_x = event[self.X_LOCATION_IDX]
        start_y = event[self.Y_LOCATION_IDX]
        end_x = event[carry_end_x_idx]
        end_y = event[carry_end_y_idx]

        distance = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        if distance < 0.01:
            severity = IssueSeverity.WARNING if self.strictness == StrictnessLevel.LENIENT else IssueSeverity.ERROR
            issue = ValidationIssue(
                code="CARRY_NO_MOVEMENT",
                message="Carry event has no movement from start to end",
                severity=severity,
                explanation="Carry events represent a player moving with the ball. Zero movement is unusual."
            )
            report.add_issue(issue)
            self.logger.warning("Carry has zero distance")

        self.logger.debug("Carry validation complete")

    def _validate_goalkeeper_event(self, event: np.ndarray, report: ValidationReport) -> None:
        """
        Validate goalkeeper-specific features.

        Goalkeeper features (starting at index 38):
        - goalkeeper.end_location (43-44): x, y coordinates
        """
        self.logger.debug("Validating goalkeeper-specific features")

        gk_end_x_idx = 43
        gk_end_y_idx = 44

        # Validate goalkeeper end location
        self._validate_range_feature(
            event[gk_end_x_idx], "goalkeeper.end_location[0]", gk_end_x_idx,
            0.0, 120.0, "meters", report,
            explanation="Goalkeeper action end X location"
        )
        self._validate_range_feature(
            event[gk_end_y_idx], "goalkeeper.end_location[1]", gk_end_y_idx,
            0.0, 80.0, "meters", report,
            explanation="Goalkeeper action end Y location"
        )

        # Validate that goalkeeper is near their own goal
        # Assuming defending the left goal (x near 0) or right goal (x near 120)
        gk_x = event[self.X_LOCATION_IDX]
        if not (gk_x < 0.2 or gk_x > 0.8):  # Not near either goal
            severity = IssueSeverity.INFO if self.strictness == StrictnessLevel.LENIENT else IssueSeverity.WARNING
            issue = ValidationIssue(
                code="GOALKEEPER_UNUSUAL_LOCATION",
                message=f"Goalkeeper action at unusual location (x={gk_x:.3f})",
                severity=severity,
                field_name="location[0]",
                field_index=self.X_LOCATION_IDX,
                actual_value=gk_x,
                explanation=(
                    "Goalkeeper actions typically occur near the goal (x < 0.2 or x > 0.8). "
                    "A goalkeeper action in midfield is unusual."
                )
            )
            report.add_issue(issue)
            self.logger.info(f"Goalkeeper at unusual location: x={gk_x:.3f}")

        self.logger.debug("Goalkeeper validation complete")

    def _validate_generic_event_features(
        self,
        event: np.ndarray,
        event_type_id: int,
        report: ValidationReport
    ) -> None:
        """
        Validate features for event types without specific validators.

        Checks that:
        - Event-specific features are within [0, 1] (normalized)
        - No unexpected non-zero values outside the event's designated range
        """
        event_config = event_types_mapping.get(event_type_id, {})
        starting_index = event_config.get("starting_index", -1)

        if starting_index < 0:
            return

        # Get the range of indices for this event type
        feature_parsers = event_config.get("feature_parsers", {})
        num_features = len(feature_parsers)

        if num_features == 0:
            # Event has no specific features
            self.logger.debug(f"Event type {event_type_id} has no specific features")
            return

        # Check that values in the event's range are valid (0 to 1)
        event_features = event[starting_index:starting_index + num_features]

        if np.any((event_features < 0) | (event_features > 1)):
            out_of_range = np.where((event_features < 0) | (event_features > 1))[0]
            issue = ValidationIssue(
                code="EVENT_FEATURE_OUT_OF_RANGE",
                message=f"Event-specific features out of [0, 1] range at offsets: {out_of_range.tolist()}",
                severity=IssueSeverity.ERROR,
                explanation=(
                    f"Features for {self.event_id_to_name.get(event_type_id, 'this event')} "
                    f"(indices {starting_index}-{starting_index+num_features-1}) must be normalized to [0, 1]"
                )
            )
            report.add_issue(issue)
            self.logger.error(
                f"Event features out of range at indices {starting_index + out_of_range}"
            )

        self.logger.debug(f"Generic validation complete for event type {event_type_id}")

    def _validate_categorical_feature(
        self,
        value: float,
        field_name: str,
        field_index: int,
        valid_categories: List[int],
        human_name: str,
        report: ValidationReport,
        explanation: str = None
    ) -> None:
        """Helper to validate a categorical feature."""
        # Get the categorical parser
        num_categories = len(valid_categories)

        # Check if value is in valid range
        if not (0 <= value <= 1):
            issue = ValidationIssue(
                code="CATEGORICAL_OUT_OF_RANGE",
                message=f"{human_name} value {value} is outside normalized range [0, 1]",
                severity=IssueSeverity.ERROR,
                field_name=field_name,
                field_index=field_index,
                expected_value="0.0 to 1.0",
                actual_value=value,
                explanation=explanation or f"{human_name} is normalized to range [0, 1]"
            )
            report.add_issue(issue)
            self.logger.error(f"{field_name} out of range: {value}")

    def _validate_range_feature(
        self,
        value: float,
        field_name: str,
        field_index: int,
        min_val: float,
        max_val: float,
        unit: str,
        report: ValidationReport,
        explanation: str = None
    ) -> None:
        """Helper to validate a range feature."""
        # Value should be normalized to [0, 1]
        if not (0 <= value <= 1):
            tolerance = 0.01 if self.strictness == StrictnessLevel.LENIENT else 0.0
            if value < -tolerance or value > 1 + tolerance:
                issue = ValidationIssue(
                    code="RANGE_OUT_OF_BOUNDS",
                    message=f"{field_name} value {value} is outside normalized range [0, 1]",
                    severity=IssueSeverity.ERROR,
                    field_name=field_name,
                    field_index=field_index,
                    expected_value="0.0 to 1.0",
                    actual_value=value,
                    explanation=(
                        explanation or
                        f"{field_name} is normalized from range [{min_val}, {max_val}] {unit} to [0, 1]"
                    )
                )
                report.add_issue(issue)
                self.logger.error(f"{field_name} out of range: {value}")

    def _validate_boolean_feature(
        self,
        value: float,
        field_name: str,
        field_index: int,
        report: ValidationReport
    ) -> None:
        """Helper to validate a boolean feature (0 or 1)."""
        # Boolean features are categorical with 2 categories: [0, 1]
        # Normalized as: 0 -> 0.0, 1 -> 0.5 or 1.0 depending on implementation
        # Let's accept values that round to 0 or 1 when denormalized

        if not (0 <= value <= 1):
            issue = ValidationIssue(
                code="BOOLEAN_OUT_OF_RANGE",
                message=f"{field_name} value {value} is outside range [0, 1]",
                severity=IssueSeverity.ERROR,
                field_name=field_name,
                field_index=field_index,
                expected_value="0.0 or close to 1.0",
                actual_value=value,
                explanation=f"{field_name} is a boolean field (True/False)"
            )
            report.add_issue(issue)
            self.logger.error(f"{field_name} out of range: {value}")

    def _validate_location(
        self,
        x: float,
        y: float,
        field_name: str,
        field_index: int,
        report: ValidationReport
    ) -> None:
        """
        Validate location coordinates.

        X coordinate: 0-120m (length of pitch)
        Y coordinate: 0-80m (width of pitch)
        Both normalized to [0, 1]
        """
        if not (0 <= x <= 1):
            issue = ValidationIssue(
                code="X_LOCATION_OUT_OF_BOUNDS",
                message=f"X location {x} is outside normalized range [0, 1]",
                severity=IssueSeverity.ERROR,
                field_name=f"{field_name}[0]",
                field_index=field_index,
                expected_value="0.0 to 1.0 (representing 0-120m)",
                actual_value=x,
                explanation="X coordinate represents position along the length of the pitch (0-120 meters)"
            )
            report.add_issue(issue)
            self.logger.error(f"X location out of bounds: {x}")

        if not (0 <= y <= 1):
            issue = ValidationIssue(
                code="Y_LOCATION_OUT_OF_BOUNDS",
                message=f"Y location {y} is outside normalized range [0, 1]",
                severity=IssueSeverity.ERROR,
                field_name=f"{field_name}[1]",
                field_index=field_index + 1,
                expected_value="0.0 to 1.0 (representing 0-80m)",
                actual_value=y,
                explanation="Y coordinate represents position along the width of the pitch (0-80 meters)"
            )
            report.add_issue(issue)
            self.logger.error(f"Y location out of bounds: {y}")

    def _calculate_validity_score(self, report: ValidationReport) -> float:
        """
        Calculate a validity score from 0.0 to 1.0 based on issues found.

        Scoring:
        - Start at 1.0
        - Each ERROR: -0.2
        - Each WARNING: -0.05
        - Each INFO: -0.01
        - Minimum: 0.0
        """
        score = 1.0
        score -= report.error_count * 0.2
        score -= report.warning_count * 0.05
        score -= report.info_count * 0.01
        return max(0.0, score)

    # ==================== Sequence Validation Methods ====================

    def _validate_chronological_order(
        self,
        events: np.ndarray,
        report: SequenceValidationReport
    ) -> None:
        """
        Validate that events are in chronological order.

        Checks:
        - Periods are non-decreasing
        - Within same period, time is non-decreasing
        """
        self.logger.debug("Validating chronological order")

        for i in range(len(events) - 1):
            curr_period = events[i][self.PERIOD_IDX]
            next_period = events[i + 1][self.PERIOD_IDX]

            curr_minute = events[i][self.MINUTE_IDX]
            next_minute = events[i + 1][self.MINUTE_IDX]

            curr_second = events[i][self.SECOND_IDX]
            next_second = events[i + 1][self.SECOND_IDX]

            # Denormalize period (categorical)
            curr_period_val = round(curr_period * 5)  # Periods 1-5
            next_period_val = round(next_period * 5)

            # Denormalize minute and second (range)
            curr_minute_val = curr_minute * 60
            next_minute_val = next_minute * 60
            curr_second_val = round(curr_second * 60)
            next_second_val = round(next_second * 60)

            # Calculate total time in seconds
            curr_time = curr_period_val * 45 * 60 + curr_minute_val * 60 + curr_second_val
            next_time = next_period_val * 45 * 60 + next_minute_val * 60 + next_second_val

            if next_time < curr_time:
                issue = ValidationIssue(
                    code="NON_CHRONOLOGICAL_ORDER",
                    message=f"Events {i} and {i+1} are not in chronological order",
                    severity=IssueSeverity.ERROR,
                    explanation=(
                        f"Event {i} occurs at period {curr_period_val}, "
                        f"minute {curr_minute_val:.1f}, second {curr_second_val}, "
                        f"but event {i+1} occurs at period {next_period_val}, "
                        f"minute {next_minute_val:.1f}, second {next_second_val}. "
                        "Events must be in chronological order."
                    )
                )
                report.add_sequence_issue(issue)
                self.logger.error(
                    f"Non-chronological order between events {i} and {i+1}: "
                    f"{curr_time:.1f}s -> {next_time:.1f}s"
                )

        self.logger.debug("Chronological order validation complete")

    def _validate_possession_continuity(
        self,
        events: np.ndarray,
        report: SequenceValidationReport
    ) -> None:
        """
        Validate possession continuity across the sequence.

        Checks:
        - Possession changes only occur on valid events (interceptions, tackles, etc.)
        - Possession team is consistent when not changing
        """
        self.logger.debug("Validating possession continuity")

        for i in range(len(events) - 1):
            curr_possession = events[i][self.POSSESSION_TEAM_IDX]
            next_possession = events[i + 1][self.POSSESSION_TEAM_IDX]

            # Check if possession changed
            if abs(curr_possession - next_possession) > 0.01:  # Possession changed
                # Get event type of current event
                curr_event_type_normalized = events[i][self.EVENT_TYPE_IDX]
                curr_event_type = self._get_event_type_from_normalized(curr_event_type_normalized)

                next_event_type_normalized = events[i + 1][self.EVENT_TYPE_IDX]
                next_event_type = self._get_event_type_from_normalized(next_event_type_normalized)

                # Check if either event is a possession-changing event
                is_valid_change = (
                    curr_event_type in self.POSSESSION_CHANGE_EVENTS or
                    next_event_type in self.POSSESSION_CHANGE_EVENTS
                )

                if not is_valid_change:
                    curr_event_name = self.event_id_to_name.get(curr_event_type, "Unknown")
                    next_event_name = self.event_id_to_name.get(next_event_type, "Unknown")

                    severity = IssueSeverity.WARNING if self.strictness == StrictnessLevel.LENIENT else IssueSeverity.ERROR
                    issue = ValidationIssue(
                        code="INVALID_POSSESSION_CHANGE",
                        message=f"Possession changed between events {i} ({curr_event_name}) and {i+1} ({next_event_name}) without a possession-changing event",
                        severity=severity,
                        explanation=(
                            f"Possession changed from team {curr_possession:.3f} to {next_possession:.3f}, "
                            f"but neither '{curr_event_name}' nor '{next_event_name}' are typical "
                            "possession-changing events (interception, duel, tackle, etc.)"
                        )
                    )
                    report.add_sequence_issue(issue)
                    self.logger.warning(
                        f"Invalid possession change between {i} ({curr_event_name}) and {i+1} ({next_event_name})"
                    )

        self.logger.debug("Possession continuity validation complete")

    def _validate_location_plausibility(
        self,
        events: np.ndarray,
        report: SequenceValidationReport
    ) -> None:
        """
        Validate that location transitions between events are plausible.

        The ball can't teleport across the field - there should be reasonable
        continuity in location between consecutive events.
        """
        self.logger.debug("Validating location plausibility")

        for i in range(len(events) - 1):
            curr_x = events[i][self.X_LOCATION_IDX]
            curr_y = events[i][self.Y_LOCATION_IDX]
            next_x = events[i + 1][self.X_LOCATION_IDX]
            next_y = events[i + 1][self.Y_LOCATION_IDX]

            # Calculate distance (in normalized coordinates)
            distance = np.sqrt((next_x - curr_x)**2 + (next_y - curr_y)**2)

            # Denormalize to meters (approximate)
            # Field is 120m x 80m, diagonal is ~145m
            distance_meters = distance * 145  # Approximate

            if distance_meters > self.max_location_jump:
                curr_event_type = self._get_event_type_from_normalized(events[i][self.EVENT_TYPE_IDX])
                next_event_type = self._get_event_type_from_normalized(events[i + 1][self.EVENT_TYPE_IDX])

                curr_event_name = self.event_id_to_name.get(curr_event_type, "Unknown")
                next_event_name = self.event_id_to_name.get(next_event_type, "Unknown")

                severity = IssueSeverity.WARNING if self.strictness == StrictnessLevel.LENIENT else IssueSeverity.ERROR
                issue = ValidationIssue(
                    code="IMPLAUSIBLE_LOCATION_JUMP",
                    message=f"Large location jump ({distance_meters:.1f}m) between events {i} and {i+1}",
                    severity=severity,
                    actual_value=f"{distance_meters:.1f}m",
                    expected_value=f"< {self.max_location_jump}m",
                    explanation=(
                        f"Events {i} ({curr_event_name}) at ({curr_x:.3f}, {curr_y:.3f}) "
                        f"and {i+1} ({next_event_name}) at ({next_x:.3f}, {next_y:.3f}) "
                        f"are {distance_meters:.1f}m apart. This is unusually large and might "
                        "indicate missing events or data errors."
                    )
                )
                report.add_sequence_issue(issue)
                self.logger.warning(
                    f"Large location jump ({distance_meters:.1f}m) between events {i} and {i+1}"
                )

        self.logger.debug("Location plausibility validation complete")

    def _validate_time_gaps(
        self,
        events: np.ndarray,
        report: SequenceValidationReport
    ) -> None:
        """
        Validate that time gaps between events are reasonable.

        Large time gaps might indicate missing events or data issues.
        """
        self.logger.debug("Validating time gaps")

        for i in range(len(events) - 1):
            curr_period = events[i][self.PERIOD_IDX]
            next_period = events[i + 1][self.PERIOD_IDX]

            curr_minute = events[i][self.MINUTE_IDX]
            next_minute = events[i + 1][self.MINUTE_IDX]

            curr_second = events[i][self.SECOND_IDX]
            next_second = events[i + 1][self.SECOND_IDX]

            # Denormalize
            curr_period_val = round(curr_period * 5)
            next_period_val = round(next_period * 5)
            curr_minute_val = curr_minute * 60
            next_minute_val = next_minute * 60
            curr_second_val = round(curr_second * 60)
            next_second_val = round(next_second * 60)

            # Calculate time difference in seconds
            if curr_period_val == next_period_val:
                time_gap = (next_minute_val - curr_minute_val) * 60 + (next_second_val - curr_second_val)
            else:
                # Different periods - skip validation
                continue

            if time_gap > self.max_time_gap:
                severity = IssueSeverity.INFO if self.strictness == StrictnessLevel.LENIENT else IssueSeverity.WARNING
                issue = ValidationIssue(
                    code="LARGE_TIME_GAP",
                    message=f"Large time gap ({time_gap:.1f}s) between events {i} and {i+1}",
                    severity=severity,
                    actual_value=f"{time_gap:.1f}s",
                    expected_value=f"< {self.max_time_gap}s",
                    explanation=(
                        f"Events {i} and {i+1} are {time_gap:.1f} seconds apart. "
                        "This is longer than expected and might indicate missing events."
                    )
                )
                report.add_sequence_issue(issue)
                self.logger.info(f"Large time gap ({time_gap:.1f}s) between events {i} and {i+1}")

        self.logger.debug("Time gap validation complete")

    def _get_event_type_from_normalized(self, normalized_value: float) -> Optional[int]:
        """Get event type ID from normalized value."""
        common_config = event_types_mapping["common"]
        type_parser = common_config["feature_parsers"]["type.id"]
        return self._denormalize_categorical(
            normalized_value,
            type_parser.categories,
            type_parser.num_categories
        )

    def _calculate_sequence_validity_score(
        self,
        report: SequenceValidationReport
    ) -> float:
        """
        Calculate overall sequence validity score.

        Combines:
        - Average validity score of individual events
        - Penalty for sequence-level issues
        """
        # Average of individual event scores
        if report.total_events > 0:
            avg_event_score = sum(r.validity_score for r in report.event_reports) / report.total_events
        else:
            avg_event_score = 0.0

        # Penalty for sequence issues
        sequence_penalty = report.sequence_error_count * 0.2 + report.sequence_warning_count * 0.05

        return max(0.0, avg_event_score - sequence_penalty)

