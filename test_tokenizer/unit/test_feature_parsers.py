import unittest
from parameterized import parameterized
from tokenizer.match_parser import MatchEventsParser
from tokenizer.feature_parsers import (
    CategoricalFeatureParser,
    RangeFeatureParser,
    MinuteFeatureParser,
    PassRecipientFeatureParser,
    FreezeFrameFeaturesParser
)


class TestTokenizer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @parameterized.expand([
        ([0, 1], [0.5, 1]),
        ([12, 58], [0.5, 1]),
        ([809, 58], [1, 0.5]),
        ([41, 1, 2, 100], [0.75, 0.25, 0.5, 1]),
    ])
    def test_categorical_feature_parser(self, categories, expected):
        parser = CategoricalFeatureParser("test parser", categories)
        for i, elem in enumerate(categories):
            self.assertEquals(parser.get_normalized(elem), expected[i])

    @parameterized.expand([
        (0, 2, 1, 0.5),
        (100, 200, 100, 0),
        (60, 80, 75, 0.75),
        (1, 2, 3, 1),
        (-3, 3, 0, 0.5),
        (-2, 2, -3, 0),
        (0, 120, 48, 0.4)
    ])
    def test_range_feature_parser(self, min_val, max_val, test_val, expected):
        parser = RangeFeatureParser("test parser", min_val, max_val)
        self.assertEquals(parser.get_normalized(test_val), expected)

    @parameterized.expand([
        (15, {"period": 1}, 0.25),
        (60, {"period": 2}, 0.25),
        (105, {"period": 3}, 0.25),
        (120, {"period": 4}, 0.25),
        (24, {"period": 1}, 0.4),
        (69, {"period": 2}, 0.4),
        (114, {"period": 3}, 0.4),
        (129, {"period": 4}, 0.4),
        (45, {"period": 1}, 0.75),
        (90, {"period": 2}, 0.75),
        (105, {"period": 3}, 0.25),
        (120, {"period": 4}, 0.25),
        (60, {"period": 1}, 1),
        (75, {"period": 1}, 1),
        (60, {"period": 2}, 0.25),
        (75, {"period": 2}, 0.5),
    ])
    def test_minute_feature_parser(self, val, event, expected):
        # on the actual parser the top of the range is 60 inclusive, simplified here for easy calculations
        parser = MinuteFeatureParser("test parser", 0, 60)
        self.assertEquals(parser.get_normalized(val, event=event), [expected])

    @parameterized.expand([
        (903, {1827: {905: 0.833, 902: 1, 903: 0.2, 901: 0.15}},    {"team": {"id": 1827}}, 0.2),
        (22,  {1: {22: 0.833, 23: 1}, 2: {22: 0.1, 23: 0.5}},       {"team": {"id": 2}},    0.1),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 2}},    -1),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   -1),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   -1),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   -1),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   -1),
    ])
    def test_pass_recipient_feature_parser(self, player_id, teams_and_players, event, expected):
        parser = PassRecipientFeatureParser("test parser")
        match_parser = MatchEventsParser(1)
        match_parser.teams_and_players = teams_and_players
        if expected == -1:
            with self.assertRaises(KeyError):
                self.assertEquals(parser.get_normalized(player_id, match_parser=match_parser, event=event), [expected])
        else:
            self.assertEquals(parser.get_normalized(player_id, match_parser=match_parser, event=event), [expected])

    def test_freeze_frame_features_parser(self):
        pass
