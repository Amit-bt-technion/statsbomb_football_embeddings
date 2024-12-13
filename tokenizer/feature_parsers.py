from abc import ABC, abstractmethod
from typing import List, Any, Union


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
        val = min(val, self.max_value)
        val = max(val, self.min_value)
        return (val - self.min_value) / (self.max_value - self.min_value)


class CategoricalFeatureParser(FeatureParser):
    def __init__(self, name: str, categories: List[Any]):
        super().__init__(name)
        self.categories = {value: index + 1 for index, value in enumerate(sorted(categories))}
        self.num_categories = len(categories)

    def get_normalized(self, val, **kwargs):
        return self.categories.get(val, 0) / self.num_categories


class MinuteFeatureParser(RangeFeatureParser):
    def __init__(self, name: str, min_value: float, max_value: float) -> None:
        super().__init__(name, min_value, max_value)

    def get_normalized(self, val: float, **kwargs) -> Union[float, List[float]]:
        """
        calculates a normalized value of the minute of the event as an offset from period start.
        :param val: a value representing the minute of the event.
        :param kwargs['event']: the pass event from which the minute is parsed
        :return: the normalized value of the event minute
        """
        period = int(kwargs["event"]["period"])
        if period <= 2:
            val = val - (45 * (period - 1))
        elif period <= 4:
            val = val - 90 - ((period - 3) * 15)
        elif period == 5:
            val = self.max_value
        return [super().get_normalized(val)]


class PassRecipientFeatureParser(FeatureParser):
    def __init__(self, name: str):
        super().__init__(name)

    def get_normalized(self, val, **kwargs) -> List[float]:
        """
        calculates a normalized value of the position of the player, identified by the id
        :param val: a value representing the player id in the json file
        :param kwargs['match_parser']: a MatchEventParser instance of the current match
        :param kwargs['event']: the pass event from which the recipient is parsed
        :return: the normalized value of the position of the player
        """
        # if val is 0, 'recipient' doesn't exist on 'pass' dict, pass is incomplete
        if val == 0:
            return [0]
        match_parser = kwargs["match_parser"]
        team_id = kwargs["event"]["team"]["id"]
        # positions in the teams_and_players mapping are normalized
        return [match_parser.teams_and_players[team_id][val]]


class FreezeFrameFeaturesParser(FeatureParser):
    def __init__(self, name: str, num_of_players):
        super().__init__(name)
        self.num_of_players = num_of_players
        self.x_loc_parser = RangeFeatureParser("x location parser", 0, 120)
        self.y_loc_parser = RangeFeatureParser("Y location parser", 0, 80)
        self.is_teammate_parser = CategoricalFeatureParser("is_teammate", [0, 1])

    def get_normalized(self, val: List[dict], **kwargs) -> List[float]:
        """
        returns a list of length 4 * num_of_players, containing the normalized values for player position, x location,
        y location, and is teammate for every player in the top num_of_players
        :param val: the freeze_frame object from the shot event
        :param kwargs['match_parser']: a MatchEventParser instance of the current match
        :param kwargs['event']: the event from which the freeze_frame on the shot event is parsed
        :return:
        """
        if type(val) is not list or len(val) == 0:
            return [0 for i in range(4 * self.num_of_players)]

        match_parser = kwargs["match_parser"]
        event = kwargs["event"]
        team_id = event["team"]["id"]
        teams_and_players = match_parser.teams_and_players
        opponent_team_id = next(num for num in teams_and_players.keys() if num != team_id)
        features = []

        num_of_players = min(self.num_of_players, len(val))
        for player_obj in val[:num_of_players]:
            is_teammate = player_obj["teammate"]
            player_id = player_obj["player"]["id"]
            # player position is normalized on players_and_positions dict
            player_pos = teams_and_players[team_id if is_teammate else opponent_team_id][player_id]
            x_loc = self.x_loc_parser.get_normalized(player_obj["location"][0])
            y_loc = self.y_loc_parser.get_normalized(player_obj["location"][1])
            features.extend([player_pos, x_loc, y_loc, self.is_teammate_parser.get_normalized(is_teammate)])

        # filling the list with trailing 0s to match the length of num_of_players * 4 to match range length
        features += [0] * ((4 * self.num_of_players) - len(features))
        return features

