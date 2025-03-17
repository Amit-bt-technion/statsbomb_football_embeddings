# Tokenized Football Event Data for Machine Learning

## Introduction
This project is an academic endeavor developed at the Technion - Israel Institute of Technology. It leverages the [StatsBomb Open Data](https://github.com/statsbomb/open-data) project to create a tokenized representation of football match events. The project aims to convert raw football event data into structured, machine-learning-ready vectors that can be used in research and academic projects.

The tokenizer processes event data from football matches and generates a consistent feature vector for each event. These feature vectors can be utilized in various machine learning contexts, including predictive modeling, event classification, and match analysis, such as predicting match outcomes or classifying player actions.

## Design Choices
1. **Standalone event approach**: Each event is regarded as standalone, and there is no shared state or context between events.
2. **Player identity anonymity**: Event representations do not include information regarding the players' identities, but do account for the players' roles on the field.
3. **Team anonymity**: Event representations do not include information regarding the specific football clubs in play.
4. **Timestamps**: Event time is recorded using 3 features - period, minute, and second.
5. **Discarded event types**: Tactics, starting 11, half start and half end events are skipped.

## Normalization Choices
1. **Multiclass features**: Represented as discrete values in range (0, 1] (excluding 0) in constant intervals using min-max normalization.
2. **Boolean features**: Represented as 0.5 or 1.
3. **Continuous features**: Represented as continuous values in range [0, 1] (zero-inclusive), where values exceeding the allowed range from Statsbomb Doc are approximated to the closest end of the range.

## Visual Representation of the Output Vectors
Each event is represented by a 128-dimensional vector. Below is a comprehensive breakdown of all 128 indices and their data types:

| Index | Name                               | Type         | Details    |
|-------|------------------------------------|--------------|------------|
| 0     | Event Type                         | Discrete     | 30 classes |
| 1     | Play Pattern                       | Discrete     | 9 classes  |
| 2     | X Location                         | Continuous   |            |
| 3     | Y Location                         | Continuous   |            |
| 4     | Duration                           | Continuous   |            |
| 5     | Under Pressure                     | Boolean      |            |
| 6     | Out                                | Boolean      |            |
| 7     | Counterpress                       | Boolean      |            |
| 8     | Period                             | Discrete     | 5 classes  |
| 9     | Second                             | Discrete     | 60 classes |
| 10    | Position ID                        | Discrete     | 25 classes |
| 11    | Minute                             | Continuous   |            |
| 12    | Team ID                            | Discrete     |            |
| 13    | Possession Team ID                 | Discrete     |            |
| 14    | Player Position Designation        | Discrete     |            |
| 15    | Offensive Ball Recovery            | Boolean      |            |
| 16    | Failed Ball Recovery               | Boolean      |            |
| 17    | Duel Type                          | Discrete     | 2 classes  |
| 18    | Duel Outcome                       | Discrete     | 7 classes  |
| 19    | Block Deflection                   | Boolean      |            |
| 20    | Block Offensive                    | Boolean      |            |
| 21    | Block Saved                        | Boolean      |            |
| 22    | Clearance Aerial Won               | Boolean      |            |
| 23    | Clearance Body Part                | Discrete     | 4 classes  |
| 24    | Interception Outcome               | Discrete     | 7 classes  |
| 25    | Dribble Overrun                    | Boolean      |            |
| 26    | Dribble Nutmeg                     | Boolean      |            |
| 27    | Dribble Outcome                    | Discrete     | 2 classes  |
| 28    | Dribble No Touch                   | Boolean      |            |
| 29    | Substitution Outcome               | Discrete     | 2 classes  |
| 30    | Foul Won Defensive                 | Boolean      |            |
| 31    | Foul Won Advantage                 | Boolean      |            |
| 32    | Foul Won Penalty                   | Boolean      |            |
| 33    | Foul Committed Type                | Discrete     | 6 classes  |
| 34    | Offensive Foul Committed           | Boolean      |            |
| 35    | Foul Committed Advantage           | Boolean      |            |
| 36    | Foul Committed Penalty             | Boolean      |            |
| 37    | Foul Committed Card                | Discrete     | 3 classes  |
| 38    | Goalkeeper Type                    | Discrete     | 14 classes |
| 39    | Goalkeeper Outcome                 | Discrete     | 19 classes |
| 40    | Goalkeeper Position                | Discrete     | 3 classes  |
| 41    | Goalkeeper Technique               | Discrete     | 2 classes  |
| 42    | Goalkeeper Body Part               | Discrete     | 7 classes  |
| 43    | Goalkeeper End Location X          | Continuous   |            |
| 44    | Goalkeeper End Location Y          | Continuous   |            |
| 45    | Bad Behavior Card                  | Discrete     | 3 classes  |
| 46    | Player Off Permanently             | Boolean      |            |
| 47    | Pass Type                          | Discrete     | 7 classes  |
| 48    | Pass Length                        | Continuous   |            |
| 49    | Pass Angle                         | Continuous   |            |
| 50    | Pass Height                        | Discrete     | 3 classes  |
| 51    | Pass End Location X                | Continuous   |            |
| 52    | Pass End Location Y                | Continuous   |            |
| 53    | Pass Backheel                      | Boolean      |            |
| 54    | Pass Deflected                     | Boolean      |            |
| 55    | Pass Miscommunication              | Boolean      |            |
| 56    | Pass Cross                         | Boolean      |            |
| 57    | Pass Cut Back                      | Boolean      |            |
| 58    | Pass Switch                        | Boolean      |            |
| 59    | Pass Shot Assist                   | Boolean      |            |
| 60    | Pass Goal Assist                   | Boolean      |            |
| 61    | Pass Body Part                     | Discrete     | 7 classes  |
| 62    | Pass Outcome                       | Discrete     | 5 classes  |
| 63    | Pass Technique                     | Discrete     | 4 classes  |
| 64    | Recipient Player Position          | Discrete     |            |
| 65    | 50/50 Outcome                      | Discrete     | 4 classes  |
| 66    | Miscontrol Aerial Won              | Boolean      |            |
| 67    | Injury Stoppage                    | Boolean      |            |
| 68    | Ball Receipt Outcome               | Discrete     | 1 class    |
| 69    | Carry End Location X               | Continuous   |            |
| 70    | Carry End Location Y               | Continuous   |            |
| 71    | Shot Type                          | Discrete     | 4 classes  |
| 72    | Shot End Location X                | Continuous   |            |
| 73    | Shot End Location Y                | Continuous   |            |
| 74    | Shot End Location Z                | Continuous   |            |
| 75    | Shot Aerial Won                    | Boolean      |            |
| 76    | Shot Follows Dribble               | Boolean      |            |
| 77    | Shot First Time                    | Boolean      |            |
| 78    | Shot Open Goal                     | Boolean      |            |
| 79    | Shot StatsBomb xG                  | Continuous   |            |
| 80    | Shot Deflected                     | Boolean      |            |
| 81    | Shot Technique                     | Discrete     | 7 classes  |
| 82    | Shot Body Part                     | Discrete     | 4 classes  |
| 83    | Shot Outcome                       | Discrete     | 8 classes  |
| 84    | Freeze Frame Player 1 Position X   | Continuous   |            |
| 85    | Freeze Frame Player 1 Position Y   | Continuous   |            |
| 86    | Freeze Frame Player 2 Position X   | Continuous   |            |
| 87    | Freeze Frame Player 2 Position Y   | Continuous   |            |
| 88    | Freeze Frame Player 3 Position X   | Continuous   |            |
| 89    | Freeze Frame Player 3 Position Y   | Continuous   |            |
| 90    | Freeze Frame Player 4 Position X   | Continuous   |            |
| 91    | Freeze Frame Player 4 Position Y   | Continuous   |            |
| 92    | Freeze Frame Player 5 Position X   | Continuous   |            |
| 93    | Freeze Frame Player 5 Position Y   | Continuous   |            |
| 94    | Freeze Frame Player 6 Position X   | Continuous   |            |
| 95    | Freeze Frame Player 6 Position Y   | Continuous   |            |
| 96    | Freeze Frame Player 7 Position X   | Continuous   |            |
| 97    | Freeze Frame Player 7 Position Y   | Continuous   |            |
| 98    | Freeze Frame Player 8 Position X   | Continuous   |            |
| 99    | Freeze Frame Player 8 Position Y   | Continuous   |            |
| 100   | Freeze Frame Player 9 Position X   | Continuous   |            |
| 101   | Freeze Frame Player 9 Position Y   | Continuous   |            |
| 102   | Freeze Frame Player 10 Position X  | Continuous   |            |
| 103   | Freeze Frame Player 10 Position Y  | Continuous   |            |
| 104   | Freeze Frame Player 11 Position X  | Continuous   |            |
| 105   | Freeze Frame Player 11 Position Y  | Continuous   |            |
| 106   | Freeze Frame Player 12 Position X  | Continuous   |            |
| 107   | Freeze Frame Player 12 Position Y  | Continuous   |            |
| 108   | Freeze Frame Player 13 Position X  | Continuous   |            |
| 109   | Freeze Frame Player 13 Position Y  | Continuous   |            |
| 110   | Freeze Frame Player 14 Position X  | Continuous   |            |
| 111   | Freeze Frame Player 14 Position Y  | Continuous   |            |
| 112   | Freeze Frame Player 15 Position X  | Continuous   |            |
| 113   | Freeze Frame Player 15 Position Y  | Continuous   |            |
| 114   | Freeze Frame Player 16 Position X  | Continuous   |            |
| 115   | Freeze Frame Player 16 Position Y  | Continuous   |            |
| 116   | Freeze Frame Player 17 Position X  | Continuous   |            |
| 117   | Freeze Frame Player 17 Position Y  | Continuous   |            |
| 118   | Freeze Frame Player 18 Position X  | Continuous   |            |
| 119   | Freeze Frame Player 18 Position Y  | Continuous   |            |
| 120   | Freeze Frame Player 19 Position X  | Continuous   |            |
| 121   | Freeze Frame Player 19 Position Y  | Continuous   |            |
| 122   | Freeze Frame Player 20 Position X  | Continuous   |            |
| 123   | Freeze Frame Player 20 Position Y  | Continuous   |            |
| 124   | Freeze Frame Player 21 Position X  | Continuous   |            |
| 125   | Freeze Frame Player 21 Position Y  | Continuous   |            |
| 126   | Freeze Frame Player 22 Position X  | Continuous   |            |
| 127   | Freeze Frame Player 22 Position Y  | Continuous   |            |


## Example Usage
The following code snippet demonstrates how to use the `Tokenizer` class to process football match event data and export the tokenized vectors to CSV files, assuming [StatsBomb's Open Data](https://github.com/statsbomb/open-data) repo is cloned as a sibling directory to the project root:

```python
from tokenizer.tokenizer import Tokenizer
import os

base_dir = os.getcwd()
events_dir = os.path.join(base_dir, "..", "open-data", "data", "events")

if __name__ == "__main__":
    for match in os.listdir(events_dir):
        try:
            tokenizer = Tokenizer(os.path.join(events_dir, match))
            df = tokenizer.get_tokenized_match_events()
            tokenizer.export_to_csv("csv/")
        except Exception as e:
            print(f"{match} failed with error: {e}")
```

The following code snippet demonstrates how to use the `Tokenizer` class to process football match event data without cloning the open-data repo:

```python
from tokenizer.tokenizer import Tokenizer

if __name__ == "__main__":
    matches = [
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15946.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15956.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15973.json",
    ]   
    for match in matches:
        tokenizer = Tokenizer(match, True)
        tokenizer.get_tokenized_match_events()
        # tokenizer.export_to_csv("csv/")
```

## Installation
To install the necessary dependencies, run:
```bash
pip install -r requirements.txt
```

## Repository Authors
Amit Ben-Tzvi & Ilan Zendel.

## Contributing
We welcome contributions to improve this project. Please submit issues or pull requests on the project's GitHub repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.








