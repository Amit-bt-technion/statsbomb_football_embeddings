import pandas as pd
from typing import List, Self, Union


class MatchEventsParser:
    def __init__(
        self,
        event_type_mapping: dict[int: tuple[Self, int, int]],
        common_feature_mapping: tuple[Self, int, int],
        vector_size: int,
    ):
        self.event_type_mapping = event_type_mapping
        self.common_feature_mapping = common_feature_mapping
        self.vector_size = vector_size
        self.tokenized_event = None
        self.teams_and_players: Union[dict[int, dict], None] = None

    def parse_event(self, event: dict):
        self.tokenized_event = pd.Series(0, index=range(self.vector_size))
        # call parse_common_features
        # extract  specific event block (data)
        # call event parser of this event using the mapping and event_type_id property with data
        pass

    # **************************************    Feature Parsers     ******************************************
    def common_features_event_parser(self, start_index: int, num_of_features: int):
        pass

    def ball_receipt_event_parser(self, start_index: int, num_of_features: int):
        pass

    def ball_recovery_event_parser(self, start_index: int, num_of_features: int):
        pass

    def dispossessed_event_parser(self, start_index: int, num_of_features: int):
        pass

    def duel_event_parser(self, start_index: int, num_of_features: int):
        pass

    def on_camera_event_parser(self, start_index: int, num_of_features: int):
        pass

    def block_event_parser(self, start_index: int, num_of_features: int):
        pass

    def offside_event_parser(self, start_index: int, num_of_features: int):
        pass

    def clearance_event_parser(self, start_index: int, num_of_features: int):
        pass

    def interception_event_parser(self, start_index: int, num_of_features: int):
        pass

    def dribble_event_parser(self, start_index: int, num_of_features: int):
        pass

    def shot_event_parser(self, start_index: int, num_of_features: int):
        pass

    def pressure_event_parser(self, start_index: int, num_of_features: int):
        pass

    def substitution_event_parser(self, start_index: int, num_of_features: int):
        pass

    def own_goal_against_event_parser(self, start_index: int, num_of_features: int):
        pass

    def foul_won_event_parser(self, start_index: int, num_of_features: int):
        pass

    def foul_committed_event_parser(self, start_index: int, num_of_features: int):
        pass

    def goal_keeper_event_parser(self, start_index: int, num_of_features: int):
        pass

    def bad_behavior_event_parser(self, start_index: int, num_of_features: int):
        pass

    def own_goal_for_event_parser(self, start_index: int, num_of_features: int):
        pass

    def player_on_event_parser(self, start_index: int, num_of_features: int):
        pass

    def player_off_event_parser(self, start_index: int, num_of_features: int):
        pass

    def shield_event_parser(self, start_index: int, num_of_features: int):
        pass

    def pass_event_parser(self, start_index: int, num_of_features: int):
        pass

    def fifty_fifty_event_parser(self, start_index: int, num_of_features: int):
        pass

    def starting_xi_event_parser(self, start_index: int, num_of_features: int):
        pass

    def tactical_shift_event_parser(self, start_index: int, num_of_features: int):
        pass

    def error_event_parser(self, start_index: int, num_of_features: int):
        pass

    def miscontrol_event_parser(self, start_index: int, num_of_features: int):
        pass

    def dribble_past_event_parser(self, start_index: int, num_of_features: int):
        pass

    def injury_stoppage_event_parser(self, start_index: int, num_of_features: int):
        pass

    def referee_ball_drop_event_parser(self, start_index: int, num_of_features: int):
        pass

    def carry_event_parser(self, start_index: int, num_of_features: int):
        pass

    def skip_event_type_parser(self, start_index: int, num_of_features: int):
        """
        TBDean verdict - not to process these events, but rather incorporate its meaning in ''period" feature
        - half_start_event_parser
        - half_end_event_parser
        """
        pass

