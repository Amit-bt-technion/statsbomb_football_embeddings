# **Approaches for core field types** (keep / omit / normalize / categorize / custom)
****
**The following properties should be omitted:**
1. All 'name' properties.
2. related_events property.
3. Player/team/event identifiers.
1. ID
8. Possession
12.Player.id
****
**The following properties should be treated with the specified approach:**

| ID    | Property Name              | Approach    | Comments                                                                             |
|-------|----------------------------|-------------|--------------------------------------------------------------------------------------|
| 0     | Index                      | TBDean      |                                                                                      |
| 1     | Period                     | categorize  |                                                                                      |
| 2     | Timestamp                  | omit - dean | (1) redundant with (period, minute, second) <br/> (2) potential normalization issues |
| 3     | Minute                     | normalize   | Obtain max of last minutes of each period in the game                                |
| 4     | Second                     | normalize   |                                                                                      |
| 5     | Type.id                    | categorize  |                                                                                      |
| 6     | Possession_team.id         | custom      | replace team ids with 0/1                                                            |
| 7     | Play_pattern.id            | categorize  |                                                                                      |
| 8     | Team.id                    | custom      | replace team id with 0/1                                                             |
| 9     | Position.id                | categorize  |                                                                                      |
| 10    | Location.x                 | normalize   | *Are we sure we don't want to duplicate these for each event type?*                  |
| 11    | Location.y                 | normalize   |                                                                                      |
| 12    | Duration                   | TBDean      |                                                                                      |
| 13    | under_pressure             | normalize   |                                                                                      |
| 14    | off_camera                 | TBDean      |                                                                                      |
| 15    | out                        | normalize   |                                                                                      |
| 16-37 | tactics.lineup (team 1)    | TBDean      | positions (i, i+1) = (position_id, jersey_num) of player num (i / 2)                 |
| 38    | tactics.formation (team 1) | TBDean      |                                                                                      |
| 39-60 | tactics.lineup (team 2)    | TBDean      | positions (i, i+1) = (position_id, jersey_num) of player num (i / 2)                 |                                                                   |
| 61    | tactics.formation (team 2) | TBDean      |                                                                                      |

# **Approaches for specialized field types** (keep / omit / normalize / categorize / custom)
****
**The following properties should be omitted:**
1. All 'name' properties.
2. related_events property.
3. Player/team/event identifiers.
1.   ID: omit
8. Possession: omit
12. Player.id: omit
****
**The following properties should be treated with the specified approach:**

| ID |        Property Name           |     Approach  |   Comments   |
|----|--------------------------------|---------------|----------------|
| 1  | 5050.outcome.id                | categorize    | |
| 2  | 5050.counterpress              | categorize    | |
| 3  | bad_behavior.card.id           | categorize    | |
| 4  | ball_recipt.outcome.id         | categorize    | |
| 5  | ball_recovery.offensive        | categorize    | |
| 6  | ball_recovery.recovery_failure | categorize    | |
| 7  | block.deflection               | categorize    | |
| 8  | block.offensive                | categorize    | |
| 9  | block.save_block               | categorize    | |
| 10 | block.counterpress             | categorize    | |
| 12 | carry.end_location.x           | normalize     | |
| 13 | carry.end_location.y           | normalize     | |
| 14 | clearance.aerial_won           | categorize    | |
| 15 | clearance.body_part.id         | categorize    | |
| 16 | dribble.overrun                | categorize    | |
| 17 | dribble.nutmeg                 | categorize    | |
| 18 | dribble.outcome.id             | categorize    | |
| 19 | dribble.no_touch               | categorize    | |
| 20 | dribble_post.counterpress      | categorize    | |
| 21 | duel.counterpress               | categorize    | |
| 22 | duel.type.id                    | categorize    | |
| 23 | duel.outcome.id                 | categorize    | |
| 24 | foul_commited.counterpress      | categorize    | |
| 25 | foul_commited.offensive         | categorize    | |
| 26 | foul_commited.type.id           | categorize    | |
| 27 | foul_commited.advantage         | categorize    | |
| 28 | foul_commited.penalty           | categorize    | |
| 29 | foul_commited.card.id           | categorize    | |
| 30 | foul_won.defensive              | categorize    | |
| 31 | foul_won.advantage              | categorize    | |
| 32 | foul_won.penalty                | categorize    | |
| 33 | goalkeeper.position.id          | categorize    | |
| 34 | goalkeeper.technique.id         | categorize    | |
| 35 | goalkeeper.body_part.id         | categorize    | |
| 36 | goalkeeper.type.id              | categorize    | |
| 37 | goalkeeper.outcome.id           | categorize    | |
| 38 | half_end.early_video_end        | TBDean        | |
| 39 | half_end.match_suspended        | categorize    | |
| 40 | half_start.late_video_start     | categorize    | |
| 41 | injury_stoppage.in_chain        | categorize    | |
| 42 | interception.outcome.id         | categorize    | |
| 43 | miscontrol.aerial_won           | categorize    | |
| 44 | pass.recipient.position         | cusom         | Patched using pass.recipient.id and player-position mapping |
| 45 | pass.length                     | normalize     | |
| 46 | pass.angle                      | normalize     | |
| 47 | pass.height.id                  | categorize    | |
| 48 | pass.end_location.x             | normalize     | |
| 49 | pass.end_location.y             | normalize     | |
| 50 | pass.backheel                   | categorize    | |
| 51 | pass.deflected                  | categorize    | |
| 52 | pass.miscommunication           | categorize    | |
| 53 | pass.cross                      | categorize    | |
| 54 | pass.cut_back                   | categorize    | |
| 55 | pass.switch                     | categorize    | |
| 56 | pass.shot_assist                | categorize    | |
| 57 | pass.goal_assist                | categorize    | |
| 58 | pass.body_part.id               | categorize    | |
| 59 | pass.type.id                    | categorize    | |
| 60 | pass.outcome.id                 | categorize    | |
| 61 | pass.technique.id               | categorize    | |
| 62 | player_off.permanent            | categorize    | |
| 63 | pressure.counterpress           | categorize    | |
| 64 | shot.end_location.x             | normalize     | |
| 65 | shot.end_location.y             | normalize     | |
| 66 | shot.end_location.z             | normalize     | |
| 67 | shot.aerial_won                 |  categorize    | |
| 68 | shot.follows_dribble            | categorize    | |
| 69 | shot.first_time                 | categorize    | |
| 70 | shot.freeze_frame[i].location.x | TBDean        | |
| 71 | shot.freeze_frame[i].location.y | TBDean        | |
| 72 | shot.freeze_frame[i].position.id| categorize    | |
| 73 | shot.freeze_frame[i].teammate   | categorize    | |
| 74 | shot.open_goal                  | categorize    | |
| 75 | shot.statsbomb_xg               | keep          | |
| 76 | shot.deflected                  | categorize    | |
| 77 | shot.technique.id               | categorize    | |
| 78 | shot.body_part.id               | categorize    | |
| 79 | shot.type.id                    | categorize    | |
| 80 | shot.outcome.id                 | categorize    | |
| 81 | substitution.replacement.id     | custom        | Patched from player.id and player-position mapping |
| 82 | substitution.outcome.id         | categorize    | |
| - | ------------------               | ----------    | |
| a | global.player_position_mapping[i].position | categorize | Array for mapping all active player positions |
| b | global.player_position_mapping[i].mapping | categorize | Player's index in the mapping array |



**Global mappings**
1. A mapping of players (currently on field) to positions in input vector & positions on field.
2. Mapping of playing teams to 0 / 1.

# JSON File Event Tokenizer


> Input: json file url that contains match events data in StatsBomb format.

> Output: A matrix of the tokenized event data in the file, in which every row represents an event and rows are ordered by appearance.

## Main Execution Flow

Tokenizer API

```
tokenizer = Tokenizer(<url to json file>)
matrix = tokenizer.get_tokenized_match_events()
```
Tokenizer Execution Flow

```
data = json.load(<url>)
match_events_parser = MatchEventsParser(<mappings args>)
for event in data:
  tokenized_event = match_events_parser.parse_event(event)
  tokenizer.token_matrix.append(tokenized_event)

pickle.dump(tokenizer.token_matrix)
... -> send to Autoencoder
```
Match Event Parsing Execution Flow


```
init()
parse_common_features() # and populate vector accordingly
# reminder - event parsers for each event type are instantiated in mapping declaration
event_parser = event_parser_mapping[self.event_type_id](<mapping>)
return event_parser.parse(eventdata, self.tokenized_event)
```
Event Parser


```
# reminder - feature parser instantiated in mapping declaration
# remider - approaches for nested dictionaries: use FeatureParser subclass or write string parser
for event_name, (vector_index, feature_parser) in event_features_mapping.items():
  if event_obj.get(event_name, None) is not None:
    tokenized_event[vector_index] = feature_parser.get_normalized(event_obj[event_name])
return tokenized_event
```







```














