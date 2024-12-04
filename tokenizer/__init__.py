import logging
from tokenizer.feature_parsers import FeatureParser, CategoricalFeatureParser, RangeFeatureParser

logger = logging.getLogger(__name__)

# ************************************************************************************************************
#                                           Parsers Mapping
# ************************************************************************************************************
common_features_start_index = 0

event_types_mapping = {
    # ball recovery parser
    2: {
        "ignore_event_type": False,
        "starting_index": 14,
        "feature_parsers": {
            "ball_recovery.offensive": CategoricalFeatureParser("offensive ball recovery", [0, 1]),
            "ball_recovery.recovery_failure": CategoricalFeatureParser("failed ball recovery", [0, 1]),
        }
    },
    3: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    4: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    5: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    6: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    8: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    9: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    10: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    14: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    16: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    17: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    18: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    19: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    20: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    21: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    22: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    23: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    24: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    25: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    26: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    27: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    28: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    30: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    33: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    34: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    35: {
        "ignore_event_type": True,
        "starting_index": -1,
        "feature_parsers": {}
    },
    36: {
        "ignore_event_type": True,
        "starting_index": -1,
        "feature_parsers": {}
    },
    37: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    38: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    39: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    40: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    41: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    42: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
    43: {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {

        }
    },
}

common_features_parsers = {
    "period": CategoricalFeatureParser("period", [i for i in range(1, 6)]),
    # TODO: awaiting distribution exploration
    "minute": CategoricalFeatureParser("minute", [i for i in range(0, 100)]),
    "second": CategoricalFeatureParser("second", [i for i in range(0, 60)]),
    "type.id": CategoricalFeatureParser("type", [key for key in event_types_mapping.keys()]),
    "possession_team.id": CategoricalFeatureParser("possession_team", [0, 1]),
    "play_pattern.id": CategoricalFeatureParser("play_pattern", [i for i in range(1, 10)]),
    "team.id": CategoricalFeatureParser("team", [0, 1]),
    "position.id": CategoricalFeatureParser("position", [i for i in range(1, 26)]),
    "location[0]": RangeFeatureParser("x_location", min_value=0, max_value=120),
    "location[1]": RangeFeatureParser("y_location", min_value=0, max_value=80),
    "duration": RangeFeatureParser("duration", min_value=0, max_value=3),
    "under_pressure": CategoricalFeatureParser("under_pressure", [0, 1]),
    "out": CategoricalFeatureParser("out", [0, 1]),
}
