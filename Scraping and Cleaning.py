#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np


# In[2]:


import pandas as pd


# In[3]:


import matplotlib.pyplot as plt


# In[4]:


# import data & check head
results = pd.read_csv(r'Bundesliga_Results.csv')
results.head()


# In[5]:


# check botttom 20 rows (commented out)
# results[-20:]


# In[6]:


# create dataframe where half-time results are NaN (before season 1995-96) & check bottom 5 rows
results_nan = results[results.isna().any(axis=1)]
results_nan[-5:]


# In[7]:


# create dataframe without NaN values (starting season 1995-96)
# this is the dataframe used in the following analysis
r = results.dropna()


# In[8]:


# set half-time goals to integer (before: float) & print head 5 rows
r['HTHG'] = r['HTHG'].astype(int)
r['HTAG'] = r['HTAG'].astype(int)
r.head()


# In[9]:


# import data this season & check head
results2 = pd.read_csv(r'Ergebnisse 2019 bis Spieltag 17.csv', sep =';', decimal=",")
results3 = pd.read_csv(r'Spielergebnisse 2018-19.csv', sep =';', decimal=",")
results2.head()


# In[10]:


# create list of dates to adjust format
date_list = []
for date in results2['Date']:
    date_list.append(date.replace('.', '/'))
for date in results3['Date']:
    date_list.append(date.replace('.', '/'))


# In[11]:


#Add column 'Season' to results2 and results3

results3['Season'] = '2018-19'
results2['Season'] = '2019-20'


# In[12]:


results2


# In[13]:


# concatenate both df & reset index
r = pd.concat([r, results2, results3])
r.reset_index(inplace=True, drop=True)
r


# In[14]:


# create list with all seasons (1995-96 until 2018-19); sort in ascending order
allssn = list(set(r['Season']))
allssn.sort()


# In[15]:


# create dictionary with season as keys and list of teams in the season as value; check if list hass 18 teams
tms_dict = dict()
for ssn in allssn:
    tms = list(set(r[r['Season'] == ssn]['HomeTeam']))
    if len(tms) != 18: print('Not 18 teams')
    tms_dict.update({ssn:tms})


# In[16]:


tbl_dict = dict()

# loop through each season in tms_dict (gives list of teams for specific season)
for ssn, tms in tms_dict.items():

    # create temporary list for each variable
    tmp_pnts = list()
    tmp_games = list()
    tmp_win = list()
    tmp_draw = list()
    tmp_loose = list()
    tmp_goalsfor = list()
    tmp_goalsagainst = list()
    tmp_goaldifference = list()


    # loop through all teams in list tms_season x; set points & games variable to 0;
    for tm in tms:
        pnts = 0
        win = 0
        draw = 0
        loose = 0
        games = 0
        goalsfor = 0
        goalsagainst = 0
        goaldifference = 0

    # loop through all home/ away games and add 3/1 points to points variable for win/draw; add 1 to game variable
    # old: test = r[r['Season'] == '1995-96'][r['HomeTeam'] == 'Bayern Munich']['FTR']
        # old: for rslt in r95[r95['HomeTeam'] == tm]['FTR']:
        for rslt in r[r['Season'] == ssn][r['HomeTeam'] == tm]['FTR']:
            if rslt == 'H':
                pnts += 3
                win +=1
            elif rslt == 'D':
                pnts += 1
                draw += 1
            else:
                loose += 1
            games += 1
        for rslt in r[r['Season'] == ssn][r['AwayTeam'] == tm]['FTR']:
            if rslt == 'A':
                pnts += 3
                win += 1
            elif rslt == 'D':
                pnts += 1
                draw += 1
            else:
                loose += 1
            games += 1
        if ssn != '2018-19':
            if games != 34: print('Not 34 games!') # check for 34 games
        tmp_pnts.append(pnts) # append points to temporary list
        tmp_games.append(games) # append games to temporary list
        tmp_win.append(win) # append win to temporary list
        tmp_draw.append(draw) # append draw to temporary list
        tmp_loose.append(loose) # append loose to temporary list
    # print(tmp_list)

    # goals for and against
        for glsfh in r[r['Season'] == ssn][r['HomeTeam'] == tm]['FTHG']: goalsfor += glsfh
        for glsah in r[r['Season'] == ssn][r['HomeTeam'] == tm]['FTAG']: goalsagainst += glsah
        for glsfa in r[r['Season'] == ssn][r['AwayTeam'] == tm]['FTAG']: goalsfor += glsfa
        for glsaa in r[r['Season'] == ssn][r['AwayTeam'] == tm]['FTHG']: goalsagainst += glsaa
        goaldifference = goalsfor - goalsagainst

        tmp_goalsfor.append(goalsfor) # append goalsfor to temporary list
        tmp_goalsagainst.append(goalsagainst) # append goalsagainst to temporary list
        tmp_goaldifference.append(goaldifference) # append goaldifference to temporary list

    # create temporary dictionary for creation of pandas dataframe
    tmp_dict = {'Team':tms, 'Games':tmp_games, 'Win':tmp_win, 'Draw':tmp_draw,'Loose':tmp_loose, 'GoalsFor':tmp_goalsfor,
                'GoalsAgainst':tmp_goalsagainst, 'GoalDifference':tmp_goaldifference, 'Points':tmp_pnts,}
    # print(tmp_dict)

    # create dataframe, sort on points variable, reset index and start it at 1 (not 0)
    tbl = pd.DataFrame(data = tmp_dict,columns = 
                       ['Team', 'Games', 'Win', 'Draw', 'Loose','GoalsFor', 'GoalsAgainst', 'GoalDifference', 'Points'])
    tbl.sort_values(['Points'], inplace = True, ascending = False)
    tbl.reset_index(inplace=True, drop=True)
    tbl.index += 1
    tbl_dict.update({ssn:tbl})


# In[17]:


print(r


# In[19]:


tbl_dict['2019-20'] # or any other season


# In[21]:


# create list with all teams in alphabetic order
alltms = list(set(r['HomeTeam']))
alltms.sort()
alltms


# In[22]:


# create empty dictionary
pstns = dict()

# loop through all teams in list alltms; create temporary dictionary for position of team
for tm in alltms:
    tmp_pstn = dict()

# loop through all seasons for team; set pstn variable to position (from seasons table)
# or none for seasons not in Bundesliga; update temporary dict and use this to update pstns dictionary
    for ssn in allssn:
        try: pstn = tbl_dict[ssn][tbl_dict[ssn]['Team'] == tm].index.values.astype(int)[0]
        except: pstn = None
        tmp_pstn.update({ssn:pstn})
    pstns.update({tm:tmp_pstn})


# In[23]:


pstns['Bayern Munich'] # or any other team


# In[ ]:




