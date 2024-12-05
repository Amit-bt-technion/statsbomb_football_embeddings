from abc import ABC, abstractmethod
from typing import List, Any
import pandas as pd


# Feature Classes definitions

class FeatureParser(ABC):
    def __init__(self, name: str):
        self.feature_name = name

    # TODO: implement and override as necessary
    @abstractmethod
    def get_normalized(self, val: float) -> float:
        pass

    def __repr__(self):
        return f"{self.feature_name} parser"


class RangeFeatureParser(FeatureParser):
    def __init__(self, name: str, min_value: float, max_value: float) -> None:
        super().__init__(name)
        self.min_value = min_value
        self.max_value = max_value

    def get_normalized(self, val):
        if val > self.max_value:
            val = self.max_value
        if val < self.min_value:
            val = self.min_value
        return (val - self.min_value) / (self.max_value - self.min_value)


class CategoricalFeatureParser(FeatureParser):
    def __init__(self, name: str, categories: List[Any]):
        super().__init__(name)
        self.categories = {value: index + 1 for index, value in enumerate(categories)}
        self.num_categories = len(categories)

    def get_normalized(self, val):
        return self.categories.get(val, 0) / self.num_categories


# Event Parser class definitions

# class EventParser(ABC):
#     def __init__(self, event_features_mapping: dict[str, tuple[int, FeatureParser]]):
#         # might need to add starting index location for vector data population
#         self.event_features_mapping = event_features_mapping
#         self.features_num = len(event_features_mapping)
#         self.tokenized_event = None
#
#     @abstractmethod
#     def parse(self, event_obj: dict[str, Any], tokenized_event: pd.Series) -> pd.Series:
#         self.tokenized_event = tokenized_event

