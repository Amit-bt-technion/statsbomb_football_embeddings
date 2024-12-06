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
        match_parser = kwargs["match_parser"]
        team_id = kwargs["team_id"]
        # positions in the teams_and_players mapping are normalized
        return [match_parser.teams_and_players[team_id][val]]
