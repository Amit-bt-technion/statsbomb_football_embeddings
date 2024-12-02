import json
import pandas as pd


class Tokenizer:
  def __init__(self, url: str):
    self.data = json.loads(url)
    self.tokenized_events_matrix = pd.DataFrame()  # initialize
