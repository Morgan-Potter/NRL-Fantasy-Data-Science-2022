import json
from typing import Dict
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

def get_increasing_players(stat, threshold, round_start=0, round_fin=0):
    """Returns a list of all player IDs with an increasing stat over a given round frame."""
    increasing_players = []
    use_first = False
    use_last = False
    if round_start == 0:
        use_first = True
    if round_fin == 0:
        use_last = True
    for id in ID_STATS.keys():
        start, fin = get_first_last_round(id)
        if use_first:
            round_start = start
        if use_last:
            round_fin = fin
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
    """Takes a dict with players and their correlating round stats, and converts them to lists of x and y coordinates with a legend."""
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
    """Returns the first and last round a given player has played, returns 0, 0 if they have not played a round."""
    if len(list(ID_STATS[id]["stats"]["scores"])) > 0:
        return int(list(ID_STATS[id]["stats"]["scores"])[-1]), int(list(ID_STATS[id]["stats"]["scores"])[0])
    else:
        return 0, 0
def plot_xy(data, ax):
    """Plots tuple with lists of x,y and legend on a given axis."""
    for i in range(len(data[0])):
        ax.plot(data[0][i], data[1][i], label=PLAYER_NAME[data[2][i]])
def get_dict_stat_average(stats, round_start, round_fin):
    """Returns the average scores per round of a dict of players."""
    stat_average = dict()
    average = dict()
    for round in range(round_start, round_fin):
        round_sum = 0
        i=0
        for id in stats.keys():
            i += 1
            if round in stats[id]:
                if str(stats[id][round]) != str(np.nan):
                    round_sum += stats[id][round]
        stat_average[round] = round_sum / i
    average["AVERAGE"] = stat_average
    return average
        
def main():
    fig, ax = plt.subplots()
    players = get_increasing_players("prices", -200000)
    print(players)
    # players = [ID_NAME["Siosifa Talakai"], ID_NAME["Nathan Cleary"]]
    price_data = get_list_player_stats(players, "prices")
    average = get_xy(get_dict_stat_average(price_data, 1, 13))
    print(average)
    # players = get_xy(get_list_player_stats([ID_NAME[Siosifa Talakai]]))
    # plot_xy(get_xy(ppt_data), axes)
    # print(get_xy(average))
    ax.plot(average[0][0], average[1][0], label="Average Price", ls='dotted', marker='o', markersize=12)
    ax2 = ax.twinx()
    average2 = get_xy(get_dict_stat_average(get_list_player_stats(players, "avg_scores"), 1, 13))
    ax2.plot(average2[0][0], average2[1][0], label="Average Score Average")
    # plot_xy(get_xy(get_list_player_stats(players, "ppt")), ax2)
    # plot_xy(get_xy(get_list_player_stats(players, "ppt")), axes[2])
    # fig.legend(loc='center right')
    plt.show()

main()