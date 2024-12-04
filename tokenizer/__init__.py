import json
import pandas as pd
from urllib.request import urlopen
import logging
from typing import List, Union
from tokenizer.match_parser import MatchEventsParser
from tokenizer.feature_parsers import FeatureParser, CategoricalFeatureParser, RangeFeatureParser

logger = logging.getLogger(__name__)

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
        self.event_types_mapping: Union[dict[int: tuple[MatchEventsParser, int, int]], None] = None
        self.common_features_parsers: Union[dict[str, FeatureParser], None] = None
        self.match_parser = MatchEventsParser(
            0,
            14,
            self.vector_size
        )
        self.initialize_static_properties()

        self.match_parser.load_mappings(
            self.common_features_parsers,
            self.event_types_mapping,
        )

    def get_tokenized_match_events(self) -> pd.DataFrame:
        self.match_parser.parse_event(self.data[0])
        # for event in self.data:
        #     self.match_parser.parse_event(event)
            # event_id = event["type"]["id"]
            # event_parser, start_index, features_num = self.event_types_mapping[event_id]
            # event_parser(start_index, features_num)

        return self.tokenized_events_matrix

    def initialize_static_properties(self) -> None:
        # mapping of each event id to: parser function, vector index range start, number of indices in vector
        self.event_types_mapping = {
            2: (self.match_parser.ball_recovery_event_parser,),
            3: (self.match_parser.dispossessed_event_parser,),
            4: (self.match_parser.duel_event_parser,),
            5: (self.match_parser.skip_event_type_parser,),
            6: (self.match_parser.block_event_parser,),
            8: (self.match_parser.offside_event_parser,),
            9: (self.match_parser.clearance_event_parser,),
            10: (self.match_parser.interception_event_parser,),
            14: (self.match_parser.dribble_past_event_parser,),
            16: (self.match_parser.shot_event_parser,),
            17: (self.match_parser.pressure_event_parser,),
            18: (self.match_parser.skip_event_type_parser,),
            19: (self.match_parser.substitution_event_parser,),
            20: (self.match_parser.own_goal_against_event_parser,),
            21: (self.match_parser.foul_won_event_parser,),
            22: (self.match_parser.foul_committed_event_parser,),
            23: (self.match_parser.goal_keeper_event_parser,),
            24: (self.match_parser.bad_behavior_event_parser,),
            25: (self.match_parser.own_goal_for_event_parser,),
            26: (self.match_parser.player_on_event_parser,),
            27: (self.match_parser.player_off_event_parser,),
            28: (self.match_parser.shield_event_parser,),
            30: (self.match_parser.pass_event_parser,),
            33: (self.match_parser.fifty_fifty_event_parser,),
            34: (self.match_parser.skip_event_type_parser,),
            35: (self.match_parser.starting_xi_event_parser,),
            36: (self.match_parser.tactical_shift_event_parser,),
            37: (self.match_parser.error_event_parser,),
            38: (self.match_parser.miscontrol_event_parser,),
            39: (self.match_parser.dribble_past_event_parser,),
            40: (self.match_parser.injury_stoppage_event_parser,),
            41: (self.match_parser.referee_ball_drop_event_parser,),
            42: (self.match_parser.ball_receipt_event_parser,),
            43: (self.match_parser.carry_event_parser,)
        }

        # mapping the key (including full hierarchy from dictionary) to feature parser
        self.common_features_parsers = {
            "period": CategoricalFeatureParser("period", [i for i in range(1, 6)]),
            # TODO: awaiting distribution exploration
            "minute": CategoricalFeatureParser("minute", [i for i in range(0, 100)]),
            "second": CategoricalFeatureParser("second", [i for i in range(0, 60)]),
            "type.id": CategoricalFeatureParser("type", [key for key in self.event_types_mapping.keys()]),
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



