import json
import requests

# CONSTANTS
PLAYER_STATS = json.loads(requests.get("https://fantasy.nrl.com/data/nrl/players.json").text)
COACH_STATS = json.loads(requests.get("https://fantasy.nrl.com/data/nrl/coach/players.json").text)
PLAYER_NAME = dict()
ID_NAME = dict()
FULL_STATS = dict()
for a in PLAYER_STATS: 
    id = a["id"]
    del a["id"]
    PLAYER_NAME[id] = a["first_name"] + ' ' + a["last_name"]
    ID_NAME[a["first_name"] + ' ' + a["last_name"]] = id
    FULL_STATS[id] = {**a, **COACH_STATS[str(id)]}

def get_last_element(list):
    return list[-1]

def get_player_stats(player_name):
    return FULL_STATS[ID_NAME[player_name]]
proj_score_dict = dict()
proj_score = []
for a in FULL_STATS.keys():
    if not FULL_STATS[a]['proj_prices'].keys().__contains__('14'): 
        FULL_STATS[a]['proj_prices']['14'] = 0
    proj_score_dict[FULL_STATS[a]['first_name'] + ' ' + FULL_STATS[a]['last_name']] = FULL_STATS[a]['proj_prices']['14'] - FULL_STATS[a]['stats']['prices']['13']
    proj_score.append((FULL_STATS[a]['first_name'] + ' ' + FULL_STATS[a]['last_name'], FULL_STATS[a]['proj_prices']['14'] - FULL_STATS[a]['stats']['prices']['13']))
print(FULL_STATS)