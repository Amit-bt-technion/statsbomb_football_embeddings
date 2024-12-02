import pandas as pd
from feature_parsers import EventParser, FeatureParser

# Master Parser

# TODO: make use of a better practice
vector_size = 105


class MasterParser:
    def __init__(self, event_parser_mapping: dict[int, EventParser],
                 common_feature_mapping: dict[str, tuple[int, FeatureParser]]):
        self.event_parser_mapping = event_parser_mapping
        self.common_feature_mapping = common_feature_mapping
        self.tokenized_event = None
        self.event_type_id = None

    def parse_common_features(self):
        # extract common features using the mappings.
        # set event_type_id property
        pass

    def parse_event(self, event: dict):
        self.tokenized_event = pd.Series(0, index=range(vector_size))
        self.event_type_id = None
        # call parse_common_features
        # extract  specific event block (data)
        # call event parser of this event using the mapping and event_type_id property with data
        pass
