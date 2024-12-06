import json
import pandas as pd
from urllib.request import urlopen
from typing import List, Union
from tokenizer.match_parser import MatchEventsParser
from tokenizer import logger, common_features_start_index

# ************************************************************************************************************
#                                           Tokenizer Class
# ************************************************************************************************************


class Tokenizer:
    def __init__(self, path: str, is_online_resource: bool = False):
        # load the json list of dicts
        try:
            if not is_online_resource:
                with open(path) as match_json:
                    self.data: List[dict] = json.load(match_json)
            else:
                with urlopen(path) as match_json:
                    self.data: List[dict] = json.load(match_json)
        except FileNotFoundError:
            logger.error("json file not found!")

        self.vector_size = 85
        self.tokenized_events_matrix = pd.DataFrame(columns=[f'col_{i}' for i in range(self.vector_size)], dtype=float)
        self.match_parser = MatchEventsParser(
            common_features_start_index,
            self.vector_size
        )

    def get_tokenized_match_events(self) -> pd.DataFrame:
        for i, event in enumerate(self.data):
            tokenized_event = self.match_parser.parse_event(event)
            if tokenized_event is not None:
                print(tokenized_event)
                self.tokenized_events_matrix.loc[len(self.tokenized_events_matrix)] = tokenized_event

        return self.tokenized_events_matrix
