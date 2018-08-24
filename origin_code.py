import pandas as pd
import numpy as np
import json
import itertools
import copy
from tqdm import tqdm

np.set_printoptions(threshold=np.inf)

board = list(itertools.product(range(2),repeat=12))
board = sorted(board)

matches = [ ['M17', 'JT'],
            ['M17', 'FW'],
            ['M17', 'HKA'],
            ['AFR', 'HKA'],
            ['GREX', 'MAD'],
            ['HKA', 'MAD'],
            ['AHQ','AFR'],
            ['FW', 'JT'],
            ['AHQ','GREX'],
            ['JT', 'AFR'],
            ['AHQ', 'MAD'],
            ['GREX', 'FW']
            ]

df = pd.DataFrame(data = board)
df.columns = ['FW vs M17', 'FW vs JT', 'FW vs GREX','AFR vs HKA', 'GREX vs MAD','JT vs M17', 'AHQ vs AFR', 'HKA vs MAD', 'AHQ vs GREX', 'JT vs AFR', 'HKA vs M17','AHQ vs MAD']

f = open('team.json', 'r')
team = json.load(f)

f2 = open('team1.json', 'r')
match_result = json.load(f2)

team_list = []
WL_list = []

for i in team:
    team_list.append(i)
    WL_list.append(team[i]['WL'])

score = dict(zip(team_list, WL_list))

match_tb = dict(match_result)

def sum_list(i):
    s = 0
    for e in i :
        s += e
    return s

def get_index(i):
    y = i[0]*32 + i[2]*16 + i[4]*8 + i[6]*4 + i[8]*2 + i[10]*1
    x = i[1]*32 + i[3]*16 + i[5]*8 + i[7]*4 + i[9]*2 + i[11]*1
    return (x,y)

array = np.arange(4096).reshape(64,64)


pbar = tqdm(total=4096,leave=False)

for k in range(4096):
    win_list= []
    lose_list = []

    for id in range(len(df.iloc[k].values)):
        win_team = matches[id][df.iloc[k].values[id]]
        win_list.append(win_team)
        if df.iloc[k].values[id] == 0:
            lose_team = matches[id][1]
        else:
            lose_team = matches[id][0]
        lose_list.append(lose_team)

    sub_score = copy.deepcopy(score)
    sub_match20_tb = copy.deepcopy(match_tb)
    sub_match21_tb = copy.deepcopy(match_tb)

    for win, lose in zip(win_list, lose_list):
        sub_score[win][0] = int(sub_score[win][0]) + 1
        sub_score[win][2] = int(sub_score[win][2]) + 2
        sub_score[win][4] = int(sub_score[win][4]) + 2
        # if win team lose 1 game
        sub_score[win][5] = int(sub_score[win][5]) + 1

        sub_score[lose][1] = int(sub_score[lose][1]) + 1
        sub_score[lose][4] = int(sub_score[lose][4]) + 1
        sub_score[lose][3] = int(sub_score[lose][3]) + 2
        sub_score[lose][5] = int(sub_score[lose][5]) + 2

        sub_match20_tb[lose][win][1] += 2
        sub_match20_tb[win][lose][0] += 2

        sub_match21_tb[lose][win][1] += 2
        sub_match21_tb[lose][win][0] += 1
        sub_match21_tb[win][lose][0] += 2
        sub_match21_tb[win][lose][1] += 1

    for team in sub_score:
        sub_score[team][1] = 14 - sub_score[team][0]

    win_df = pd.DataFrame.from_dict(data = sub_score, orient ='index',columns = ['Win', 'Lose','TWin','TLose','TWin1','TLose1'])
    win_df = win_df.sort_values(by =['Win','TWin'], ascending = False)
    win_df['rank'] = win_df['Win'].rank(axis =0, method = 'dense', ascending = False).astype(int)
    win_df['rank2'] = win_df['TWin'].rank(axis =0, method = 'dense', ascending = False).astype(int)
    match20_result_df = pd.DataFrame.from_dict(data = sub_match20_tb).T
    match21_result_df = pd.DataFrame.from_dict(data = sub_match21_tb).T

    #print('senario' +' '+ str(k+1) +':')
    #print('\r')
    #print('Winner: {}'.format(win_list))
    #print('\r')
    #print(win_df)
    #print('\r')
    #print(match20_result_df)
    #print('\r')
    #print(match21_result_df)


    f_team = 'M17'

    last_rank = win_df.iloc[3]['rank']
    top_team = win_df.iloc[:4].index.tolist()
    bad_team = win_df.iloc[4:].index.tolist()
    tie_team = win_df.loc[win_df['rank']==last_rank].index.tolist()

    bad_rank = win_df.iloc[7]['rank']
    last_tie_team = win_df.loc[win_df['rank']==bad_rank].index.tolist()


    def is_team(list1, list2):
        for i in list1:
            if i in list2:
                return True
            else:
                pass
        return False

    state_dict={
            -1: 'out',
            0: 'must in',
            1: 'must tie break',
            2: '一場都別輸',
            3: '贏一場還有希望'}

    def tie_winner(tie_team, f_team):
        if len(tie_team) == 2:
            if match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][0] == 4 and tie_team[0] == f_team:
                return 0

            elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][1] == 4 and tie_team[1]== f_team:
                return 0

            elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][1] == 4 and tie_team[0] == f_team:
                return -1

            elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][0] == 4 and tie_team[1] == f_team:
                return -1

            elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][0] == 3 and match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][1] == 3:
                return 1

            elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][0] == 2 and match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][1] == 2:

                if match21_result_df.iloc[match21_result_df.index == tie_team[0]][tie_team[1]][0][0] == 3 and tie_team[0] == f_team :
                    return 2
                elif match21_result_df.iloc[match21_result_df.index == tie_team[0]][tie_team[1]][0][0] == 3 and tie_team[1] == f_team :
                    return 3
                elif match21_result_df.iloc[match21_result_df.index == tie_team[1]][tie_team[0]][0][0] == 3 and tie_team[0] == f_team :
                    return 2
                elif match21_result_df.iloc[match21_result_df.index == tie_team[1]][tie_team[0]][0][0] == 3 and tie_team[1] == f_team :
                    return 3
                else:
                    return 1

            # 2-3 or 3-2 in 2-0 table
            elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][0] == 2 or match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][1] == 2:

                if match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][0] == 3 and tie_team[0] == f_team :
                    return 2
                elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][1] == 3 and tie_team[1] == f_team :
                    return 2
                elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][0] == 2 and tie_team[0] == f_team :
                    return 3
                elif match20_result_df.iloc[match20_result_df.index == tie_team[0]][tie_team[1]][0][1] == 2 and tie_team[1] == f_team :
                    return 3

        if len(tie_team) == 3 or len(tie_team) == 4 or len(tie_team) == 5:
            twin = win_df.iloc[3].index.name
            if twin == f_team:
                return 2
            else:
                return 3

    if f_team not in tie_team and f_team in top_team:
        state = 0
    elif f_team in tie_team and is_team(tie_team, bad_team) == False :
        state = 0
    elif f_team in tie_team and is_team(tie_team, bad_team) == True :
        state = tie_winner(tie_team, f_team)
    else:
        state = -1

    #print('\r')
    #print(state)
    #print('----------------------------------------------------------------------------------------')
    #print('\r')

    # put state into array

    index = get_index(df.iloc[k])
    array[index[0]][index[1]] = state
    pbar.update(1)

pbar.close()

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

colors = ['black',"medium green", "yellow", "light orange", "red", "dusty purple"]
sns.palplot(sns.xkcd_palette(colors))

f, ax= plt.subplots(figsize = (20,20))

hm = sns.heatmap(array, vmin = -1, vmax = 4, center=2,
                linewidths = 0.01, linecolor =('#d8dcd6'),
                cmap =sns.xkcd_palette(colors), cbar = False,
                xticklabels = False, yticklabels = False, robust=False)

plt.show(block=False)
