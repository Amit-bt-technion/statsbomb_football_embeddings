import unittest
from parameterized import parameterized
from tokenizer import vector_size, event_types_mapping, event_ids
from tokenizer.feature_parsers import CategoricalFeatureParser
from tokenizer.match_parser import MatchEventsParser

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

    """dispossessed, duel, camera_on, block, offside, clearance, interception, dribble, shot, pressure, half_start, 
    substitution, own_goal, foul_won, foul_committed, goal_keeper, bad_behavior, own_goal_for, player_on, player_off, 
    shield, pass, 50_50, half_end, starting_xi, tactical_shift, error, miscontrol, dribbled_past, injury_stoppage, 
    referee_ball_drop, ball_receipt, carry,"""
    @parameterized.expand([
        (0, "ball_recovery", {"offensive": True, "recovery_failure": False}, [1, 0.5]),
        (1, "ball_recovery", {"offensive": True, "recovery_failure": False}, [1, 0.5]),
    ])
    def test_event_parser_features(self, set_index, event_name, event_specific_dict, expected):
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

