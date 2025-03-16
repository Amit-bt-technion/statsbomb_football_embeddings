import pandas as pd
from typing import List, Self, Union

from tokenizer import event_types_mapping
from tokenizer.utils.helper_functions import get_value_of_nested_key
from tokenizer.feature_parsers import FeatureParser, CategoricalFeatureParser, RangeFeatureParser

player_position_parser = CategoricalFeatureParser("player position id", [i for i in range(1, 26)])


class MatchEventsParser:
    """
    This class handles tokenizing single events.

    Attributes:
        vector_size: the number of features in the output vector.
        tokenized_event: the tokenized vector representation of an event.
        teams_and_players: a dictionary 2 keys for teams, each mapping to a dictionary of player-id to player-position mapping.
        change_teams_and_players: a dictionary of event types that update teams_and_players, and their corresponding handlers.
        cleanup_teams_and_players: a dictionary of event types that should update teams_and_players after parsing the event.
    """
    def __init__(
        self,
        vector_size: int,
    ):
        self.vector_size = vector_size
        self.tokenized_event = None
        self.teams_and_players: dict[int, dict] = {}
        self.change_teams_and_players = {
            19: self.substitution_event_handler,
            # starting_xi event type
            35: self.lineup_handler,
            # tactical_shift event type
            36: self.lineup_handler,
        }
        self.cleanup_teams_and_players = {
            19: self.substitution_event_cleaner
        }

    def parse_event(self, event: dict) -> Union[List, None]:
        """
        Manages the entire flow of event parsing by initializing the vector, extracting the event id, updating the
        teams_and_players attribute and ignoring the event if necessary.
        :param event: the event dictionary as loaded from the json file.
        :return: vector representation of the event.
        """
        self.tokenized_event = [0 for _ in range(self.vector_size)]
        event_id = event["type"]["id"]
        if event_id in self.change_teams_and_players:
            self.change_teams_and_players[event_id](event)
        if event_types_mapping[event_id]["ignore_event_type"]:
            return None
        self.tokenize_event(event, event_id)
        if event_id in self.cleanup_teams_and_players:
            self.cleanup_teams_and_players[event_id](event)
        return self.tokenized_event

    def tokenize_event(self, event: dict, event_id: int, parse_common:bool = True):
        """
        Parses an entire event and returns a vector representation of the event.
        The method is called by parse_event and parsers the common features of the event, and then recurses to parse
        the event-specific events by altering the boolean flag.
        :param event: the event dictionary as loaded from the json file.
        :param event_id: the number representing the type of event.
        :param parse_common: a boolean flag stating whether the method should handle parsing the common or specific features.
        :return: vector representation of the event.
        """
        if parse_common:
            event_mapping = event_types_mapping["common"]
        else:
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
                event=event
            )
            features.extend(vals)
        self.tokenized_event[starting_index: starting_index + total_num_of_features] = features
        if parse_common:
            self.tokenize_event(event, event_id, parse_common=False)
        return self.tokenized_event

    # **************************************    Special event_handlers     ******************************************

    def lineup_handler(self, event: dict):
        """
        Updates the teams_and_players attribute based on starting_xi events.
        :param event: a starting_xi event dictionary as loaded from the json file.
        """
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
        self.teams_and_players[team_id][in_player_id] = prev_position

    def substitution_event_cleaner(self, event: dict):
        """
        this method is to be invoked alongside the event parser to clean the teams_and_players property.
        :param event: a single substituted event loaded from match json file.
        """
        team_id = event["team"]["id"]
        out_player_id = event["player"]["id"]
        del self.teams_and_players[team_id][out_player_id]
