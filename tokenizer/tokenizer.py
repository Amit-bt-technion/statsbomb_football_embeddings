import os
import json
import pandas as pd
from urllib.request import urlopen
from typing import List
from tokenizer.event_parser import EventParser
from tokenizer import logger, vector_size

# ************************************************************************************************************
#                                           Tokenizer Class
# ************************************************************************************************************


class Tokenizer:
    """
    This class handles tokenizing of entire matches into dataframes, where each row corresponds to an event by order.

    Attributes:
        path: a relative / absolute file-system path or a url of the match json file.
        data: a list of dictionaries loaded from the json file, where each dictionary corresponds to an event.
        tokenized_events_matrix: a list of lists that contains the tokenized events, each list is an event representation.
        tokenized_events_dataframe: a pandas dataframe that contains the tokenized events of the entire match.
        event_parser: an instance of EventParser used to process each event.
    """
    def __init__(self, path: str, is_online_resource: bool = False):
        """
       Initialize a tokenizer for match event data.

       :param path: Path to the JSON file containing match events or URL for remote resources.
       :param is_online_resource: Whether the path is a URL (True) or local file path (False).

       Raises:
           FileNotFoundError: If the local file cannot be found.
           HTTPError: If the URL cannot be accessed (for online resources).
       """
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
        self.event_parser = EventParser(vector_size)

    def get_tokenized_match_events(self) -> pd.DataFrame:
        """
        Returns a tokenized match events dataframe.
        :return: a pandas dataframe that contains the tokenized events of the entire match.
        """
        for event in self.data:
            tokenized_event = self.event_parser.parse_event(event)
            if tokenized_event is not None:
                self.tokenized_events_matrix.append(tokenized_event)

        self.tokenized_events_dataframe = pd.DataFrame(self.tokenized_events_matrix)
        return self.tokenized_events_dataframe

    def export_to_csv(self, path='./'):
        """
        Exports the tokenized match events dataframe to a csv file placed in the given path.
        :param path: a local file=system path of the directory in which the csv file should be saved.
        """
        os.makedirs(path, exist_ok=True)
        file_path = os.path.normpath(os.path.join(path, f"{self._get_match_file_name()}.csv"))
        self.tokenized_events_dataframe.to_csv(file_path)

    def _get_match_file_name(self):
        """
        Extracts the file name without the file extension.
        :return: a string with the file name without the file extension.
        """
        return os.path.splitext(os.path.basename(self.path))[0]
