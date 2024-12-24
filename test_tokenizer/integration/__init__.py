
# shot events taken from https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/16120.json

shot_event_1 = {
  "id" : "d3448b6e-b4eb-4d30-9e4e-ebbf95533d30",
  "index" : 314,
  "period" : 1,
  "timestamp" : "00:05:09.168",
  "minute" : 5,
  "second" : 9,
  "type" : {
    "id" : 16,
    "name" : "Shot"
  },
  "possession" : 10,
  "possession_team" : {
    "id" : 216,
    "name" : "Getafe"
  },
  "play_pattern" : {
    "id" : 1,
    "name" : "Regular Play"
  },
  "team" : {
    "id" : 216,
    "name" : "Getafe"
  },
  "player" : {
    "id" : 6611,
    "name" : "Ángel Luis Rodríguez Díaz"
  },
  "position" : {
    "id" : 22,
    "name" : "Right Center Forward"
  },
  "location" : [ 103.7, 48.2 ],
  "duration" : 0.808543,
  "related_events" : [ "bb27d750-9f1a-401e-8c96-3e81423340d1" ],
  "shot" : {
    "statsbomb_xg" : 0.12042114,
    "end_location" : [ 120.0, 40.8, 5.6 ],
    "key_pass_id" : "d20d9571-7d6d-419d-b245-b2bc95f8eb23",
    "technique" : {
      "id" : 95,
      "name" : "Volley"
    },
    "first_time" : True,
    "outcome" : {
      "id" : 98,
      "name" : "Off T"
    },
    "body_part" : {
      "id" : 40,
      "name" : "Right Foot"
    },
    "type" : {
      "id" : 87,
      "name" : "Open Play"
    },
    "freeze_frame" : [ {
      "location" : [ 105.1, 39.8 ],
      "player" : {
        "id" : 6379,
        "name" : "Sergi Roberto Carnicer"
      },
      "position" : {
        "id" : 2,
        "name" : "Right Back"
      },
      "teammate" : False
    }, {
      "location" : [ 91.4, 32.6 ],
      "player" : {
        "id" : 6873,
        "name" : "Francisco Portillo Soler"
      },
      "position" : {
        "id" : 16,
        "name" : "Left Midfield"
      },
      "teammate" : True
    }, {
      "location" : [ 108.8, 51.4 ],
      "player" : {
        "id" : 6826,
        "name" : "Clément Lenglet"
      },
      "position" : {
        "id" : 5,
        "name" : "Left Center Back"
      },
      "teammate" : False
    }, {
      "location" : [ 118.4, 42.7 ],
      "player" : {
        "id" : 20055,
        "name" : "Marc-André ter Stegen"
      },
      "position" : {
        "id" : 1,
        "name" : "Goalkeeper"
      },
      "teammate" : False
    }, {
      "location" : [ 113.7, 63.4 ],
      "player" : {
        "id" : 5213,
        "name" : "Gerard Piqué Bernabéu"
      },
      "position" : {
        "id" : 3,
        "name" : "Right Center Back"
      },
      "teammate" : False
    }, {
      "location" : [ 103.5, 53.1 ],
      "player" : {
        "id" : 5470,
        "name" : "Ivan Rakitić"
      },
      "position" : {
        "id" : 10,
        "name" : "Center Defensive Midfield"
      },
      "teammate" : False
    }, {
      "location" : [ 101.1, 72.2 ],
      "player" : {
        "id" : 5211,
        "name" : "Jordi Alba Ramos"
      },
      "position" : {
        "id" : 6,
        "name" : "Left Back"
      },
      "teammate" : False
    }, {
      "location" : [ 96.4, 65.6 ],
      "player" : {
        "id" : 4546,
        "name" : "Dimitri Foulquier"
      },
      "position" : {
        "id" : 12,
        "name" : "Right Midfield"
      },
      "teammate" : True
    }, {
      "location" : [ 114.2, 72.4 ],
      "player" : {
        "id" : 11550,
        "name" : "Jaime Mata Arnaiz"
      },
      "position" : {
        "id" : 24,
        "name" : "Left Center Forward"
      },
      "teammate" : True
    } ]
  }
}


expected_shot_event_1 = [0.29411764705882354, 0.1111111111111111, 0.8641666666666666, 0.6025, 0.26951433333333336, 0.5, 0.5, 0.5, 0.2, 0.16666666666666666, 0.88, 0.08333333333333333, 0.5, 0.5, 0.88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.75, 1.0, 0.51, 1.0, 0.5, 0.5, 1.0, 0.5, 0.12042114, 0.5, 1.0, 0.75, 0.375, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.8033333333333333, 0.82, 0.7616666666666667, 0.40750000000000003, 0, 0, 0.9516666666666667, 0.905, 0.9866666666666667, 0.5337500000000001, 0.8758333333333332, 0.49749999999999994, 0.9475, 0.7925, 0.9066666666666666, 0.6425, 0.8424999999999999, 0.9025000000000001, 0.8625, 0.6637500000000001, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
