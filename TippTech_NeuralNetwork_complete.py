#!/usr/bin/env python
# coding: utf-8

# In[1]:


## installation of tensorflow pip of anaconda
# !pip install tensorflow
# !conda install tensorflow


# In[2]:


# import libraries
import numpy as np
import pandas as pd
import tensorflow as tf
import re


# In[3]:


# import data (adjust file paths to local file paths)
results1 = pd.read_csv(r'C:\Users\Simon\Desktop\Bundesliga_Results.csv')
results2 = pd.read_csv(r'C:\Users\Simon\Desktop\Spielergebnisse 2018-19.csv', sep=';')
results3 = pd.read_csv(r'C:\Users\Simon\Desktop\Ergebnisse 2019 bis Spieltag 17.csv', sep=';')


# In[4]:


# lists with relevant data to create Dataframe
# row 5202 of results1 corresponds to first match of season 2010-11; for more data choose lower index
dates_temp = list(results1[5202:]['Date']) + list(results2['Date']) + list(results3['Date'])
hometeams_temp = list(results1[5202:]['HomeTeam']) + list(results2['HomeTeam']) + list(results3['HomeTeam'])
awayteams_temp = list(results1[5202:]['AwayTeam']) + list(results2['AwayTeam']) + list(results3['AwayTeam'])
FTRs_temp = list(results1[5202:]['FTR']) + list(results2['FTR']) + list(results3['FullTimeResult'])


# In[5]:


# create dataframe with match data
r = pd.DataFrame()
r['Date'] = dates_temp
r['HomeTeam'] = hometeams_temp
r['AwayTeam'] = awayteams_temp
r['FTR'] = FTRs_temp
r


# In[6]:


data = r[918:] ## row 918 is start of season 2013-14 so three previous seasons are in dataset for match history 
HTpnts_lst = [] # creating empty lists
ATpnts_lst = []
H_lst = []
D_lst = []
A_lst = []
lb1 = 10  ## look back at the 'lb1' - last matches of the home team and the away team (to calculate points from these)  
lb2 = 3  ## look back at 'lb2' - last matches in match history of exact same match (i.e. home team and away team the same)


for ind in data.index.tolist():
    ht = data.loc[ind]['HomeTeam']
    at = data.loc[ind]['AwayTeam']

    # calc points from last matches of home team and away team
    
    home_matches_HT = r[:ind][r['HomeTeam']==ht] # dataframe of all home matches of hometeam before current match
    away_matches_HT = r[:ind][r['AwayTeam']==ht] # dataframe of all away matches of hometeam before current match
    
    df = pd.concat([home_matches_HT, away_matches_HT]) # concatenate home and away matches, sort and choose last 10 (lb1) matches 
    df = df.sort_index()
    df.reset_index(inplace=True, drop=True)
    df = df[-lb1:]
    
    # calc points from last 10 matches and append to list
    HTpnts = ((df[df['HomeTeam']==ht]['FTR'].values == 'H').sum() * 3 +
        (df[df['HomeTeam']==ht]['FTR'].values == 'D').sum() * 1 +
        (df[df['AwayTeam']==ht]['FTR'].values == 'A').sum() * 3 +
        (df[df['AwayTeam']==ht]['FTR'].values == 'D').sum() * 1)
    HTpnts_lst.append(HTpnts)
    
    
    # same as above but for away team instead of home team
    home_matches_AT = r[:ind][r['HomeTeam']==at]
    away_matches_AT = r[:ind][r['AwayTeam']==at]
    df = pd.concat([home_matches_AT, away_matches_AT])
    df = df.sort_index()
    df.reset_index(inplace=True, drop=True)
    df = df[-lb1:]
    ATpnts = ((df[df['HomeTeam']==at]['FTR'].values == 'H').sum() * 3 +
        (df[df['HomeTeam']==at]['FTR'].values == 'D').sum() * 1 +
        (df[df['AwayTeam']==at]['FTR'].values == 'A').sum() * 3 +
        (df[df['AwayTeam']==at]['FTR'].values == 'D').sum() * 1)
    ATpnts_lst.append(ATpnts)

    
    # count outcomes in match history of exact same match (i.e. home team and away team the same)
    
    H = (r[:ind][r['HomeTeam']==ht][r['AwayTeam']==at]['FTR'].values[-lb2:] == 'H').sum()
    D = (r[:ind][r['HomeTeam']==ht][r['AwayTeam']==at]['FTR'].values[-lb2:] == 'D').sum()
    A = (r[:ind][r['HomeTeam']==ht][r['AwayTeam']==at]['FTR'].values[-lb2:] == 'A').sum()

    H_lst.append(H)
    D_lst.append(D)
    A_lst.append(A)


# add columns to dataframe
data['HTpnts'] = HTpnts_lst
data['ATpnts'] = ATpnts_lst
data['H'] = H_lst
data['D'] = D_lst
data['A'] = A_lst
data.reset_index(inplace=True, drop=True)
data


# In[8]:


# set up model

feature_columns = [
    tf.feature_column.numeric_column(key='HTpnts'),
    tf.feature_column.numeric_column(key='ATpnts'),
    tf.feature_column.numeric_column(key='H'),
    tf.feature_column.numeric_column(key='D'),
    tf.feature_column.numeric_column(key='A'),
]

model = tf.estimator.DNNClassifier(
  model_dir='model_new/',
  hidden_units=[10],
  feature_columns=feature_columns,
  n_classes=3,
  label_vocabulary=['H', 'D', 'A'],
  optimizer=tf.train.ProximalAdagradOptimizer(
    learning_rate=0.1,
    l1_regularization_strength=0.001
  ))


# In[9]:


# split data into training (90%) and test data
train_data = data[:round(len(data)*0.9)]
test_data = data[round(len(data)*0.9):]


# In[10]:


# set up training and test input
# training
train_features = {
    'HTpnts': np.array(train_data['HTpnts']),
    'ATpnts': np.array(train_data['ATpnts']),
    'H': np.array(train_data['H']),
    'D': np.array(train_data['D']),
    'A': np.array(train_data['A']),
}

train_labels = np.array(train_data['FTR'])

train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x=train_features,
    y=train_labels,
    batch_size=500,
    num_epochs=None,
    shuffle=True
)

#test
test_features = {
    'HTpnts': np.array(test_data['HTpnts']),
    'ATpnts': np.array(test_data['ATpnts']),
    'H': np.array(test_data['H']),
    'D': np.array(test_data['D']),
    'A': np.array(test_data['A']),
}

test_labels = np.array(test_data['FTR'])

test_input_fn = tf.estimator.inputs.numpy_input_fn(
    x=test_features,
    y=test_labels,
    batch_size=500,
    num_epochs=None,
    shuffle=True
)


# In[75]:


## train model (only first time code is executed or to improve model performance)
## subsequently, model will be restored automatically from latest version in directory ('model_new/')
# model.train(input_fn=train_input_fn, steps=1000)


# In[76]:


# evaluation of model: increase number of steps to get more accurate evaluation, but execution time increases as well
# evaluation = model.evaluate(input_fn=test_input_fn, steps=200)
# evaluation


# In[13]:


# construct list of all teams
tms_list = list(set(data['HomeTeam']))
tms_list.sort()


# In[35]:


# Manually enter matches we want to predict 

print('Enter matches in format "HomeTeam vs. AwayTeam" followed by ENTER; Enter "Predict" to predict outcomes')
print()
print('Team names:', tms_list)
print()

HT_predict_lst = []
AT_predict_lst = []
matches_predict_lst = []

while True:
    string = input()
    if string == 'Predict':
        break
    elif len(re.findall('(.*\svs.\s.*)', string)) == 0:
        print('Please enter match in format "HomeTeam vs. AwayTeam"!')
    else:
        HomeTeam = re.findall('(.*)\svs..*', string)[0]
        AwayTeam = re.findall('.*vs.\s(.*)', string)[0]
        
        if HomeTeam not in tms_list:
            print('Please check spelling of HomeTeam in team list')
        elif AwayTeam not in tms_list:
            print('Please check spelling of AwayTeam in team list')
        else:
            HT_predict_lst.append(HomeTeam)
            AT_predict_lst.append(AwayTeam)
            matches_predict_lst.append([HomeTeam, AwayTeam])


# In[36]:


#same code as above to construct features for matches to predict

HTpnts_lst = []
ATpnts_lst = []
H_lst = []
D_lst = []
A_lst = []

for ht in HT_predict_lst:
    home_matches_HT = r[r['HomeTeam']==ht] # dataframe of all home matches of hometeam before current match
    away_matches_HT = r[r['AwayTeam']==ht] # dataframe of all away matches of hometeam before current match
    
    df = pd.concat([home_matches_HT, away_matches_HT]) # concatenate home and away matches, sort and choose last 10 (lb1) matches 
    df = df.sort_index()
    df.reset_index(inplace=True, drop=True)
    df = df[-lb1:]
    
    # calc points from last 10 matches and append to list
    HTpnts = ((df[df['HomeTeam']==ht]['FTR'].values == 'H').sum() * 3 +
        (df[df['HomeTeam']==ht]['FTR'].values == 'D').sum() * 1 +
        (df[df['AwayTeam']==ht]['FTR'].values == 'A').sum() * 3 +
        (df[df['AwayTeam']==ht]['FTR'].values == 'D').sum() * 1)
    HTpnts_lst.append(HTpnts)

# same for awayteam    
for at in AT_predict_lst:
    home_matches_AT = r[r['HomeTeam']==at]
    away_matches_AT = r[r['AwayTeam']==at]
    df = pd.concat([home_matches_AT, away_matches_AT])
    df = df.sort_index()
    df.reset_index(inplace=True, drop=True)
    df = df[-lb1:]
    ATpnts = ((df[df['HomeTeam']==at]['FTR'].values == 'H').sum() * 3 +
        (df[df['HomeTeam']==at]['FTR'].values == 'D').sum() * 1 +
        (df[df['AwayTeam']==at]['FTR'].values == 'A').sum() * 3 +
        (df[df['AwayTeam']==at]['FTR'].values == 'D').sum() * 1)
    ATpnts_lst.append(ATpnts)

# match history
for match in matches_predict_lst:
    ht = match[0]
    at = match[1]
    H = (r[r['HomeTeam']==ht][r['AwayTeam']==at]['FTR'].values[-lb2:] == 'H').sum()
    D = (r[r['HomeTeam']==ht][r['AwayTeam']==at]['FTR'].values[-lb2:] == 'D').sum()
    A = (r[r['HomeTeam']==ht][r['AwayTeam']==at]['FTR'].values[-lb2:] == 'A').sum()

    H_lst.append(H)
    D_lst.append(D)
    A_lst.append(A)


# In[37]:


# construct dataframe out of matches to predict and features
matches_topredict = pd.DataFrame()
matches_topredict['HomeTeam'] = HT_predict_lst
matches_topredict['AwayTeam'] = AT_predict_lst
matches_topredict['HTpnts'] = HTpnts_lst
matches_topredict['ATpnts'] = ATpnts_lst
matches_topredict['H'] = H_lst
matches_topredict['D'] = D_lst
matches_topredict['A'] = A_lst
matches_topredict


# In[38]:


# input for neural network
pred_features = {
    'HTpnts': np.array(matches_topredict['HTpnts']),
    'ATpnts': np.array(matches_topredict['ATpnts']),
    'H': np.array(matches_topredict['H']),
    'D': np.array(matches_topredict['D']),
    'A': np.array(matches_topredict['A']),
}

pred_input_fn = tf.estimator.inputs.numpy_input_fn(
    x=pred_features,
    num_epochs=1,
    shuffle=False
)


# In[52]:


# predict and store predictions
prediction = model.predict(input_fn=pred_input_fn)
results = list(prediction)


# In[71]:


# add probabilities and predictions to dataframe

prob_lst = []
pred_lst = []

for match in results:
    prob_lst.append(match['probabilities'].round(decimals=4))
    pred_lst.append(str(match['classes'])[3])
    
matches_topredict['Probabilities'] = prob_lst
matches_topredict['Prediction'] = pred_lst
matches_topredict


# In[ ]:




