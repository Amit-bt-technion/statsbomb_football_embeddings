from abc import ABC, abstractmethod
from typing import List, Any, Union
import pandas as pd


# Feature Classes definitions

class FeatureParser(ABC):
    def __init__(self, name: str):
        self.feature_name = name

    # TODO: implement and override as necessary
    @abstractmethod
    def get_normalized(self, val: float) -> Union[float, List[float]]:
        pass

    def __repr__(self):
        return f"{self.feature_name} parser"


class RangeFeatureParser(FeatureParser):
    def __init__(self, name: str, min_value: float, max_value: float) -> None:
        super().__init__(name)
        self.min_value = min_value
        self.max_value = max_value

    def get_normalized(self, val):
        if val > self.max_value:
            val = self.max_value
        if val < self.min_value:
            val = self.min_value
        return (val - self.min_value) / (self.max_value - self.min_value)


class CategoricalFeatureParser(FeatureParser):
    def __init__(self, name: str, categories: List[Any]):
        super().__init__(name)
        self.categories = {value: index + 1 for index, value in enumerate(categories)}
        self.num_categories = len(categories)

    def get_normalized(self, val, **kwargs):
        return self.categories.get(val, 0) / self.num_categories


class PassRecipientFeatureParser(FeatureParser):
    def __init__(self, name: str):
        super().__init__(name)

    def get_normalized(self, val, **kwargs) -> List[float]:
        """
        calculates a normalized value of the position of the player, identified by the id
        :param val: a value representing the player id in the json file
        :param kwargs['match_parser']: a MatchEventParser instance of the current match
        :param kwargs['team_id']: the id of the team whose player recipient belongs to
        :return: the normalized value of the position of the player
        """
        # if val is 0, 'recipient' doesn't exist on 'pass' dict, pass is incomplete
        if val == 0:
            return [0]
        match_parser = kwargs["match_parser"]
        team_id = kwargs["team_id"]
        # positions in the teams_and_players mapping are normalized
        return [match_parser.teams_and_players[team_id][val]]


class FreezeFrameFeaturesParser(FeatureParser):
    def __init__(self, name: str, num_of_features):
        super().__init__(name)
        self.num_of_players = num_of_features // 4

    def get_normalized(self, val: List[float], **kwargs) -> List[float]:
        """
        returns a list of length 4 * num_of_players, containing the normalized values for player position, x location,
        y location, and is teammate for every player in the top num_of_players
        :param val: the freeze_frame object from the shot event
        :param kwargs['match_parser']: a MatchEventParser instance of the current match
        :param kwargs['team_id']: the id of the team whose player recipient belongs to
        :return:
        """
        if type(val) is not list or len(val) == 0:
            return [0 for i in range(4 * self.num_of_players)]

        match_parser = kwargs["match_parser"]
        team_id = kwargs["team_id"]
        features = []

        num_of_players = min(self.num_of_players, len(val))
        for player_obj in val[:num_of_players]:
            # parse if teammate
            # check fo player id under the relevant team
            # extract position from teams_and_players
            player_id = player_obj["player"]["id"]
            features.append(match_parser.teams_and_players[team_id])

