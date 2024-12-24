import unittest
from parameterized import parameterized
from tokenizer import vector_size, event_types_mapping, event_ids
from tokenizer.feature_parsers import CategoricalFeatureParser
from tokenizer.match_parser import MatchEventsParser
from test_tokenizer.integration import (
    shot_event_1, shot_event_2, shot_event_3, shot_event_4,
    expected_shot_event_1, expected_shot_event_2, expected_shot_event_3, expected_shot_event_4
)

event_id_parser = CategoricalFeatureParser("event type", event_ids.values())
parser = MatchEventsParser(vector_size)


class TestEventParsers(unittest.TestCase):
    def setUp(self) -> None:
        parser.teams_and_players = {
            222: {
                24: 1,
                25: 0.92,
                28: 0.36,
            },
            333: {
                31: 0.28,
                32: 0.56,
                39: 0.6
            }
        }

        common_values_set_1 = {
            "type": {"id": -1},
            "play_pattern": {"id": 3},
            "location": [90, 20],
            "duration": 2.25,
            "under_pressure": False,
            "out": False,
            "counterpress": True,
            "period": 2,
            "second": 11,
            "position": {"id": 13}, # is this value on purpose? no such position ID
            "minute": 75,
            "team": {"id": 333},
            "possession_team": {"id": 222},
            "player": {"id": 32},
        }
        expected_common_set_1 = [None, 1/3, 0.75, 0.25, 0.75, 0.5, 0.5, 1, 0.4, 0.2, 0.52, 0.5, 1, 0.5, 0.56]

        common_values_set_2 = {
            "type": {"id": -1},
            "play_pattern": {"id": 6},
            "location": [96, 56],
            "duration": 1.125,
            "under_pressure": True,
            "out": True,
            "counterpress": False,
            "period": 4,
            "second": 50,
            "position": {"id": 21}, # is this value on purpose? no such position ID
            "minute": 117,
            "team": {"id": 333},
            "possession_team": {"id": 333},
            "player": {"id": 31},
        }
        expected_common_set_2 = [None, 2/3, 0.8, 0.7, 0.375, 1, 1, 0.5, 0.8, 0.85, 0.84, 0.2, 1, 1, 0.28]

        # allowing iteration over all sets in all tests with minimal effort for adding new sets
        self.common_values_sets = [common_values_set_1, common_values_set_2]
        self.common_values_expected = [expected_common_set_1, expected_common_set_2]

    """shot,  
    bad_behavior, own_goal_for, player_on, player_off, 
    shield, pass, 50_50, half_end, starting_xi, tactical_shift, error, miscontrol, dribbled_past, injury_stoppage, 
    referee_ball_drop, ball_receipt, carry,"""
    @parameterized.expand([
        # Ball recovery
        (0, "ball_recovery", {"offensive": True, "recovery_failure": True}, [1, 1]),
        (1, "ball_recovery", {"offensive": True, "recovery_failure": False}, [1, 0.5]),
        (1, "ball_recovery", {"offensive": True}, [1, 0.5]),
        (0, "ball_recovery", {}, [0.5, 0.5]),

        # dispossessed
        (0, "dispossessed", {}, []),
        (1, "dispossessed", {}, []),

        # duel
        (0, "duel", {"type": {"id": 10}, "outcome": {"id": 1}}, [0.5, 1/7]),  # Aerial Lost + Lost
        (1, "duel", {"type": {"id": 10}, "outcome": {"id": 4}}, [0.5, 2/7]),  # Aerial Lost + Won
        (0, "duel", {"type": {"id": 11}, "outcome": {"id": 13}}, [1, 3/7]),  # Tackle + Lost In Play
        (0, "duel", {"type": {"id": 11}, "outcome": {"id": 14}}, [1, 4/7]),  # Tackle + Lost Out
        (1, "duel", {"type": {"id": 10}, "outcome": {"id": 15}}, [0.5, 5/7]),  # Aerial Lost + Success
        (1, "duel", {"type": {"id": 11}, "outcome": {"id": 16}}, [1, 6/7]),  # Tackle + Success In Play
        (1, "duel", {"type": {"id": 11}, "outcome": {"id": 17}}, [1, 1]),  # Tackle + Success Out

        # camera_on - commented out bc it's an ignored event
        # (0, "camera_on", {}, []),
        # (1, "camera_on", {}, []),

        # Block events - (team, event_type, event_data, expected_output)
        (0, "block", {"deflection": True}, [1, 0.5, 0.5]), # Team 0, deflection only
        (1, "block", {"offensive": True}, [0.5, 1, 0.5]), # Team 1, offensive only
        (0, "block", {"save_block": True}, [0.5, 0.5, 1]), # Team 0, save block only
        (1, "block", {"deflection": True, "offensive": True}, [1, 1, 0.5]), # Team 1, deflection + offensive
        (0, "block", {"deflection": True, "save_block": True}, [1, 0.5, 1]), # Team 0, deflection + save block
        (1, "block", {"offensive": True, "save_block": True}, [0.5, 1, 1]), # Team 1, offensive + save block
        (0, "block", {"deflection": True, "offensive": True, "save_block": True}, [1, 1, 1]),  # Team 0, all true
        (1, "block", {}, [0.5, 0.5, 0.5]), # Team 1, all false

        # offside
        (0, "offside", {}, []),
        (1, "offside", {}, []),

        # Clearance events - (team, event_type, event_data, expected_output)
        (0, "clearance", {"aerial_won": True, "body_part": {"id": 37}}, [1, 0.25]),  # Team 0, aerial won + head
        (1, "clearance", {"body_part": {"id": 38}}, [0.5, 0.5]),  # Team 1, no aerial + left foot
        (0, "clearance", {"aerial_won": True, "body_part": {"id": 40}}, [1, 0.75]),  # Team 0, aerial won + right foot
        (1, "clearance", {"body_part": {"id": 70}}, [0.5, 1.0]),  # Team 1, no aerial + other
        (0, "clearance", {"aerial_won": True, "body_part": {"id": 70}}, [1, 1.0]),  # Team 0, aerial won + other
        (1, "clearance", {"body_part": {"id": 37}}, [0.5, 0.25]),  # Team 1, no aerial + head

        # Interception events - (team, event_type, event_data, expected_output)
        (0, "interception", {"outcome": {"id": 1}}, [1 / 7]),  # Team 0, Lost
        (1, "interception", {"outcome": {"id": 4}}, [2 / 7]),  # Team 1, Won
        (0, "interception", {"outcome": {"id": 13}}, [3 / 7]),  # Team 0, Lost In Play
        (1, "interception", {"outcome": {"id": 14}}, [4 / 7]),  # Team 1, Lost Out
        (0, "interception", {"outcome": {"id": 15}}, [5 / 7]),  # Team 0, Success
        (1, "interception", {"outcome": {"id": 16}}, [6 / 7]),  # Team 1, Success In Play
        (0, "interception", {"outcome": {"id": 17}}, [7 / 7]),  # Team 0, Success Out

        # Dribble events - (team, event_type, event_data, expected_output)
        (0, "dribble", {"overrun": True, "outcome": {"id": 8},}, [1, 0.5, 1 / 2, 0.5]),  # Team 0
        (1, "dribble", {"nutmeg": True, "outcome": {"id": 9}}, [0.5, 1, 1, 0.5]), # Team 1
        (0, "dribble", {"overrun": True, "nutmeg": True, "outcome": {"id": 8}, "no_touch": True}, [1, 1, 1 / 2, 1]), # Team 0
        (1, "dribble", {"outcome": {"id": 9}, "no_touch": True}, [0.5, 0.5, 1, 1]), # Team 1
        (0, "dribble", {"outcome": {"id": 8}}, [0.5, 0.5, 1 / 2, 0.5]),  # Team 0
        (1, "dribble", {"overrun": True, "nutmeg": True, "outcome": {"id": 9}, "no_touch": True}, [1, 1, 1, 1]), # Team 1, all maximums
        (0, "dribble", {"outcome": {"id": 8}}, [0.5, 0.5, 1 / 2, 0.5]),  # Team 0, all minimums

        # pressure
        (0, "pressure", {}, []),
        (1, "pressure", {}, []),

        # Substitution events - (team, event_type, event_data, expected_output)
        (0, "substitution", {"outcome": {"id": 102}, "replacement": {"id": 512}}, [1 / 2]),  # Team 0, Injury substitution
        (1, "substitution", {"outcome": {"id": 103}, "replacement": {"id": 512}}, [1]),  # Team 1, Tactical substitution
        (0, "substitution", {"outcome": {"id": 102}, "replacement": {"id": 512}}, [1 / 2]),  # Team 0, Injury substitution
        (1, "substitution", {"outcome": {"id": 103}, "replacement": {"id": 512}}, [1]),  # Team 1, Tactical substitution

        # own_goal
        (0, "own_goal", {}, []),
        (1, "own_goal", {}, []),

        # Foul Won events - (team, event_type, event_data, expected_output)
        (0, "foul_won", {"defensive": True}, [1, 0.5, 0.5]), # Team 0, defensive only
        (1, "foul_won", {"advantage": True}, [0.5, 1, 0.5]), # Team 1, advantage only
        (0, "foul_won", {"penalty": True}, [0.5, 0.5, 1]), # Team 0, penalty only
        (1, "foul_won", {"defensive": True, "advantage": True}, [1, 1, 0.5]), # Team 1, defensive + advantage
        (0, "foul_won", {"defensive": True, "penalty": True}, [1, 0.5, 1]), # Team 0, defensive + penalty
        (1, "foul_won", {"advantage": True, "penalty": True}, [0.5, 1, 1]), # Team 1, advantage + penalty
        (0, "foul_won", {"defensive": True, "advantage": True, "penalty": True}, [1, 1, 1]),  # Team 0, all true
        (1, "foul_won", {}, [0.5, 0.5, 0.5]), # Team 1, all false

        # Foul Committed events - (team, event_type, event_data, expected_output)
        # Single attribute cases
        (0, "foul_committed", {"type": {"id": 19}}, [1 / 6, 0.5, 0.5, 0.5, 0]),  # Team 0, only type specified
        (1, "foul_committed", {"offensive": True}, [0, 1, 0.5, 0.5, 0]),  # Team 1, only offensive specified
        (0, "foul_committed", {"advantage": True}, [0, 0.5, 1, 0.5, 0]),  # Team 0, only advantage specified
        (1, "foul_committed", {"penalty": True}, [0, 0.5, 0.5, 1, 0]),  # Team 1, only penalty specified
        (0, "foul_committed", {"card": {"id": 7}}, [0, 0.5, 0.5, 0.5, 1]),  # Team 0, only card specified
        # Two attributes combinations
        (1, "foul_committed", {"type": {"id": 21}, "offensive": True}, [3 / 6, 1, 0.5, 0.5, 0]),  # Team 1, type + offensive
        (0, "foul_committed", {"advantage": True, "penalty": True}, [0, 0.5, 1, 1, 0]),  # Team 0, advantage + penalty
        (1, "foul_committed", {"card": {"id": 5}}, [0, 0.5, 0.5, 0.5, 1 / 3]),  # Team 1, offensive + card
        # Three attributes combinations
        (0, "foul_committed", {"type": {"id": 23}, "offensive": True, "advantage": True}, [5 / 6, 1, 1, 0.5, 0]),  # Team 0, type + offensive + advantage
        (1, "foul_committed", {"advantage": True, "penalty": True, "card": {"id": 6}}, [0, 0.5, 1, 1, 2 / 3]),  # Team 1, advantage + penalty + card
        # Four attributes combinations
        (0, "foul_committed", {
            "type": {"id": 24},
            "offensive": True,
            "advantage": True,
            "penalty": True
        }, [6 / 6, 1, 1, 1, 0]),  # Team 0, all except card
        (1, "foul_committed", {
            "offensive": True,
            "advantage": True,
            "penalty": True,
            "card": {"id": 7}
        }, [0, 1, 1, 1, 1]),  # Team 1, all except type
        # Full combinations (all attributes)
        (0, "foul_committed", {
            "type": {"id": 22},
            "offensive": True,
            "advantage": True,
            "penalty": True,
            "card": {"id": 7}
        }, [4 / 6, 1, 1, 1, 1]),  # Team 0, all attributes specified
        (1, "foul_committed", {
            "type": {"id": 20},
            "card": {"id": 5}
        }, [2 / 6, 0.5, 0.5, 0.5, 1 / 3]),  # Team 1, all attributes specified (minimums)

        # Goalkeeper events - (team, event_type, event_data, expected_output)
        # Single attribute cases
        (0, "goalkeeper", {"type": {"id": 25}}, [1 / 14, 0, 0, 0, 0, 0, 0]),  # Team 0, only type specified
        (1, "goalkeeper", {"outcome": {"id": 47}}, [0, 7 / 18, 0, 0, 0, 0, 0]),  # Team 1, only outcome specified
        (0, "goalkeeper", {"position": {"id": 42}}, [0, 0, 1 / 3, 0, 0, 0, 0]),  # Team 0, only position specified
        # Two attributes combinations
        (1, "goalkeeper", {"type": {"id": 27}, "body_part": {"id": 35}}, [3 / 14, 0, 0, 0, 1 / 7, 0, 0]),  # Team 1, type + body part
        (0, "goalkeeper", {"position": {"id": 43}, "technique": {"id": 45}}, [0, 0, 2 / 3, 1 / 2, 0, 0, 0]),  # Team 0, position + technique
        # Three attributes combinations
        (1, "goalkeeper", {
            "type": {"id": 30},
            "outcome": {"id": 51},
            "body_part": {"id": 37},
            "end_location": [80, 80]
        }, [6 / 14, 11 / 18, 0, 0, 3 / 7, 2/3, 1]),  # Team 1, type + outcome + body part
        (0, "goalkeeper", {
            "outcome": {"id": 53},
            "position": {"id": 44},
            "technique": {"id": 46},
            "end_location": [0, 0]
        }, [0, 13 / 18, 3 / 3, 2 / 2, 0, 0, 0]),  # Team 0, outcome + position + technique
        # Four attributes combinations
        (1, "goalkeeper", {
            "type": {"id": 33},
            "outcome": {"id": 56},
            "position": {"id": 42},
            "technique": {"id": 45},
            "end_location": [12, 72]
        }, [9 / 14, 15 / 18, 1 / 3, 1 / 2, 0, 0.1, 0.9]),  # Team 1, all except body part
        (0, "goalkeeper", {
            "type": {"id": 109},
            "outcome": {"id": 117},
            "position": {"id": 43},
            "body_part": {"id": 40},
            "end_location": [24,  20]
        }, [11 / 14, 18 / 18, 2 / 3, 0, 6 / 7, 0.2, 0.25]),  # Team 0, all except technique
        # Full combinations
        (1, "goalkeeper", {
            "type": {"id": 114},
            "outcome": {"id": 59},
            "position": {"id": 44},
            "technique": {"id": 46},
            "body_part": {"id": 41},
            "end_location": [200,  200]
        }, [14 / 14, 17 / 18, 3 / 3, 2 / 2, 7 / 7, 1, 1]),  # Team 1, all attributes maximum values
        (0, "goalkeeper", {
            "type": {"id": 25},
            "outcome": {"id": 4},
            "position": {"id": 42},
            "technique": {"id": 45},
            "body_part": {"id": 35},
            "end_location": [-1,  0]
        }, [1 / 14, 1 / 18, 1 / 3, 1 / 2, 1 / 7, 0, 0]),  # Team 0, all attributes minimum values


        # shot event
        (0, "shot", shot_event_1, expected_shot_event_1),
        (1, "shot", shot_event_2, expected_shot_event_2),
        (0, "shot", shot_event_3, expected_shot_event_3),
        (1, "shot", shot_event_4, expected_shot_event_4),
    ])

    def test_event_parser_features(self, set_index, event_name, event_specific_dict, expected):
        # Foul Committed events - (index, event_type, event_data, expected_output)
        common_value_set = self.common_values_sets[set_index]
        expected_common = self.common_values_expected[set_index]
        event_type_id = event_ids[event_name]
        common_value_set["type"]["id"] = event_type_id
        expected_common[0] = event_id_parser.get_normalized(event_type_id)
        # grabbing the index ranges in the vector
        common_start_index = event_types_mapping["common"]["starting_index"]
        common_end_index = len(event_types_mapping["common"]["feature_parsers"]) + \
                           event_types_mapping["common"]["num_of_special_features"] + common_start_index
        specific_start_index = event_types_mapping[event_type_id]["starting_index"]
        specific_end_index = len(event_types_mapping[event_type_id]["feature_parsers"]) + \
                             event_types_mapping[event_type_id].get("num_of_special_features", 0) + specific_start_index

        common_value_set[event_name] = event_specific_dict
        vec = parser.parse_event(common_value_set)

        # validating common values and specific-event values, and all other vector values are 0
        for cell_index in range(vector_size):
            if common_start_index <= cell_index < common_end_index:
                self.assertEqual(vec[cell_index], expected_common[cell_index - common_start_index])
            elif specific_start_index <= cell_index < specific_end_index:
                self.assertEqual(vec[cell_index], expected[cell_index - specific_start_index])
            else:
                a = vec[cell_index]
                self.assertEqual(vec[cell_index], 0)


    @parameterized.expand([
        # substitution events - id 19
        (
                {1: {11: 0.08, 16: 0.56}, 2: {28: 0.76, 29: 0.92}},
                {'type': {'id': 19}, 'team': {'id': 2}, 'player': {'id': 29}, 'substitution': {'replacement': {'id': 21}}},
                {1: {11: 0.08, 16: 0.56}, 2: {28: 0.76, 21: 0.92}},
        ), (
                {1: {11: 0.08, 16: 0.56}, 2: {11: 0.08, 16: 0.56}},
                {'type': {'id': 19}, 'team': {'id': 1}, 'player': {'id': 11}, 'substitution': {'replacement': {'id': 40}}},
                {1: {40: 0.08, 16: 0.56}, 2: {11: 0.08, 16: 0.56}},
        ),(
                {1: {11: 0.08, 16: 0.56}, 2: {28: 0.76, 29: 0.92}},
                {'type': {'id': 19}, 'team': {'id': 2}, 'player': {'id': 29}, 'substitution': {'replacement': {'id': 29}}},
                {1: {11: 0.08, 16: 0.56}, 2: {28: 0.76}}, # expecting 29 to be removed from the field
        ),

        # starting_xi events - id 35
        (
                {},
                {'type': {'id': 35}, 'team': {'id': 2}, 'tactics': {'lineup': [
                     {'player': {'id': 22}, 'position': {'id': 25},},
                     {'player': {'id': 23}, 'position': {'id': 14},},
                 ]}},
                {2: {22: 1, 23: 0.56}}
        ), (
                {2: {22: 1, 23: 0.56}},
                {'type': {'id': 35}, 'team': {'id': 1}, 'tactics': {'lineup': [
                     {'player': {'id': 14}, 'position': {'id': 10},},
                     {'player': {'id': 15}, 'position': {'id': 20},},
                 ]}},
                {2: {22: 1, 23: 0.56}, 1: {14: 0.4, 15: 0.8}}
        ),

        # tactical shift event - id 36
        (
                {2: {22: 1, 23: 0.56}, 1: {14: 0.4, 15: 0.8}},
                {'type': {'id': 36}, 'team': {'id': 1}, 'tactics': {'lineup': [
                    {'player': {'id': 16}, 'position': {'id': 5}, },
                    {'player': {'id': 17}, 'position': {'id': 15}, },
                ]}},
                {2: {22: 1, 23: 0.56}, 1: {16: 0.2, 17: 0.6}}
        ), (
                {2: {22: 1, 23: 0.56}, 1: {14: 0.4, 15: 0.8}},
                {'type': {'id': 36}, 'team': {'id': 2}, 'tactics': {'lineup': [
                    {'player': {'id': 16}, 'position': {'id': 5}, },
                    {'player': {'id': 17}, 'position': {'id': 15}, },
                ]}},
                {2: {16: 0.2, 17: 0.6}, 1: {14: 0.4, 15: 0.8}}
        ),
    ])
    def test_teams_and_players(self, prev_lineup, event, expected_lineup):
        """
        tests correctness and consistency of MatchEventsParser.teams_and_players after lineup changes
        """
        parser.teams_and_players = prev_lineup
        for key, val in self.common_values_sets[0].items():
            if event.get(key, None) is None:
                event[key] = val

        parser.parse_event(event)
        self.assertEquals(expected_lineup, parser.teams_and_players)

