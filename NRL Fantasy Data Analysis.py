import json
# import requests
import numpy as np
import matplotlib.pyplot as plt

# GENERATE CONSTANTS

# # Get data set from fantasy website
# PLAYER_STATS = json.loads(requests.get("https://fantasy.nrl.com/data/nrl/players.json").text)
PLAYER_STATS = json.loads(open("players.json").read()) # Uses pre-downloaded dataset from Fantasy Stats Centre Website.
PLAYER_NAME = dict()
ID_STATS = dict()
for player in PLAYER_STATS: # Loops over dictionaries with player stats.
    # Create required variables
    score_sum = 0
    player_avg_score = dict()
    player_ppt = dict()
    round_num = 0
    # Generates the average points statistic, and price per point if required
    for round in reversed(player["stats"]["scores"].keys()):
        round_num += 1
        score_sum += player["stats"]["scores"][round] # Moving sum of all points scored over each round
        player_avg_score[round] = score_sum / round_num # Cannot divide by the round, as some players miss rounds. 
        # if player_avg_score[round] != 0:
            # player_ppt[round] = player["stats"]["prices"][round] / player_avg_score[round]
    player["stats"]["avg_scores"] = player_avg_score # Moves the average score dict into the player stats
    # player["stats"]["ppt"] = player_ppt
    id = player["id"]
    del player["id"] # Has to be removed so ID_STATS does not have player id as a value.
    PLAYER_NAME[id] = player["first_name"] + ' ' + player["last_name"] # A dict to convert player ids to names.
    ID_STATS[id] = player # Creates a dict with all the needed player stats associated with player id keys.

# DATA CLEANING FUNCTIONS

def get_increasing_players(stat, threshold, round_start=0, round_fin=0):
    """Returns a list of all player IDs with an increasing stat over a given round frame."""
    increasing_players = []

    # Used to determine whether the function needs to return a stat with a given round frame, or use the first and last played rounds.
    use_first = False
    use_last = False
    if round_start == 0:
        use_first = True
    if round_fin == 0:
        use_last = True

    # Main logic
    for id in ID_STATS.keys():
        # Get required variables
        start, fin = get_first_last_round(id)
        if use_first:
            round_start = start
        if use_last:
            round_fin = fin
        start_stat = get_player_round_stat(id, round_start, stat)
        fin_stat = get_player_round_stat(id, round_fin, stat)

        if start_stat != np.nan and fin_stat != np.nan and fin_stat - start_stat > threshold:
            # Append the player id if they have increased in the round frame, and have played in the given starting and finishing rounds. 
            increasing_players.append(id)
    return increasing_players

def get_player_round_stat(id, round, stat):
    """Returns a statistic of a player on a given round, returns nan if the player has not played the round."""
    round = str(round)
    if round in ID_STATS[id]["stats"][stat].keys() and round != 0: # The player could not have played the round, and the round can be 0 if passed get_first_last_round.
        return ID_STATS[id]["stats"][stat][round]
    else:
        return np.nan
def get_list_player_stats(list, stat):
    """Returns the stats of a list of players over all their rounds as a dict."""
    player_stats = dict()
    list_stats = dict()
    for id in list:
        round_start, round_fin = get_first_last_round(id)
        if 0 not in (round_start, round_fin): # Needed as get_first_last_round can return 0
            for round in range(round_start, round_fin + 1): # Seems un-optimized to use a for loop here as the whole stats dictionary can be grabbed with ID_STATS[id]["stats"][stat], however this is needed to give all rounds a value.
                player_stats[round] = (get_player_round_stat(id, round, stat))
            list_stats[id] = player_stats # Makes a dict of player ids with dict values of their stats for each round.
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
            x[i].append(xy[0]) # X axis is the keys, or the player id
            y[i].append(xy[1]) # Y axis is the values for each stat
        legend.append(id)
        i += 1
    return x, y, legend

def get_first_last_round(id):
    """Returns the first and last round a given player has played, returns 0, 0 if they have not played a round."""
    if len(list(ID_STATS[id]["stats"]["scores"])) > 0:
        return int(list(ID_STATS[id]["stats"]["scores"])[-1]), int(list(ID_STATS[id]["stats"]["scores"])[0]) # The stats in the data are in descending order, so the last value is the first round and the first value is the last round.
    else:
        return 0, 0
def get_dict_stat_average(stats, round_start, round_fin):
    """Returns the average scores per round of a dict of players."""
    stat_average = dict()
    average = dict()
    for round in range(round_start, round_fin): # Loops for every round.
        round_sum = 0
        i=0
        for id in stats.keys():
            i += 1 # Counts the number of players
            if round in stats[id].keys(): # If the player has played that round.
                if str(stats[id][round]) != str(np.nan): # If the player has played that round.
                    round_sum += stats[id][round] # Add each players round score to the sum.
        stat_average[round] = round_sum / i # Average the round sum over the number of players
    average["AVERAGE"] = stat_average # Returns a dict of dicts, so it can be used with other functions.
    return average

# DATA VISUALIZATION FUNCTIONS
     
def plot_xy(data, ax):
    """Plots tuple with lists of x,y and legend on a given axis."""
    # This function is used specifically for plotting multiple different player lines. This is not used in my report, but is extra functionality.
    for i in range(len(data[0])):
        ax.plot(data[0][i], data[1][i], label=PLAYER_NAME[data[2][i]])

        
def round_6_9_avg():
    """This is the first example in the report - gets average of players with a spike in rounds 6-9."""
    # Create needed variables
    fig, ax = plt.subplots()
    players = get_increasing_players("prices", 100000, round_start=6, round_fin=9) # Gets the list of increasing players with a 100000$ spike in price between rounds 6-9.
    average = get_xy(get_dict_stat_average(get_list_player_stats(players, "prices"), 1, 13)) # Gets the prices average
    average2 = get_xy(get_dict_stat_average(get_list_player_stats(players, "avg_scores"), 1, 13)) # Gets the avg_scores average
    ax2 = ax.twinx() # Creates a second y axis that shares the x

    # Plot the two lines on their axes.
    ax.plot(average[0][0], average[1][0], label="Average Player Price", ls='dotted', marker='o', markersize=12)
    ax2.plot(average2[0][0], average2[1][0], label="Mean Player Average Score")

    # Setup additional plot elements
    ax.set(ylabel="Average Player Price ($)", xlabel="Round", xticks=range(1,14))
    ax2.set(ylabel="Mean Player Average Score")
    fig.legend(loc='upper right')
    fig.suptitle('Players With Spike of 100000$ Between Rounds 6 and 9')
    plt.show()

def round_3_6_avg():
    """This is the second example in the report - plots average of players with a spike in rounds 3-6."""
    # Create needed variables
    fig, ax = plt.subplots()
    players = get_increasing_players("prices", 100000, round_start=3, round_fin=6) # Gets the list of increasing players with a 100000$ spike in price between rounds 3-6.
    average = get_xy(get_dict_stat_average(get_list_player_stats(players, "prices"), 1, 13)) # Gets the prices average
    average2 = get_xy(get_dict_stat_average(get_list_player_stats(players, "avg_scores"), 1, 13)) # Gets the avg_scores average
    ax2 = ax.twinx() # Creates a second y axis that shares the x

    # Plot the two lines on their axes.
    ax.plot(average[0][0], average[1][0], label="Average Player Price", ls='dotted', marker='o', markersize=12)
    ax2.plot(average2[0][0], average2[1][0], label="Mean Player Average Score")

    # Setup additional plot elements
    ax.set(ylabel="Average Player Price ($)", xlabel="Round", xticks=range(1,14))
    ax2.set(ylabel="Mean Player Average Score")
    fig.legend(loc='upper right')
    fig.suptitle('Average of Players With Spike of 100000$ Between Rounds 3 and 6')
    plt.show()

def round_3_9_player():
    """This is the third example in the report, it plots a specific player with a spike in rounds 3-9."""
    # Get needed variables
    fig, ax = plt.subplots()
    players = [504072] # Set player id list to only be Tom Starling (has a spike of $200000 between rounds 3-9.)
    price_data = get_xy(get_list_player_stats(players, "prices")) # Gets the price data for Tom Starling
    scores_data = get_xy(get_list_player_stats(players, "avg_scores")) # Gets the scores data for Tom Starling
    ax2 = ax.twinx() # Creates second y axis that shares the x

    # Plot the two lines on their axes.
    ax.plot(price_data[0][0], price_data[1][0], label="Price", ls='dotted', marker='o', markersize=12)
    ax2.plot(scores_data[0][0], scores_data[1][0], label="Average Score")

    # Setup additional plot elements
    ax.set(ylabel="Price ($)", xlabel="Round", xticks=range(1,14))
    ax2.set(ylabel="Average Score")
    fig.legend(loc='upper right')
    fig.suptitle('Tom Starling')
    plt.show()

def all_player_example():
    """This is an example of the codes further functionality in plotting multiples players. This plots the price all the players with a spike in rounds 6-9"""
    # Create needed variables
    fig, ax = plt.subplots()
    players = get_increasing_players("prices", 100000, round_start=6, round_fin=9) # Gets the list of increasing players with a 100000$ spike in price between rounds 6-9.

    # Plot all the player lines.
    plot_xy(get_xy(get_list_player_stats(players, "prices")), ax)

    # Setup additional plot elements
    ax.set(ylabel="Player Price ($)", xlabel="Round", xticks=range(1,14))
    fig.legend(loc='upper right')
    fig.suptitle('Players With Spike of 100000$ Between Rounds 6 and 9')
    plt.show()

round_6_9_avg()
round_3_6_avg()
round_3_9_player()
all_player_example()