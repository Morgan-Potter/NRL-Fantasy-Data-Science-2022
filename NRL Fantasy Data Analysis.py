import json
import requests
import numpy as np
import matplotlib.pyplot as plt

# CONSTANTS
# # Get data set from fantasy website
# PLAYER_STATS = json.loads(requests.get("https://fantasy.nrl.com/data/nrl/players.json").text)
# COACH_STATS = json.loads(requests.get("https://fantasy.nrl.com/data/nrl/coach/players.json").text)
PLAYER_STATS = json.loads(open("players.json").read())
# COACH_STATS = json.loads(open("coachplayers.json").read())
PLAYER_NAME = dict()
ID_NAME = dict()
# FULL_STATS = dict()
ID_STATS = dict()
for player in PLAYER_STATS:
    score_sum = 0
    player_avg_score = dict()
    player_ppt = dict()
    round_num = 0
    for round in reversed(player["stats"]["scores"].keys()):
        round_num += 1
        score_sum += player["stats"]["scores"][round]
        player_avg_score[round] = score_sum / round_num
        if player_avg_score[round] != 0:
            player_ppt[round] = player["stats"]["prices"][round] / player_avg_score[round]
    player["stats"]["avg_scores"] = player_avg_score
    player["stats"]["ppt"] = player_ppt
    id = player["id"]
    del player["id"]
    PLAYER_NAME[id] = player["first_name"] + ' ' + player["last_name"]
    ID_NAME[player["first_name"] + ' ' + player["last_name"]] = id
    ID_STATS[id] = player

# def get_player_stats(player_name):
#     return FULL_STATS[ID_NAME[player_name]]
# proj_score_dict = dict()
# proj_score = []
# for a in FULL_STATS.keys():
#     if not FULL_STATS[a]['proj_prices'].keys().__contains__('14'): 
#         FULL_STATS[a]['proj_prices']['14'] = 0
#     proj_score_dict[FULL_STATS[a]['first_name'] + ' ' + FULL_STATS[a]['last_name']] = FULL_STATS[a]['proj_prices']['14'] - FULL_STATS[a]['stats']['prices']['13']
#     proj_score.append((FULL_STATS[a]['first_name'] + ' ' + FULL_STATS[a]['last_name'], FULL_STATS[a]['proj_prices']['14'] - FULL_STATS[a]['stats']['prices']['13']))

def get_increasing_players(stat, threshold):
    """Returns a list of all player IDs with an increasing stat over a given round frame."""
    increasing_players = []
    for id in ID_STATS.keys():
        round_start, round_fin = get_first_last_round(id)
        start_stat = get_player_round_stat(id, round_start, stat)
        fin_stat = get_player_round_stat(id, round_fin, stat)
        if start_stat != np.nan and fin_stat != np.nan and fin_stat - start_stat > threshold:
            increasing_players.append(id)
    return increasing_players

def get_player_round_stat(id, round, stat):
    """Returns a statistic of a player on a given round, returns nan if the player has not played the round."""
    round = str(round)
    if round in ID_STATS[id]["stats"][stat].keys() and round != 0:
        return ID_STATS[id]["stats"][stat][round]
    else:
        return np.nan
def get_list_player_stats(list, stat):
    """Returns the stats of a list of players over a given round frame as a dict."""
    player_stats = dict()
    list_stats = dict()
    for id in list:
        round_start, round_fin = get_first_last_round(id)
        if 0 not in (round_start, round_fin):
            for round in range(round_start, round_fin + 1):
                player_stats[round] = (get_player_round_stat(id, round, stat))
            list_stats[id] = player_stats
            player_stats = dict()
    return list_stats

def get_xy(player_stats_dict):
    """Takes a dict with players and their correlating round stats, and converts them to x and y coordinates."""
    x = []
    y = []
    i = 0
    legend = []
    for id in player_stats_dict.keys():
        x.append([])
        y.append([])
        for xy in player_stats_dict[id].items():
            x[i].append(xy[0])
            y[i].append(xy[1])
        legend.append(id)
        i += 1
    return x, y, legend

def get_first_last_round(id):
    if len(list(ID_STATS[id]["stats"]["scores"])) > 0:
        return int(list(ID_STATS[id]["stats"]["scores"])[-1]), int(list(ID_STATS[id]["stats"]["scores"])[0])
    else:
        return 0, 0
def plot_xy(data, ax):
    for i in range(len(data[0])):
        ax.plot(data[0][i], data[1][i], label=PLAYER_NAME[data[2][i]])
def main():
    fig, axes = plt.subplots(2, 1)
    players = get_increasing_players("prices", 200000)
    ppt_data = get_xy(get_list_player_stats(players, "prices"))
    plot_xy(ppt_data, axes[0])
    plot_xy(get_xy(get_list_player_stats(players, "avg_scores")), axes[1])

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right')
    plt.show()

main()