import pandas as pd
from typing import List, Self, Union

from tokenizer import common_features_parsers, event_types_mapping
from tokenizer.utils.helper_functions import get_value_of_nested_key
from tokenizer.feature_parsers import FeatureParser, CategoricalFeatureParser, RangeFeatureParser

player_position_parser = CategoricalFeatureParser("player position id", [i for i in range(1, 26)])


class MatchEventsParser:
    def __init__(
        self,
        common_features_start_index: int,
        vector_size: int,
    ):
        self.common_features_start_index = common_features_start_index
        self.num_of_common_features = len(common_features_parsers)
        self.vector_size = vector_size
        self.tokenized_event = None
        self.teams_and_players: dict[int, dict] = {}
        self.special_events_mapping = {
            19: self.substitution_event_handler,
            # starting_xi event type
            35: self.lineup_handler,
            # tactical_shift event type
            36: self.lineup_handler,
        }

    def parse_event(self, event: dict) -> Union[pd.Series, None]:
        self.tokenized_event = pd.Series(0, index=range(self.vector_size), dtype=float)
        event_id = event["type"]["id"]
        if event_id in self.special_events_mapping:
            self.special_events_mapping[event_id](event)
        if event_types_mapping[event_id]["ignore_event_type"]:
            return None
        self.parse_common_event_features(event)
        self.specific_event_parser(event, event_id)
        return self.tokenized_event

    # **************************************    Feature Parsers     ******************************************
    def parse_common_event_features(self, event: dict):
        """
        parsers the keys in the event object that are common and exist for every event.
        :param event: a single event loaded from match json file.
        :return: a pandas series of length self.num_of_common_features that stores the normalized values after parsing.
        """
        features = pd.Series(0.0, index=range(self.num_of_common_features))
        for i, (dict_path, feature_parser) in enumerate(common_features_parsers.items()):
            val = feature_parser.get_normalized(get_value_of_nested_key(event, dict_path))
            features.iloc[i] = val

        end_index = self.common_features_start_index + self.num_of_common_features
        self.tokenized_event.iloc[self.common_features_start_index: end_index] = features
        return features

    def specific_event_parser(self, event: dict, event_id: int):
        event_mapping = event_types_mapping[event_id]
        starting_index = event_mapping["starting_index"]
        parsers = event_mapping["feature_parsers"]
        # calculate total number of features in the specific event's range
        total_num_of_features = len(parsers) + event_mapping.get("num_of_special_features", 0)
        features = []

        # interating through regular feature parsers
        for dict_path, feature_parser in parsers.items():
            val = feature_parser.get_normalized(get_value_of_nested_key(event, dict_path))
            features.append(val)

        # calling special feature parsing functions that utilize the bottom part of index range in vector
        special_parsers = event_mapping.get("special_parsers", {})
        for dict_path, special_parser in special_parsers.items():
            vals = special_parser.get_normalized(
                get_value_of_nested_key(event, dict_path),
                match_parser=self,
                team_id=event["team"]["id"]
            )
            features.extend(vals)
        self.tokenized_event.iloc[starting_index: starting_index + total_num_of_features] = features
        return features

    # **************************************    Special event_handlers     ******************************************

    def lineup_handler(self, event: dict):
        team_id = event["team"]["id"]
        self.teams_and_players[team_id] = {}
        lineup = event["tactics"]["lineup"]
        for member in lineup:
            player_id = member["player"]["id"]
            player_position_id = member["position"]["id"]
            self.teams_and_players[team_id][player_id] = player_position_parser.get_normalized(player_position_id)
        # self.teams_and_players[team_id]["formation"] = event["tactics"]["formation"]

    def substitution_event_handler(self, event: dict):
        """
        this method is to be invoked alongside the event parser to update the teams_and_players property.
        :param event: a single substituted event loaded from match json file.
        """
        team_id = event["team"]["id"]
        out_player_id = event["player"]["id"]
        in_player_id = event["substitution"]["replacement"]["id"]
        # retaining the previous players' position as there is no attribute in the event that indicates a change
        prev_position = self.teams_and_players[team_id][out_player_id]
        del self.teams_and_players[team_id][out_player_id]
        self.teams_and_players[team_id][in_player_id] = prev_position
