import requests
# import BeautifulSoup for webscraping
from bs4 import BeautifulSoup
# import csv writer to be able to write our data to a CSV-file
from csv import writer
# ------------------------------------------- forebet -------------------------------------------

# get the website from the website
forebet = requests.get('https://www.forebet.com/en/football-tips-and-predictions-for-germany/Bundesliga')
# initialize BeautifulSoup with the website. Also let bs know that it needs to parse html
fb = BeautifulSoup(forebet.text, 'html.parser')
# -------------------- Teams in match order --------------------
# create list with all the teams
matchDay = []
# first filter to the table with the class "schema tblen", then find the specific tr with class "tr_0"
# and find the name of the team in the span element where the attribute "itemprop" is set to "name"
teamsAsList = fb.find('table', {'class': "schema tblen"}) \
    .find('tr', {"class": "tr_0"}) \
    .find_all('span', attrs={"itemprop": "name"})
for team in teamsAsList:
    matchDay.append(team.get_text())
# -------------------- Prediction forebet --------------------
# P = probability for home/draw/away-result
forebetPrediction = fb.find('table', {'class': "schema tblen"}) \
    .find('tr', {"class": "tr_0"}) \
    .find_all('td', {"class": ""})
forebetPrediction = forebetPrediction[:27]
result = ""  # specific game outcome
allResults = []  # array with all outcomes
counter = 1  # counter for making sure to only use the desired probabilities and not other info
# convert all html tags (<td><b>57</b></td>) to int (57)
for probability in forebetPrediction:
    index = forebetPrediction.index(probability)
    forebetPrediction[index] = int(forebetPrediction[index].get_text())

# ------------------------------------------- kickform -------------------------------------------
# -------------------- Prediction kickform --------------------

kickform = requests.get('https://www.kickform.de/')
# initialize BeautifulSoup with the website. Also let bs know that it needs to parse html
kf = BeautifulSoup(kickform.text, 'html.parser')

# Predictions forebet
# P = probability for home/draw/away-result
kickformPrediction = kf.find_all('div', {"class": "prognose-balken"})
for probability in kickformPrediction:
    index = kickformPrediction.index(probability)
    kickformPrediction[index] = int(kickformPrediction[index].get_text().replace("%", ""))
# too many predictions -> reduce/slice down to the ones we need for this matchday
kickformPrediction = kickformPrediction[:27]

# get the mean of both lists
probabilities = [(g + h) / 2 for g, h in zip(forebetPrediction, kickformPrediction)]

# check what is the maximum probability
for probability in probabilities:
    # find the maximum probability and set the winner accordingly
    if ((probabilities[0] >= probabilities[1]) &
            (probabilities[0] >= probabilities[2])):
        result = "Home"
    elif ((probabilities[1] >= probabilities[0]) &
          (probabilities[1] >= probabilities[2])):
        result = "Draw"
    else:
        result = "Away"
    # take away the first three possibilities because we already evaluated them for this match
    probabilities = probabilities[3:]
    # add the result to allResults
    allResults.append(result)

    # print(str(counter) + " " + result) # Print all results
    counter += 1
    if counter >= 10:
        break

# -------------------- write to CSV --------------------
# open or create this csv file and w = write to it
with open('predictions.csv', 'w') as csv_file:
    # use the imported writer to write posts.csv as csv_file
    csv_writer = writer(csv_file)
    headers = ['HomeTeam', 'AwayTeam', 'Result']
    # write the headers
    csv_writer.writerow(headers)

    # Teams
    homeTeam = ""
    awayTeam = ""
    counter = 0
    for team in matchDay:
        teamIndex = matchDay.index(team)
        # home team always is at at even index
        if teamIndex % 2 == 0:
            homeTeam = team
        # whereas the away team always is positioned at an odd index
        else:
            awayTeam = team

        if (  # check if home & away team are defined
                (homeTeam != "") & (awayTeam != "") &
                # and make sure that the teams do not get used twice because only one team is updated in each iteration
                (awayTeam != matchDay[teamIndex - 1]) & (homeTeam != matchDay[teamIndex - 2])):
            # write the data into the csv
            csv_writer.writerow([homeTeam, awayTeam, allResults[counter]])
            counter += 1
        # because we only want to have the predictions for next week, we filter out the predictions from last
        # match day by saying we want to stop after we have got all 18 teams, who play on that match day
        if teamIndex >= 17:
            break

# soup.body.title
# or find('h3') [prints first elem] or findAll() [findAll('div)[indexORe.g.'href']]
# soup.find(id='idName') or class_='className'
# soup.select('idName')  --- returns a list so just add a [0] if needed
# soup.find(attrs={"attributE": "valuE"})
# print without html-tags:
# soup.find(id='idName').get_text()

# navigate
# !! soup.body.contents[1].contents[2].find_next_sibling().find_previous_sibling().find_next_sibling('p').find_parent()

# !! get rid of linebreaks ('\n') by using .replace('\n', '')
