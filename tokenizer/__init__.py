import logging
from tokenizer.feature_parsers import (
    FeatureParser,
    CategoricalFeatureParser,
    RangeFeatureParser,
    TeamIdParser,
    MinuteFeatureParser,
    PlayerPositionFeatureParser,
    FreezeFrameFeaturesParser
)

logger = logging.getLogger(__name__)

# ************************************************************************************************************
#                                           Parsers Mapping
# ************************************************************************************************************
vector_size = 122
num_of_players_in_freeze_frame = 22
event_ids = {
    'ball_recovery': 2, 'dispossessed': 3, 'duel': 4, 'camera_on': 5, 'block': 6,
    'offside': 8, 'clearance': 9, 'interception': 10, 'dribble': 14, 'shot': 16,
    'pressure': 17, 'half_start': 18, 'substitution': 19, 'own_goal': 20, 'foul_won': 21,
    'foul_committed': 22, 'goal_keeper': 23, 'bad_behavior': 24, 'own_goal_for': 25,
    'player_on': 26, 'player_off': 27, 'shield': 28, 'pass': 30, '50_50': 33,
    'half_end': 34, 'starting_xi': 35, 'tactical_shift': 36, 'error': 37, 'miscontrol': 38,
    'dribbled_past': 39, 'injury_stoppage': 40, 'referee_ball_drop': 41, 'ball_receipt': 42, 'carry': 43
}


event_types_mapping = {
    # common features
    "common": {
        "ignore_event_type": False,
        "starting_index": 0,
        "feature_parsers": {
            "type.id": CategoricalFeatureParser("type", list(event_ids.values())),
            "play_pattern.id": CategoricalFeatureParser("play_pattern", [i for i in range(1, 10)]),
            "location[0]": RangeFeatureParser("x_location", min_value=0, max_value=120),
            "location[1]": RangeFeatureParser("y_location", min_value=0, max_value=80),
            "duration": RangeFeatureParser("duration", min_value=0, max_value=3),
            "under_pressure": CategoricalFeatureParser("under_pressure", [0, 1]),
            "out": CategoricalFeatureParser("out", [0, 1]),
            "counterpress": CategoricalFeatureParser("counterpress", [0, 1]),
            "period": CategoricalFeatureParser("period", [i for i in range(1, 6)]),
            "second": CategoricalFeatureParser("second", [i for i in range(0, 60)]),
            "position.id": CategoricalFeatureParser("position", [i for i in range(1,26)])
        },
        "special_parsers": {
            "minute": MinuteFeatureParser("minute", 0, 60),
            "team.id": TeamIdParser("team"),
            "possession_team.id": TeamIdParser("possession_team"),
            "player.id": PlayerPositionFeatureParser("player_designated_position"),
        },
        "num_of_special_features": 4

    },
    # ball recovery event
    2: {
        "ignore_event_type": False,
        "starting_index": 15,
        "feature_parsers": {
            "ball_recovery.offensive": CategoricalFeatureParser("offensive ball recovery", [0, 1]),
            "ball_recovery.recovery_failure": CategoricalFeatureParser("failed ball recovery", [0, 1]),
        }
    },
    # dispossessed event - no specific feature parsers
    3: {
        "ignore_event_type": False,
        "starting_index": 17,
        "feature_parsers": {}
    },
    # duel event
    4: {
        "ignore_event_type": False,
        "starting_index": 17,
        "feature_parsers": {
            "duel.type.id": CategoricalFeatureParser("duel type", [10, 11]),
            "duel.outcome.id": CategoricalFeatureParser("duel type", [1, 4, 13, 14, 15, 16, 17]),
        }
    },
    # camera on event
    5: {
        "ignore_event_type": True,
        "starting_index": 19,
        "feature_parsers": {}
    },
    # block event
    6: {
        "ignore_event_type": False,
        "starting_index": 19,
        "feature_parsers": {
            "block.deflection": CategoricalFeatureParser("block deflection", [0, 1]),
            "block.offensive": CategoricalFeatureParser("block offensive", [0, 1]),
            "block.save_block": CategoricalFeatureParser("block saved", [0, 1]),
        }
    },
    # offside event
    8: {
        "ignore_event_type": False,
        "starting_index": 22,
        "feature_parsers": {}
    },
    # clearance event
    9: {
        "ignore_event_type": False,
        "starting_index": 22,
        "feature_parsers": {
            "clearance.aerial_won": CategoricalFeatureParser("clearance aerial won", [0, 1]),
            "clearance.body_part.id": CategoricalFeatureParser("clearance body part", [37, 38, 40, 70]),
        }
    },
    # interception event
    10: {
        "ignore_event_type": False,
        "starting_index": 24,
        "feature_parsers": {
            "interception.outcome.id": CategoricalFeatureParser("interception outcome", [1, 4, 13, 14, 15, 16, 17]),
        }
    },
    # dribble event
    14: {
        "ignore_event_type": False,
        "starting_index": 25,
        "feature_parsers": {
            "dribble.overrun": CategoricalFeatureParser("dribble overrun", [0, 1]),
            "dribble.nutmeg": CategoricalFeatureParser("dribble nutmeg", [0, 1]),
            "dribble.outcome.id": CategoricalFeatureParser("dribble nutmeg", [8, 9]),
            "dribble.no_touch": CategoricalFeatureParser("dribble no toch", [0, 1]),
        }
    },
    # shot event - setting starting index to the end of the vector
    16: {
        "ignore_event_type": False,
        "starting_index": 69,
        "feature_parsers": {
            "shot.type.id": CategoricalFeatureParser("shot type", [61, 62, 87, 88]),
            "shot.end_location[0]": RangeFeatureParser("shot end location x", 0, 120),
            "shot.end_location[1]": RangeFeatureParser("shot end location y", 0, 80),
            # after exploration - setting maximum z shot height to 5 meters, the 90th percentile
            "shot.end_location[2]": RangeFeatureParser("shot end location z", 0, 10),
            "shot.aerial_won": CategoricalFeatureParser("shot aerial won", [0, 1]),
            "shot.follows_dribble": CategoricalFeatureParser("shot follows dribble", [0, 1]),
            "shot.first_time": CategoricalFeatureParser("shot first time", [0, 1]),
            "shot.open_goal": CategoricalFeatureParser("shot open goal", [0, 1]),
            "shot.statsbomb_xg": RangeFeatureParser("shot statsbomb xg", 0, 1),
            "shot.deflected": CategoricalFeatureParser("shot deflected", [0, 1]),
            "clearance.technique.id": CategoricalFeatureParser("shot technique", [i for i in range(89, 96)]),
            "clearance.body_part.id": CategoricalFeatureParser("shot body part", [37, 38, 40, 70]),
            "clearance.outcome.id": CategoricalFeatureParser("shot body part", [96, 97, 98, 99, 100, 101, 115, 116]),
        },
        "special_parsers": {
            "shot.freeze_frame": FreezeFrameFeaturesParser("freeze frame", num_of_players_in_freeze_frame),
        },
        "num_of_special_features": num_of_players_in_freeze_frame * 4
    },
    # pressure event
    17: {
        "ignore_event_type": False,
        "starting_index": 29,
        "feature_parsers": {}
    },
    # half start
    18: {
        "ignore_event_type": True,
        "starting_index": -1,
        "feature_parsers": {}
    },
    # substitution event
    19: {
        "ignore_event_type": False,
        "starting_index": 29,
        "feature_parsers": {
            # disregarding replacement as we are not addressing player identities and the player position is included in the common features
            "substitution.outcome.id": CategoricalFeatureParser("substitution outcome", [102, 103]),
        }
    },
    # own goal against event
    20: {
        "ignore_event_type": False,
        "starting_index": 30,
        "feature_parsers": {}
    },
    # foul won event
    21: {
        "ignore_event_type": False,
        "starting_index": 30,
        "feature_parsers": {
            "foul_won.defensive": CategoricalFeatureParser("foul won defensive", [0, 1]),
            "foul_won.advantage": CategoricalFeatureParser("foul won advantage", [0, 1]),
            "foul_won.penalty": CategoricalFeatureParser("foul won penalty", [0, 1]),
        }
    },
    # foul committed event
    22: {
        "ignore_event_type": False,
        "starting_index": 33,
        "feature_parsers": {
            "foul_committed.type.id": CategoricalFeatureParser("offensive foul committed", [i for i in range (19, 25)]),
            "foul_committed.offensive": CategoricalFeatureParser("offensive foul committed", [0, 1]),
            "foul_committed.advantage": CategoricalFeatureParser("foul committed advantage", [0, 1]),
            "foul_committed.penalty": CategoricalFeatureParser("foul committed penalty", [0, 1]),
            "foul_committed.card.id": CategoricalFeatureParser("foul committed penalty", [5, 6, 7]),
        }
    },
    # goal keeper event
    23: {
        "ignore_event_type": False,
        "starting_index": 38,
        "feature_parsers": {
            "goalkeeper.type.id": CategoricalFeatureParser("goalkeeper type", [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 109, 110, 113, 114]),
            "goalkeeper.outcome.id": CategoricalFeatureParser("goalkeeper outcome", [4, 13, 14, 16, 17, 47, 48, 49, 50, 51, 52, 53, 55, 56, 15, 58, 59, 117]),
            "goalkeeper.position.id": CategoricalFeatureParser("goalkeeper position", [42, 43, 44]),
            "goalkeeper.technique.id": CategoricalFeatureParser("goalkeeper position", [45, 46]),
            "goalkeeper.body_part.id": CategoricalFeatureParser("goalkeeper body part", [i for i in range(35, 42)]),
        }
    },
    # bad behavior event
    24: {
        "ignore_event_type": False,
        "starting_index": 43,
        "feature_parsers": {
            "bad_behavior.card.id": CategoricalFeatureParser("bad behavior card", [65, 66, 67]),
        }
    },
    # own goal for event
    25: {
        "ignore_event_type": False,
        "starting_index": 44,
        "feature_parsers": {}
    },
    # player on event
    26: {
        "ignore_event_type": False,
        "starting_index": 44,
        "feature_parsers": {}
    },
    # player off event
    27: {
        "ignore_event_type": False,
        "starting_index": 44,
        "feature_parsers": {
            "player_off.permanent": CategoricalFeatureParser("player off permanently", [0, 1]),
        }
    },
    # shield event
    28: {
        "ignore_event_type": False,
        "starting_index": 45,
        "feature_parsers": {}
    },
    # pass event
    30: {
        "ignore_event_type": False,
        "starting_index": 45,
        "feature_parsers": {
            "pass.type.id": CategoricalFeatureParser("pass type", [i for i in range(61, 68)]),
            "pass.length": RangeFeatureParser("pass length", 0, 120),
            "pass.angle": RangeFeatureParser("pass angle", -3.15, 3.15),
            "pass.height.id": CategoricalFeatureParser("pass height", [1, 2, 3]),
            "pass.end_location[0]": RangeFeatureParser("pass end location x", 0, 120),
            "pass.end_location[1]": RangeFeatureParser("pass end location y", 0, 80),
            "pass.backheel": CategoricalFeatureParser("pass backheel", [0, 1]),
            "pass.deflected": CategoricalFeatureParser("pass deflected", [0, 1]),
            "pass.miscommunication": CategoricalFeatureParser("pass miscommunication", [0, 1]),
            "pass.cross": CategoricalFeatureParser("pass cross", [0, 1]),
            "pass.cut_back": CategoricalFeatureParser("pass cut back", [0, 1]),
            "pass.switch": CategoricalFeatureParser("pass switch", [0, 1]),
            "pass.shot_assist": CategoricalFeatureParser("pass shot assist", [0, 1]),
            "pass.goal_assist": CategoricalFeatureParser("pass goal assist", [0, 1]),
            "pass.body_part.id": CategoricalFeatureParser("pass body part", [37, 38, 40, 68, 69, 70, 106]),
            "pass.outcome.id": CategoricalFeatureParser("pass outcome", [9, 74, 75, 76, 77]),
            "pass.technique.id": CategoricalFeatureParser("pass technique", [104, 105, 107, 108]),
        },
        "special_parsers": {
            "pass.recipient.id": PlayerPositionFeatureParser("player position"),
        },
        "num_of_special_features": 1
    },
    # 50-50 event
    33: {
        "ignore_event_type": False,
        "starting_index": 63,
        "feature_parsers": {
            "50_50.outcome.id": CategoricalFeatureParser("50/50 outcome", [108, 109, 147, 148])
        }
    },
    # half end event
    34: {
        "ignore_event_type": True,
        "starting_index": -1,
        "feature_parsers": {}
    },
    # starting xi event
    35: {
        "ignore_event_type": True,
        "starting_index": -1,
        "feature_parsers": {}
    },
    # tactical shift event
    36: {
        "ignore_event_type": True,
        "starting_index": -1,
        "feature_parsers": {}
    },
    # error event
    37: {
        "ignore_event_type": False,
        "starting_index": 64,
        "feature_parsers": {}
    },
    # miscontrol
    38: {
        "ignore_event_type": False,
        "starting_index": 64,
        "feature_parsers": {
            "miscontrol.aerial_won": CategoricalFeatureParser("aerial won", [0, 1]),
        }
    },
    # dribbled past event
    39: {
        "ignore_event_type": False,
        "starting_index": 65,
        "feature_parsers": {}
    },
    # injury stoppage
    40: {
        "ignore_event_type": False,
        "starting_index": 65,
        "feature_parsers": {
            "injury_stoppage.in_chain": CategoricalFeatureParser("injury stoppage", [0, 1]),
        }
    },
    # referee ball drop event
    41: {
        "ignore_event_type": False,
        "starting_index": 66,
        "feature_parsers": {}
    },
    # ball receipt event
    42: {
        "ignore_event_type": False,
        "starting_index": 66,
        "feature_parsers": {
            "ball_receipt.outcome.id": CategoricalFeatureParser("ball receipt outcome", [9])
        }
    },
    # carry event
    43: {
        "ignore_event_type": False,
        "starting_index": 67,
        "feature_parsers": {
            "carry.end_location[0]": RangeFeatureParser("carry end location x", 0, 120),
            "carry.end_location[1]": RangeFeatureParser("carry end location y", 0, 80),
        }
    },
}
