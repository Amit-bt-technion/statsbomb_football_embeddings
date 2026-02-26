from abc import ABC, abstractmethod
from typing import List, Any, Union


class FeatureParser(ABC):
    """
    This base class defines the interface with which parsers of features from the json files are used.
    """
    def __init__(self, name: str):
        self.feature_name = name

    # TODO: implement and override as necessary
    @abstractmethod
    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        pass

    def __repr__(self):
        return f"{self.feature_name} parser"


class RangeFeatureParser(FeatureParser):
    def __init__(self, name: str, min_value: float, max_value: float) -> None:
        super().__init__(name)
        self.min_value = min_value
        self.max_value = max_value

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        Calculates a normalized value of the parameter using continuous min-max scaling in range [0,1].
        :param val: The value to be normalized.
        :return: The normalized value in range [0,1].
        """
        val = min(val, self.max_value)
        val = max(val, self.min_value)
        return (val - self.min_value) / (self.max_value - self.min_value)


class CategoricalFeatureParser(FeatureParser):
    def __init__(self, name: str, categories: List[Any]):
        super().__init__(name)
        self.categories = {value: index + 1 for index, value in enumerate(sorted(categories))}
        self.num_categories = len(categories)

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        Calculates a normalized value of the parameter using discrete segmentation of range (0, 1].
        :param val: The value to be normalized.
        :return: The value in range (0, 1] that represents the category of the parameter.
        """
        return self.categories.get(val, 0) / self.num_categories


class TeamIdParser(CategoricalFeatureParser):
    def __init__(self, name: str) -> None:
        super().__init__(name, [])

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        provides binary classification for team ids, that remains constant throughout the match
        :param val: a value representing the id of the team.
        :param kwargs['event_parser']: a MatchEventParser instance of the current match with an initialized
        teams_and_players property
        :return: a category for the team id.
        """
        super().__init__(self.feature_name, kwargs["event_parser"].teams_and_players.keys())
        return [super().get_normalized(val)]


class MinuteFeatureParser(RangeFeatureParser):
    def __init__(self, name: str, min_value: float, max_value: float) -> None:
        super().__init__(name, min_value, max_value)

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
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


class PlayerPositionFeatureParser(FeatureParser):
    def __init__(self, name: str):
        super().__init__(name)

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        calculates a normalized value of the position of the player, identified by the id
        :param val: a value representing the player id in the json file
        :param kwargs['event_parser']: a MatchEventParser instance of the current match
        :param kwargs['event']: the pass event from which the recipient is parsed
        :return: the normalized value of the position of the player
        """
        # if val is 0, 'recipient' doesn't exist on 'pass' dict, pass is incomplete
        if val == 0:
            return [0]
        event_parser = kwargs["event_parser"]
        team_id = kwargs["event"]["team"]["id"]
        # positions in the teams_and_players mapping are normalized
        return [event_parser.teams_and_players[team_id][val]]


class FreezeFrameFeaturesParser(FeatureParser):
    def __init__(self, name: str, num_of_players):
        super().__init__(name)
        self.num_of_players = num_of_players
        self.x_loc_parser = RangeFeatureParser("x location parser", 0, 120)
        self.y_loc_parser = RangeFeatureParser("Y location parser", 0, 80)
        self.is_teammate_parser = CategoricalFeatureParser("is_teammate", [0, 1])

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        returns a list of length 2 * num_of_players, containing the normalized values for player position, x location,
        y location, and is teammate for every player in the top num_of_players
        :param val: the freeze_frame object from the shot event
        :param kwargs['event_parser']: a MatchEventParser instance of the current match
        :param kwargs['event']: the event from which the freeze_frame on the shot event is parsed
        :return:
        """
        features = [0 for _ in range(2 * self.num_of_players)]
        if type(val) is not list or len(val) == 0:
            return features

        event_parser = kwargs["event_parser"]
        event = kwargs["event"]
        team_id = event["team"]["id"]
        teams_and_players = event_parser.teams_and_players
        opponent_team_id = next(num for num in teams_and_players.keys() if num != team_id)

        num_of_players = min(self.num_of_players, len(val))
        for player_obj in val[:num_of_players]:
            is_teammate = player_obj["teammate"]
            player_id = player_obj["player"]["id"]
            team = team_id if is_teammate else opponent_team_id
            team_index = list(teams_and_players).index(team)
            player_index = list(teams_and_players[team]).index(player_id)

            x_loc = self.x_loc_parser.get_normalized(player_obj["location"][0])
            y_loc = self.y_loc_parser.get_normalized(player_obj["location"][1])
            features_index_start = (team_index * 2 * 11) + (2 * player_index)
            features[features_index_start: features_index_start + 2] = [x_loc, y_loc]

        return features


class DoNothingParser(FeatureParser):
    def __init__(self, name: str):
        super().__init__(name)

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        Returns the value as-is.
        :param val: The value to be returned.
        :return: The original value.
        """
        return val


class ZeroFeatureParser(FeatureParser):
    """
    Parser that always returns zero. Used to nullify deprecated feature slots
    while preserving the vector layout.
    """
    def __init__(self, name: str, as_list: bool = False):
        super().__init__(name)
        self.as_list = as_list

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        Always returns 0 (or [0] when as_list=True for special parser context).
        :param val: Ignored.
        :return: 0 or [0].
        """
        return [0] if self.as_list else 0


class UnifiedTimeParser(FeatureParser):
    """
    Computes a single normalized total-match-seconds value from the event's
    minute and second fields.

    Placed at the "period" key in feature_parsers (vector index 8) to replace
    the three separate time features (period, second, minute) with one unified
    time representation.

    The StatsBomb ``minute`` field is absolute match time (resets to 45 at
    half-time, 90 at the start of extra time, etc.), so the formula is simply:

        total_seconds = minute * 60 + second

    Denormalization is: ``total_seconds = normalized * MAX_MATCH_SECONDS``.

    Upper-bound derivation (generous ceiling covering extra time + penalties):
        - Max minute:          150
        - Max second:          59
        - MAX_MATCH_SECONDS:   150 * 60 + 59 = 9059 s
    """

    MAX_MATCH_SECONDS = 9059

    def __init__(self, name: str):
        super().__init__(name)

    def get_normalized(self, val: Union[float, List[dict]], **kwargs) -> Union[float, List[float]]:
        """
        Computes total seconds since match start, normalized to [0, 1].

        The period value is received as ``val`` (extracted from the event's
        "period" key) but is **not used** in the calculation.  Minute and
        second are read from ``kwargs["event"]``.

        :param val: The period value (ignored).
        :param kwargs: Must contain ``event`` — the full event dictionary.
        :return: Normalized total seconds in [0, 1].
        """
        event = kwargs.get("event", {})
        minute = int(event.get("minute", 0))
        second = int(event.get("second", 0))

        total_seconds = minute * 60 + second
        total_seconds = max(0, min(total_seconds, self.MAX_MATCH_SECONDS))

        return total_seconds / self.MAX_MATCH_SECONDS
