"""
StatsBomb Football Tokenizer

A tokenizer for StatsBomb football event data, converting raw match events
into ML-ready feature vectors.
"""

# Import configuration and constants
from tokenizer.config import (
    logger,
    vector_size,
    num_of_players_in_freeze_frame,
    event_ids,
    event_types_mapping,
)

# Import feature parsers
from tokenizer.feature_parsers import (
    FeatureParser,
    CategoricalFeatureParser,
    RangeFeatureParser,
    TeamIdParser,
    MinuteFeatureParser,
    PlayerPositionFeatureParser,
    FreezeFrameFeaturesParser,
    DoNothingParser,
)

# Import main classes
from tokenizer.tokenizer import Tokenizer
from tokenizer.event_parser import EventParser

# Import validation classes
from tokenizer.validation import (
    EventValidator,
    StrictnessLevel,
    ValidationReport,
    ValidationIssue,
    IssueSeverity,
    SequenceValidationReport,
)

__all__ = [
    # Main classes
    "Tokenizer",
    "EventParser",
    # Validation classes
    "EventValidator",
    "StrictnessLevel",
    "ValidationReport",
    "ValidationIssue",
    "IssueSeverity",
    "SequenceValidationReport",
    # Feature parsers
    "FeatureParser",
    "CategoricalFeatureParser",
    "RangeFeatureParser",
    "TeamIdParser",
    "MinuteFeatureParser",
    "PlayerPositionFeatureParser",
    "FreezeFrameFeaturesParser",
    "DoNothingParser",
    # Configuration
    "vector_size",
    "num_of_players_in_freeze_frame",
    "event_ids",
    "event_types_mapping",
    "logger",
]

__version__ = "0.1.0"
