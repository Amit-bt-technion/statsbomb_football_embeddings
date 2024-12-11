import json
import pandas as pd
from urllib.request import urlopen
from typing import List
from tokenizer.match_parser import MatchEventsParser
from tokenizer import logger, common_features_start_index, vector_size

# ************************************************************************************************************
#                                           Tokenizer Class
# ************************************************************************************************************


class Tokenizer:
    def __init__(self, path: str, is_online_resource: bool = False):
        # load the json list of dicts
        try:
            if not is_online_resource:
                with open(path, encoding='utf-8') as match_json:
                    self.data: List[dict] = json.load(match_json)
            else:
                with urlopen(path) as match_json:
                    self.data: List[dict] = json.load(match_json)
        except FileNotFoundError:
            logger.error("json file not found!")

        self.path = path
        self.tokenized_events_matrix = []
        self.tokenized_events_dataframe = None
        self.match_parser = MatchEventsParser(
            common_features_start_index,
            vector_size
        )

    def get_tokenized_match_events(self) -> pd.DataFrame:
        for event in self.data:
            tokenized_event = self.match_parser.parse_event(event)
            if tokenized_event is not None:
                self.tokenized_events_matrix.append(tokenized_event)

        self.tokenized_events_dataframe = pd.DataFrame(self.tokenized_events_matrix)
        return self.tokenized_events_dataframe

    def export_to_csv(self, path='./'):
        if path[-1] != '/':
            path = f"{path}/"
        self.tokenized_events_dataframe.to_csv(f"{path}{self._get_match_file_name()}.csv")

    def _get_match_file_name(self):
        return self.path.split('/')[-1].split('.')[0]
