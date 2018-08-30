#%%
import pandas as pd
import numpy as np
import itertools
import copy
import progressbar

bar = progressbar.ProgressBar(max_value=4096)
# At First we create all the w-l condition as 0,1 by itertools
scenario_list = list(itertools.product((0,1), repeat=12))

# The 8 teams in LMS and their score 
# (we don't need team.json and team1.json anymore)
team_score_list = {'FW':[11,0,22,2,22,2]
                  ,'AHQ':[3,8,7,17,7,17]
                  ,'M17':[3,8,10,18,10,18]
                  ,'MAD':[8,3,16,9,16,9]
                  ,'HKA':[7,4,16,11,16,11]
                  ,'AFR':[3,8,8,18,8,18]
                  ,'GREX':[4,7,13,17,13,17]
                  ,'JT':[5,6,14,15,14,15]}
matchup_table = {'AHQ': 
                    {'FW': [0, 4], 'M17': [0, 4], 'HKA': [1, 4], 'AFR': [2, 0], 'GREX': [2, 1], 'MAD': [0, 2], 'JT': [2, 2]}, 
                'FW': 
                    {'AHQ': [4, 0], 'M17': [2, 0], 'HKA': [4, 0], 'AFR': [4, 1], 'GREX': [2, 0], 'MAD': [4, 0], 'JT': [2, 1]},
                'M17': 
                    {'AHQ': [4, 0], 'FW': [0, 2], 'HKA': [2, 1], 'AFR': [1, 4], 'GREX': [1, 4], 'MAD': [1, 4], 'JT': [1, 2]}, 
                'HKA': 
                    {'AHQ': [4, 1], 'FW': [0, 4], 'M17': [1, 2], 'AFR': [2, 0], 'GREX': [4, 1], 'MAD': [2, 0], 'JT': [3, 3]}, 
                'AFR': 
                    {'AHQ': [0, 2], 'FW': [1, 4], 'M17': [4, 1], 'HKA': [0, 2], 'GREX': [3, 3], 'MAD': [0, 4], 'JT': [0, 2]}, 
                'GREX': 
                    {'AHQ': [1, 2], 'FW': [0, 2], 'M17': [4, 1], 'HKA': [1, 4], 'AFR': [3, 3], 'MAD': [1, 2], 'JT': [3, 3]}, 
                'MAD': 
                    {'AHQ': [2, 0], 'FW': [0, 4], 'M17': [4, 1], 'HKA': [0, 2], 'AFR': [4, 0], 'GREX': [2, 1], 'JT': [4, 1]}, 
                'JT': 
                    {'AHQ': [2, 2], 'FW': [1, 2], 'M17': [2, 1], 'HKA': [3, 3], 'AFR': [2, 0], 'GREX': [3, 3], 'MAD': [1, 4]}
                }
matches_list = [['AFR', 'HKA'],['GREX', 'MAD'],['JT', 'M17'],['AHQ', 'AFR'],
                ['HKA', 'MAD'],['M17', 'FW'],['FW', 'JT'],['AHQ', 'GREX'],
                ['JT', 'AFR'],['HKA', 'M17'],['AHQ', 'MAD'],['GREX', 'FW']]

#build up a 64*64 zero-matrix
score_array = np.zeros_like(np.arange(4096).reshape(64,64))

# We need to know which match the first index of WL_list represent,
# so that we can add the score in the right position on the score list
# Generally I pull the focus_team to the front of matches list with same order
def sort_match(matches_list, focus_team):
    for index in range(len(matches_list)):
        match = matches_list[index]
        position = index
        while position > 0 and focus_team in match and focus_team not in matches_list[position -1]:
            matches_list[position] = matches_list[position -1]
            position -= 1
        matches_list[position] = match
    
    for index in range(3): 
        match = matches_list[index]  
        if match[0] == focus_team:
            pass
        else:
            match[1] = match[0]
            match[0] = focus_team

focus_team = 'M17'
sort_match(matches_list, focus_team)

# This is the func to tell you the coordinate where the state 
# should put in on the picture
def get_index(i):
    y = i[0]*32 + i[2]*16 + i[4]*8 + i[6]*4 + i[8]*2 + i[10]*1
    x = i[1]*32 + i[3]*16 + i[5]*8 + i[7]*4 + i[9]*2 + i[11]*1
    return (x,y)

# We use this func to find win_team and lose_team
def find_win_lose(matches_index, scenario):
    win_side = scenario[matches_index]
    if win_side == 0:
        lose_side = 1
    else:
        lose_side = 0
    win_team = matches_list[matches_index][win_side]
    lose_team = matches_list[matches_index][lose_side]
    return win_team, lose_team

def tie_winner(tie_team, focus_team):
    if len(tie_team) == 1:
        return 0
    if len(tie_team) == 2:
        if matchup_table20[tie_team[0]][tie_team[1]][0] == 4 and tie_team[0] == focus_team:
            return 0
        elif matchup_table20[tie_team[0]][tie_team[1]][1] == 4 and tie_team[1]== focus_team:
            return 0
        elif matchup_table20[tie_team[0]][tie_team[1]][1] == 4 and tie_team[0] == focus_team:
            return -1
        elif matchup_table20[tie_team[0]][tie_team[1]][0] == 4 and tie_team[1] == focus_team:
            return -1
        elif matchup_table20[tie_team[0]][tie_team[1]][0] == 3 and matchup_table20[tie_team[0]][tie_team[1]][0] == 3:
            return 1
        elif matchup_table20[tie_team[0]][tie_team[1]][0] == 2 and matchup_table20[tie_team[0]][tie_team[1]][1] == 2:
            if matchup_table21[tie_team[0]][tie_team[1]][0] == 3 and tie_team[0] == focus_team :
                return 2
            elif matchup_table21[tie_team[0]][tie_team[1]][0] == 3 and tie_team[1] == focus_team :
                return 3
            elif matchup_table21[tie_team[1]][tie_team[0]][0] == 3 and tie_team[0] == focus_team :
                return 2
            elif matchup_table21[tie_team[1]][tie_team[0]][0] == 3 and tie_team[1] == focus_team :
                return 3
            else:
                return 1
        # 2-3 or 3-2 in 2-0 table
        elif matchup_table20[tie_team[0]][tie_team[1]][0] == 2 or matchup_table20[tie_team[0]][tie_team[1]][1] == 2:
            if matchup_table20[tie_team[0]][tie_team[1]][0] == 3 and tie_team[0] == focus_team :
                return 2
            elif matchup_table20[tie_team[0]][tie_team[1]][1] == 3 and tie_team[1] == focus_team :
                return 2
            elif matchup_table20[tie_team[0]][tie_team[1]][0] == 2 and tie_team[0] == focus_team :
                return 3
            elif matchup_table20[tie_team[0]][tie_team[1]][1] == 2 and tie_team[1] == focus_team :
                return 3

    if len(tie_team) == 3 or len(tie_team) == 4 or len(tie_team) == 5:
        twin = team_score_df.iloc[3].index.name
        if twin == focus_team:
            return 2
        else:
            return 3

bar.start()
# Now we start to calculate the WL condition and add it to score_table(BO3)
for scenario in scenario_list:
    # make a deepcopy of our list
    team_score_list_cp = copy.deepcopy(team_score_list)
    matchup_table20 = copy.deepcopy(matchup_table)
    matchup_table21 = copy.deepcopy(matchup_table)    

    for matches_index in range(12):
        win_team, lose_team = find_win_lose(matches_index, scenario)

        # Now add the score to the score list
        team_score_list_cp[win_team][0] += 1
        # Total win will add 2
        team_score_list_cp[win_team][2] += 2
        team_score_list_cp[win_team][4] += 2
        # This is the scenario that win team lose 1 game 
        team_score_list_cp[win_team][5] += 1

        # For lose team we do the same thing
        team_score_list_cp[lose_team][1] += 1
        team_score_list_cp[lose_team][3] += 2
        team_score_list_cp[lose_team][5] += 2
        team_score_list_cp[lose_team][4] += 1

        # We also need to update the matchup table
        matchup_table20[win_team][lose_team][0] +=2
        matchup_table20[lose_team][win_team][1] +=2        
        
        matchup_table21[win_team][lose_team][0] +=2
        matchup_table21[win_team][lose_team][1] +=1
        matchup_table21[lose_team][win_team][0] +=1
        matchup_table21[lose_team][win_team][1] +=2

    # We sent the score to dataframe to use rank function to get the team rank
    team_score_df = pd.DataFrame.from_dict(data = team_score_list_cp, orient ='index',
                                            columns = ['W','L','TW20','TL20','TW21','TL21'])
    team_score_df = team_score_df.sort_values(by=['W','TW20'], ascending=False)
    team_score_df['rank'] = team_score_df['W'].rank(axis=0, method='dense', ascending=False).astype(int)
    team_score_df['rank2'] = team_score_df['TW20'].rank(axis=0, method='dense', ascending=False).astype(int)

    # Now we find the 4th team and find if any team tie with 4th team
    last_rank = team_score_df.iloc[3]['rank']
    top4_team = team_score_df.iloc[:4].index.tolist()
    last4_team = team_score_df.iloc[4:].index.tolist()
    tie_team = team_score_df.loc[team_score_df['rank']==last_rank].index.tolist()

    if focus_team not in tie_team and focus_team in top4_team:
        state = 0
    elif focus_team in tie_team and (tie_team and last4_team) == None :
        state = 0
    elif focus_team in tie_team and (tie_team and last4_team) != None :
        state = tie_winner(tie_team, focus_team)
    else:
        state = -1

    coordinate = get_index(scenario)
    score_array[coordinate[0]][coordinate[1]] = state
    bar.update(scenario_list.index(scenario))
bar.finish()

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

colors = ['black',"medium green", "yellow", "light orange", "red", "dusty purple"]
sns.palplot(sns.xkcd_palette(colors))

f, ax= plt.subplots(figsize = (20,20))

hm = sns.heatmap(score_array, vmin = -1, vmax = 4, center=2,
                linewidths = 0.01, linecolor =('#d8dcd6'),
                cmap =sns.xkcd_palette(colors), cbar = False,
                xticklabels = False, yticklabels = False, robust=False)

plt.show(block=False)