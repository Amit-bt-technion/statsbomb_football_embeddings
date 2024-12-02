import json
import pandas as pd
from urllib.request import Request, urlopen
import logging

logger = logging.getLogger(__name__)

from tokenizer.event_parsers import (
    ball_receipt_event_parser,
    ball_recovery_event_parser,
    dispossessed_event_parser,
    duel_event_parser,
    on_camera_event_parser,
    block_event_parser,
    offside_event_parser,
    clearance_event_parser,
    interception_event_parser,
    dribble_event_parser,
    shot_event_parser,
    pressure_event_parser,
    substitution_event_parser,
    own_goal_against_event_parser,
    foul_won_event_parser,
    foul_committed_event_parser,
    goal_keeper_event_parser,
    bad_behavior_event_parser,
    own_goal_for_event_parser,
    player_on_event_parser,
    player_off_event_parser,
    shield_event_parser,
    pass_event_parser,
    fifty_fifty_event_parser,
    starting_xi_event_parser,
    tactical_shift_event_parser,
    error_event_parser,
    miscontrol_event_parser,
    dribble_past_event_parser,
    injury_stoppage_event_parser,
    referee_ball_drop_event_parser,
    carry_event_parser,
    skip_event_type_parser
)

# static data structures
event_types_to_parsers_mapping = {
    2: ball_recovery_event_parser,
    3: dispossessed_event_parser,
    4: duel_event_parser,
    5: skip_event_type_parser,
    6: block_event_parser,
    8: offside_event_parser,
    9: clearance_event_parser,
    10: interception_event_parser,
    14: dribble_past_event_parser,
    16: shot_event_parser,
    17: pressure_event_parser,
    18: skip_event_type_parser,
    19: substitution_event_parser,
    20: own_goal_against_event_parser,
    21: foul_won_event_parser,
    22: foul_committed_event_parser,
    23: goal_keeper_event_parser,
    24: bad_behavior_event_parser,
    25: own_goal_for_event_parser,
    26: player_on_event_parser,
    27: player_off_event_parser,
    28: shield_event_parser,
    30: pass_event_parser,
    33: fifty_fifty_event_parser,
    34: skip_event_type_parser,
    35: starting_xi_event_parser,
    36: tactical_shift_event_parser,
    37: error_event_parser,
    38: miscontrol_event_parser,
    39: dribble_past_event_parser,
    40: injury_stoppage_event_parser,
    41: referee_ball_drop_event_parser,
    42: ball_receipt_event_parser,
    43: carry_event_parser
}


class Tokenizer:
    def __init__(self, path: str, is_online_resource: bool = False):
        try:
            if not is_online_resource:
                with open(path) as match_json:
                    self.data = json.load(match_json)
            else:
                with urlopen(path) as match_json:
                    self.data = json.load(match_json)
        except FileNotFoundError:
            logger.error("json file not found!")
        self.tokenized_events_matrix = pd.DataFrame()  # initialize

    def get_tokenized_match_events(self):
        for event in self.data:
            print(event["type"]["name"])

    def update_common_tactics_features(self):
        """
        This method is called by event parsers such as starting_xi_event_parser, tactical_shift_event_parser to update
        the global vector representation of players on the field and formation. This design where parsers aren't
        methods is chosen for separation of concerns and streamlining the tokenizer class, and to allow easy & readably
        event parser invocations.
        """
        pass
