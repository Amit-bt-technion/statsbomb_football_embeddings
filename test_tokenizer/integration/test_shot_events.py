import unittest
from parameterized import parameterized
from tokenizer.event_parser import EventParser
from tokenizer import vector_size
from test_tokenizer.integration import (
    shot_event_1, shot_event_2, shot_event_3, shot_event_4,
    teams_and_players_1, teams_and_players_2, teams_and_players_3, teams_and_players_4,
    expected_shot_event_1, expected_shot_event_2, expected_shot_event_3, expected_shot_event_4
)

parser = EventParser(vector_size)


class TestShotEvents(unittest.TestCase):
    @parameterized.expand([
        (shot_event_1, teams_and_players_1, expected_shot_event_1),
        (shot_event_2, teams_and_players_2, expected_shot_event_2),
        (shot_event_3, teams_and_players_3, expected_shot_event_3),
        (shot_event_4, teams_and_players_4, expected_shot_event_4),
    ])
    def test_shot_events(self, event, tnp, expected):
        parser.teams_and_players = tnp
        self.assertEqual(parser.parse_event(event), expected)
