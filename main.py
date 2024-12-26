from tokenizer.tokenizer import Tokenizer

if __name__ == "__main1__":
    matches = [
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15946.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15956.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15973.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15978.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15986.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15998.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16010.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16023.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16029.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16056.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16073.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16079.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16086.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16095.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16109.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16120.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16131.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16136.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16149.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16157.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16173.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16182.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16190.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16196.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16205.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16215.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16231.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16240.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16248.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16265.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16275.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16289.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16306.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16317.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18235.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18236.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18237.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18240.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18241.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18242.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18243.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18244.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/18245.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19714.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19715.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19716.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19717.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19718.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19719.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19720.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19722.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19723.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19724.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19725.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19726.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19727.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19728.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19729.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19730.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19731.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19732.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19733.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19734.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19735.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19736.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19737.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19738.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19739.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19740.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19741.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19742.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19743.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19744.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19745.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/19746.json"
    ]
    for match in matches:
        tokenizer = Tokenizer(match, True)
        tokenizer.get_tokenized_match_events()
        # tokenizer.export_to_csv("matches/")

if __name__ == "__main__":
    from test_tokenizer.integration import shot_event_1, shot_event_4, shot_event_2, shot_event_3, teams_and_players_1, teams_and_players_2, teams_and_players_3, teams_and_players_4
    from tokenizer.tokenizer import MatchEventsParser
    parser = MatchEventsParser(128)
    parser.teams_and_players = teams_and_players_1
    vec_1 = parser.parse_event(shot_event_1)
    parser.teams_and_players = teams_and_players_2
    vec_2 = parser.parse_event(shot_event_2)
    parser.teams_and_players = teams_and_players_3
    vec_3 = parser.parse_event(shot_event_3)
    parser.teams_and_players = teams_and_players_4
    vec_4 = parser.parse_event(shot_event_4)
    vec = []
