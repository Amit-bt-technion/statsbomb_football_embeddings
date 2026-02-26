import unittest
from parameterized import parameterized

from tokenizer import event_ids
from tokenizer.event_parser import EventParser
from tokenizer.feature_parsers import (
    CategoricalFeatureParser,
    RangeFeatureParser,
    MinuteFeatureParser,
    PlayerPositionFeatureParser,
    FreezeFrameFeaturesParser,
    UnifiedTimeParser,
    ZeroFeatureParser,
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
            self.assertEqual(parser.get_normalized(elem), expected[i])

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
        self.assertEqual(parser.get_normalized(test_val), expected)

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
        self.assertEqual(parser.get_normalized(val, event=event), [expected])

    # ---- UnifiedTimeParser tests ----

    @parameterized.expand([
        # (period, minute, second, expected_normalised)
        # Formula: total_seconds = minute * 60 + second; norm = total / 9059
        # Period is passed as `val` but ignored by the parser.
        #
        # Period 1: total = 15*60+30 = 930, norm = 930/9059
        (1, 15, 30, 930 / 9059),
        # Period 1: total = 0
        (1, 0, 0, 0.0),
        # Period 1 stoppage: total = 47*60+59 = 2879
        (1, 47, 59, 2879 / 9059),
        # Period 2: total = 60*60+0 = 3600
        (2, 60, 0, 3600 / 9059),
        # Period 2: total = 75*60+30 = 4530
        (2, 75, 30, 4530 / 9059),
        # Period 3 (extra time): total = 100*60+0 = 6000
        (3, 100, 0, 6000 / 9059),
        # Period 4 (extra time 2): total = 115*60+30 = 6930
        (4, 115, 30, 6930 / 9059),
        # Period 5 (penalties): total = 120*60+0 = 7200
        (5, 120, 0, 7200 / 9059),
    ])
    def test_unified_time_parser(self, period, minute, second, expected):
        parser = UnifiedTimeParser("test unified time")
        event = {"period": period, "minute": minute, "second": second}
        result = parser.get_normalized(period, event=event)
        self.assertAlmostEqual(result, expected, places=6)

    def test_unified_time_parser_clamps_to_max(self):
        """Values beyond MAX_MATCH_SECONDS should be clamped to 1.0."""
        parser = UnifiedTimeParser("test unified time")
        # Extreme values that would exceed the max
        event = {"period": 5, "minute": 200, "second": 59}
        result = parser.get_normalized(5, event=event)
        self.assertLessEqual(result, 1.0)

    # ---- ZeroFeatureParser tests ----

    def test_zero_feature_parser_returns_zero(self):
        parser = ZeroFeatureParser("test zeroed")
        self.assertEqual(parser.get_normalized(42), 0)
        self.assertEqual(parser.get_normalized(0), 0)
        self.assertEqual(parser.get_normalized(999), 0)

    def test_zero_feature_parser_as_list(self):
        parser = ZeroFeatureParser("test zeroed list", as_list=True)
        self.assertEqual(parser.get_normalized(42), [0])
        self.assertEqual(parser.get_normalized(0), [0])

    @parameterized.expand([
        (903, {1827: {905: 0.833, 902: 1, 903: 0.2, 901: 0.15}},    {"team": {"id": 1827}}, 0.2),
        (22,  {1: {22: 0.833, 23: 1}, 2: {22: 0.1, 23: 0.5}},       {"team": {"id": 2}},    0.1),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 2}},    None),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   None),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   None),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   None),
        (4,   {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},       {"team": {"id": 40}},   None),
    ])
    def test_pass_recipient_feature_parser(self, player_id, teams_and_players, event, expected):
        parser = PlayerPositionFeatureParser("test parser")
        event_parser = EventParser(1)
        event_parser.teams_and_players = teams_and_players
        if expected is None:
            with self.assertRaises(KeyError):
                parser.get_normalized(player_id, event_parser=event_parser, event=event), [expected]
        else:
            self.assertEqual(parser.get_normalized(player_id, event_parser=event_parser, event=event), [expected])

    @parameterized.expand([
        ([{"player": {"id": 3}, "teammate": False, "location": [30, 60]}],
         {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},
         {"team": {"id": 40}},
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.25, 0.75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ([{"player": {"id": 1}, "teammate": True, "location": [60, 10]}],
         {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},
         {"team": {"id": 40}},
         [0.5, 0.125, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ([{"player": {"id": 2}, "teammate": False, "location": [150, -30]}],
         {40: {1: 0.07, 2: 0.82}, 50: {1: 0.992, 2: 0}},
         {"team": {"id": 50}},
         [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ([{"player": {"id": 3}, "teammate": False, "location": [120, 80]}],
         {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},
         {"team": {"id": 50}},
         None),
        ([{"player": {"id": 3}, "teammate": False, "location": [120, 80]}],
         {40: {1: 0.07, 2: 0.82}, 50: {3: 0.992, 4: 0}},
         {"team": {"id": 10}},
         None),
    ])
    def test_freeze_frame_features_parser(self, freeze_frame, teams_and_players, event, expected):
        parser = FreezeFrameFeaturesParser("test parser", 22)
        events_parser = EventParser(1)
        events_parser.teams_and_players = teams_and_players
        if expected is None:
            with self.assertRaises(ValueError):
                parser.get_normalized(freeze_frame, event_parser=events_parser, event=event)
        else:
            self.assertEqual(parser.get_normalized(freeze_frame, event_parser=events_parser, event=event), expected)
        
