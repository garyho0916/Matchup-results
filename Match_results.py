#%%
import pandas as np
import numpy as np
import itertools
import copy
#%%
# At First we create all the w-l condition as 0,1 by itertools
WL_list = list(itertools.product((0,1), repeat=12))

# The 8 teams in LMS and their score 
# (we don't need team.json and team1.json anymore)
Team_score_list = {'FW':[11,0,22,2,22,2]
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

# This is the func to tell you the coordinate where the state 
# should put in on the picture
def get_index(i):
    y = i[0]*32 + i[2]*16 + i[4]*8 + i[6]*4 + i[8]*2 + i[10]*1
    x = i[1]*32 + i[3]*16 + i[5]*8 + i[7]*4 + i[9]*2 + i[11]*1
    return (x,y)

# We need to know which match the first index of WL_list represent,
# so that we can add the score in the right position on the score list
# Generally I pull the focus_team to the front of matches list with same order
#def sort_match(matches_list, focus_team):
#    for index in range(len(matches_list)):
#        for team in matches_list[index]:
#            pass
                