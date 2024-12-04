import json
import pandas as pd
from urllib.request import urlopen
import logging
from typing import List, Union
from tokenizer.match_parser import MatchEventsParser
from tokenizer.feature_parsers import FeatureParser, CategoricalFeatureParser, RangeFeatureParser

logger = logging.getLogger(__name__)

# ************************************************************************************************************
#                                           Parsers Mapping
# ************************************************************************************************************

event_types_mapping = {
    # ball recovery parser
    2: {
        "starting_index": 14,
        "num_of_features": 2,
        "feature_parsers": {
            "ball_recovery.offensive": CategoricalFeatureParser("offensive ball recovery", [0, 1]),
            "ball_recovery.recovery_failure": CategoricalFeatureParser("failed ball recovery", [0, 1]),
        }
    },
    3: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    4: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    5: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    6: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    8: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    9: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    10: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    14: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    16: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    17: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    18: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    19: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    20: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    21: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    22: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    23: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    24: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    25: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    26: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    27: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    28: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    30: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    33: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    34: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    35: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    36: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    37: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    38: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    39: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    40: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    41: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    42: {
        "starting_index": 0,
        "num_of_features": 0,
        "feature_parsers": {

        }
    },
    43: {
        "starting_index": 0,
        "num_of_features": 0,
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

# ************************************************************************************************************
#                                           Tokenizer Class
# ************************************************************************************************************


class Tokenizer:
    def __init__(self, path: str, is_online_resource: bool = False):
        # load the json list of dicts
        try:
            if not is_online_resource:
                with open(path) as match_json:
                    self.data: List[dict] = json.load(match_json)
            else:
                with urlopen(path) as match_json:
                    self.data: List[dict] = json.load(match_json)
        except FileNotFoundError:
            logger.error("json file not found!")

        self.vector_size = 105
        self.tokenized_events_matrix = pd.DataFrame()
        self.match_parser = MatchEventsParser(
            0,
            14,
            self.vector_size
        )

        self.match_parser.load_mappings(
            common_features_parsers,
            event_types_mapping,
        )

    def get_tokenized_match_events(self) -> pd.DataFrame:
        self.match_parser.parse_event(self.data[0])
        # for event in self.data:
        #     self.match_parser.parse_event(event)
            # event_id = event["type"]["id"]
            # event_parser, start_index, features_num = self.event_types_mapping[event_id]
            # event_parser(start_index, features_num)

        return self.tokenized_events_matrix




