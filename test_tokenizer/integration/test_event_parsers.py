import unittest
from parameterized import parameterized
from tokenizer import vector_size, event_types_mapping, event_ids
from tokenizer.feature_parsers import CategoricalFeatureParser
from tokenizer.event_parser import EventParser

event_id_parser = CategoricalFeatureParser("event type", event_ids.values())
parser = EventParser(vector_size)


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
        (1, "goalkeeper", {"outcome": {"id": 47}}, [0, 8 / 19, 0, 0, 0, 0, 0]),  # Team 1, only outcome specified
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
        }, [6 / 14, 12 / 19, 0, 0, 3 / 7, 2/3, 1]),  # Team 1, type + outcome + body part
        (0, "goalkeeper", {
            "outcome": {"id": 53},
            "position": {"id": 44},
            "technique": {"id": 46},
            "end_location": [0, 0]
        }, [0, 14 / 19, 3 / 3, 2 / 2, 0, 0, 0]),  # Team 0, outcome + position + technique
        # Four attributes combinations
        (1, "goalkeeper", {
            "type": {"id": 33},
            "outcome": {"id": 56},
            "position": {"id": 42},
            "technique": {"id": 45},
            "end_location": [12, 72]
        }, [9 / 14, 16 / 19, 1 / 3, 1 / 2, 0, 0.1, 0.9]),  # Team 1, all except body part
        (0, "goalkeeper", {
            "type": {"id": 109},
            "outcome": {"id": 117},
            "position": {"id": 43},
            "body_part": {"id": 40},
            "end_location": [24,  20]
        }, [11 / 14, 19 / 19, 2 / 3, 0, 6 / 7, 0.2, 0.25]),  # Team 0, all except technique
        # Full combinations
        (1, "goalkeeper", {
            "type": {"id": 114},
            "outcome": {"id": 59},
            "position": {"id": 44},
            "technique": {"id": 46},
            "body_part": {"id": 41},
            "end_location": [200,  200]
        }, [14 / 14, 18 / 19, 3 / 3, 2 / 2, 7 / 7, 1, 1]),  # Team 1, all attributes maximum values
        (0, "goalkeeper", {
            "type": {"id": 25},
            "outcome": {"id": 4},
            "position": {"id": 42},
            "technique": {"id": 45},
            "body_part": {"id": 35},
            "end_location": [-1,  0]
        }, [1 / 14, 2 / 19, 1 / 3, 1 / 2, 1 / 7, 0, 0]),  # Team 0, all attributes minimum values

        # bad behavior event
        (0, "bad_behavior", {}, [0]),
        (1, "bad_behavior", {"card": {"id": 5}}, [1/3]),
        (0, "bad_behavior", {"card": {"id": 6}}, [2/3]),
        (1, "bad_behavior", {"card": {"id": 7}}, [3/3]),

        # own_goal_for
        (0, "own_goal_for", {}, []),
        (1, "own_goal_for", {}, []),

        # player_on
        (0, "player_on", {}, []),
        (1, "player_on", {}, []),

        # player_off
        (0, "player_on", {"permanent": True}, []),
        (1, "player_on", {}, []),

        # shield
        (0, "shield", {}, []),
        (1, "shield", {}, []),

        # 50-50
        (0, "50_50", {}, [0]),
        (1, "50_50", {"outcome": {"id": 1}}, [1/4]),
        (0, "50_50", {"outcome": {"id": 2}}, [2/4]),
        (1, "50_50", {"outcome": {"id": 3}}, [3/4]),
        (0, "50_50", {"outcome": {"id": 4}}, [4/4]),

        # error event
        (0, "error", {}, []),
        (1, "error", {}, []),

        # miscontrol
        (0, "miscontrol", {}, [0.5]),
        (1, "miscontrol", {"aerial_won": True}, [1]),

        # dribbled past
        (0, "dribbled_past", {}, []),
        (1, "dribbled_past", {}, []),

        # injury_stoppage
        (0, "dribbled_past", {}, [0.5]),
        (1, "dribbled_past", {"in_chain": True}, [1]),

        # referee_ball_drop
        (0, "referee_ball_drop", {}, []),
        (1, "referee_ball_drop", {}, []),

        # ball_receipt
        (0, "ball_receipt", {}, [0]),
        (1, "ball_receipt", {"outcome": {"id": 9}}, [1]),

        # carry
        (0, "carry", {"end_location": [80, 80]}, [80/120, 80/80]),
        (1, "carry", {"end_location": [-1, -1]}, [0, 0]),
        (0, "carry", {"end_location": [92, 17]}, [92 / 120, 17 / 80]),
        (0, "carry", {"end_location": [200, 200]}, [1, 1]),

        # Pass events - (team, event_type, event_data, expected_output)
        # Simple pass with minimal attributes
        (0, "pass", {
            "type": {"id": 61},  # Corner
            "length": 20,  # normalized: 20/120
            "end_location": [60, 40]  # normalized: 60/120, 40/80
        }, [1 / 7, 1 / 6, 0.5, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0]),
        # Complex pass with many attributes
        (1, "pass", {
            "type": {"id": 63},  # Goal Kick
            "length": 60,  # normalized: 60/120
            "angle": 1.57,  # normalized: (1.57 + 3.15)/(6.3)
            "height": {"id": 2},  # Low Pass
            "end_location": [100, 60],  # normalized: 100/120, 60/80
            "backheel": True,
            "cross": True,
            "body_part": {"id": 38},  # Left Foot
            "outcome": {"id": 75},  # Out
        }, [3 / 7, 0.5, (1.57 + 3.15)/6.3, 2 / 3, 100/120, 60/80, 1, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 2 / 7, 3 / 5, 0, 0]),
        # Complete pass with all attributes
        (0, "pass", {
            "type": {"id": 65},  # Kick Off
            "length": 90,  # normalized: 90/120
            "angle": -1.57,  # normalized: (-1.57 + 3.15)/(6.3)
            "height": {"id": 3},  # High Pass
            "end_location": [30, 20],  # normalized: 30/120, 20/80
            "backheel": True,
            "deflected": True,
            "miscommunication": True,
            "cross": True,
            "cut_back": True,
            "switch": True,
            "shot_assist": True,
            "goal_assist": True,
            "body_part": {"id": 40},  # Right Foot
            "outcome": {"id": 77},  # Unknown
            "technique": {"id": 108},  # Through Ball
        }, [5 / 7, 0.75, (-1.57 + 3.15)/6.3, 1, 0.25, 0.25, 1, 1, 1, 1, 1, 1, 1, 1, 3 / 7, 5 / 5, 4 / 4, 0]),
        # Pass with different combinations and some missing attributes
        (1, "pass", {
            "type": {"id": 67},  # Throw-in
            "length": 30,  # normalized: 30/120
            "angle": 3.14,  # normalized: (3.14 + 3.15)/(6.3)
            "height": {"id": 1},  # Ground Pass
            "end_location": [45, 35],  # normalized: 45/120, 35/80
            "technique": {"id": 104},  # Inswinging
            "backheel": False,
            "deflected": False
        }, [7 / 7, 0.25, (3.14 + 3.15)/6.3, 1 / 3, 0.375, 0.4375, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 1 / 4, 0]),
        # Pass with negative angle and different body part
        (0, "pass", {
            "type": {"id": 62},  # Free Kick
            "length": 100,  # normalized: 100/120
            "angle": -3.14,  # normalized: (-3.14 + 3.15)/(6.3)
            "body_part": {"id": 69},  # Keeper Arm
            "end_location": [80, 70],  # normalized: 80/120, 70/80
        }, [2 / 7, 100/120, (-3.14+3.15)/6.3, 0, 80/120, 70/80, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 5 / 7, 0, 0, 0]),
        # Minimal pass - just required fields
        (0, "pass", {
            "type": {"id": 61},  # Corner
            "length": 15,
            "end_location": [0, 0]  # Edge case - corner of pitch
        }, [1 / 7, 15 / 120, 0.5, 0, 0 / 120, 0 / 80, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0]),
        # Edge case - maximum values
        (1, "pass", {
            "type": {"id": 67},  # Throw-in
            "length": 120,  # Max length
            "angle": 3.15,  # Max angle
            "height": {"id": 3},  # High Pass
            "end_location": [120, 80],  # Far corner
            "cross": True,
            "switch": True,
            "body_part": {"id": 106},  # No Touch
            "outcome": {"id": 77},  # Unknown
        }, [7 / 7, 120 / 120, 1, 3 / 3, 120 / 120, 80 / 80, 0.5, 0.5, 0.5, 1, 0.5, 1, 0.5, 0.5, 7 / 7, 5 / 5, 0, 0]),
        # Edge case - minimum values and negative angle
        (0, "pass", {
            "type": {"id": 61},  # Corner
            "length": 1,  # Very short pass
            "angle": -3.15,  # Min angle
            "height": {"id": 1},  # Ground pass
            "end_location": [1, 1],  # Near corner
            "goal_assist": True,
        }, [1 / 7, 1 / 120, 0, 1 / 3, 1 / 120, 1 / 80, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 0, 0, 0, 0]),
        # Complete pass with all possible True booleans
        (1, "pass", {
            "type": {"id": 64},  # Interception
            "length": 45,
            "angle": 1.57,  # 90 degrees
            "height": {"id": 2},  # Low Pass
            "end_location": [60, 40],  # Middle of pitch
            "backheel": True,
            "deflected": True,
            "miscommunication": True,
            "cross": True,
            "cut_back": True,
            "switch": True,
            "shot_assist": True,
            "goal_assist": True,
            "body_part": {"id": 38},  # Left Foot
            "outcome": {"id": 74},  # Injury Clearance
            "technique": {"id": 105},  # Outswinging
        }, [4 / 7, 45 / 120, (1.57 + 3.15) / 6.3, 2 / 3, 60 / 120, 40 / 80, 1, 1, 1, 1, 1, 1, 1, 1, 2 / 7, 2 / 5, 2 / 4,
            0]),
        # Interesting angle case (0 - straight ahead)
        (0, "pass", {
            "type": {"id": 63},  # Goal Kick
            "length": 80,
            "angle": 0,  # Straight ahead
            "end_location": [100, 40],  # Deep in opposition half
            "height": {"id": 3},  # High Pass
            "shot_assist": True,
            "body_part": {"id": 68},  # Drop Kick
        },
         [3 / 7, 80 / 120, (0 + 3.15) / 6.3, 3 / 3, 100 / 120, 40 / 80, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 4 / 7, 0,
          0, 0]),
        # Pass with mostly missing data but some crucial True booleans
        (1, "pass", {
            "type": {"id": 62},  # Free Kick
            "length": 30,
            "end_location": [40, 60],
            "cross": True,
            "goal_assist": True
        }, [2 / 7, 30 / 120, 0.5, 0, 40 / 120, 60 / 80, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 1, 0, 0, 0, 0]),
        # Edge case - diagonal pass across whole pitch
        (0, "pass", {
            "type": {"id": 65},  # Kick Off
            "length": 120,  # Maximum length
            "angle": 0.785,  # 45 degrees
            "end_location": [120, 80],  # Far corner
            "height": {"id": 2},  # Low Pass
            "switch": True,
            "body_part": {"id": 40},  # Right Foot
            "technique": {"id": 108},  # Through Ball
        }, [5 / 7, 120 / 120, (0.785 + 3.15) / 6.3, 2 / 3, 120 / 120, 80 / 80, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5,
            3 / 7, 0, 4 / 4, 0]),

        # Shot events - (index, event_type, event_data, expected_output)
        # Minimal shot data
        (0, "shot", {
            "type": {"id": 87},  # Open Play
            "end_location": [120, 40, 0],  # Goal line, center, ground shot
            "statsbomb_xg": 0.05
        }, [3/4, 120/120, 40/80, 0/5, 0.5, 0.5, 0.5, 0.5, 0.05/1, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),

        # Maximum values edge case
        (1, "shot", {
            "type": {"id": 88},  # Penalty
            "end_location": [120, 80, 5],  # Top corner
            "aerial_won": True,
            "first_time": True,
            "open_goal": True,
            "statsbomb_xg": 0.96,
            "technique": {"id": 95},  # Volley
            "body_part": {"id": 37},  # Head
            "outcome": {"id": 97},  # Goal
        }, [4/4, 120/120, 80/80, 5/5, 1, 0.5, 1, 1, 0.96/1, 0.5, 7/7, 1/4, 2/8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),

        # Corner kick shot
        (0, "shot", {
            "type": {"id": 61},  # Corner
            "end_location": [115, 35, 2.5],
            "follows_dribble": True,
            "deflected": True,
            "statsbomb_xg": 0.12,
            "technique": {"id": 90},  # Diving Header
            "body_part": {"id": 37},  # Head
            "outcome": {"id": 96},  # Blocked
        }, [1/4, 115/120, 35/80, 2.5/5, 0.5, 1, 0.5, 0.5, 0.12/1, 1, 2/7, 1/4, 1/8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),

        # Free kick with minimal height
        (1, "shot", {
            "type": {"id": 62},  # Free Kick
            "end_location": [118, 40, 0.1],
            "first_time": True,
            "statsbomb_xg": 0.08,
            "body_part": {"id": 40},  # Right Foot
            "outcome": {"id": 100},  # Saved
        }, [2/4, 118/120, 40/80, 0.1/5, 0.5, 0.5, 1, 0.5, 0.08/1, 0.5, 0, 3/4, 5/8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),

        # Complex shot with multiple True booleans
        (0, "shot", {
            "type": {"id": 87},  # Open Play
            "end_location": [119, 42, 1.8],
            "aerial_won": True,
            "follows_dribble": True,
            "first_time": True,
            "open_goal": True,
            "statsbomb_xg": 0.76,
            "deflected": True,
            "technique": {"id": 94},  # Overhead Kick
            "body_part": {"id": 38},  # Left Foot
            "outcome": {"id": 99},  # Post
            "freeze_frame": [{
                "location": [91, 50],
                "player": {
                    "id": 31,
                    "name": "<NAME>",
                },
                "position": {
                    "id": 1,
                    "name": "<pos>"
                },
                "teammate": True
            }]
        }, [3/4, 119/120, 42/80, 1.8/5, 1, 1, 1, 1, 0.76/1, 1, 6/7, 2/4, 4/8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 91/120, 50/80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        # Edge case - wide shot
        (1, "shot", {
            "type": {"id": 87},  # Open Play
            "end_location": [120, 0, 3],  # Complete wide
            "statsbomb_xg": 0.02,
            "outcome": {"id": 101},  # Wayward
            "technique": {"id": 93},  # Normal
            "freeze_frame": [{
                "location": [120, 80],
                "player": {
                    "id": 24,
                    "name": "<NAME>",
                },
                "position": {
                    "id": 1,
                    "name": "<pos>"
                },
                "teammate": False
            }, {
                "location": [60, 40],
                "player": {
                    "id": 25,
                    "name": "<NAME>",
                },
                "position": {
                    "id": 1,
                    "name": "<pos>"
                },
                "teammate": False
            }, {
                "location": [13, 17],
                "player": {
                    "id": 28,
                    "name": "<NAME>",
                },
                "position": {
                    "id": 1,
                    "name": "<pos>"
                },
                "teammate": False
            }, {
                "location": [90, 20],
                "player": {
                    "id": 31,
                    "name": "<NAME>",
                },
                "position": {
                    "id": 1,
                    "name": "<pos>"
                },
                "teammate": True
            }, {
                "location": [88, 25],
                "player": {
                    "id": 32,
                    "name": "<NAME>",
                },
                "position": {
                    "id": 1,
                    "name": "<pos>"
                },
                "teammate": True
            }, {
                "location": [110, 30],
                "player": {
                    "id": 39,
                    "name": "<NAME>",
                },
                "position": {
                    "id": 1,
                    "name": "<pos>"
                },
                "teammate": True
            }]
        }, [3/4, 120/120, 0/80, 3/5, 0.5, 0.5, 0.5, 0.5, 0.02/1, 0.5, 5/7, 0, 6/8, 1, 1, 60/120, 40/80, 13/120, 17/80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 90/120, 20/80, 88/120, 25/80, 110/120, 30/80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
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
        self.assertEqual(expected_lineup, parser.teams_and_players)

