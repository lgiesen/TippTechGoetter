# created with the support of Traversy Media's tutorial (https://www.youtube.com/watch?v=4UcqECQe5Kc)
import requests
#import BeautifulSoup for webscraping
from bs4 import BeautifulSoup
#import csv writer to be able to write our data to a CSV-file
from csv import writer

# get the website from the website
website = requests.get('https://www.forebet.com/en/football-tips-and-predictions-for-germany/Bundesliga')
# initialize BeautifulSoup with the website. Also let bs know that it needs to parse html
soup = BeautifulSoup(website.text, 'html.parser')

# create list with all the teams
matchDay = []
# first filter to the table with the class "schema tblen", then find the specific tr with class "tr_0"
# and find the name of the team in the span element where the attribute "itemprop" is set to "name"
teamsAsList = soup.find('table', {'class': "schema tblen"})\
    .find('tr', {"class": "tr_0"})\
    .find_all('span', attrs={"itemprop": "name"})
for team in teamsAsList:
    matchDay.append(team.get_text())

# open or create this csv file and w = write to it
with open('predictions.csv', 'w') as csv_file:
    #use the imported writer to write posts.csv as csv_file
    csv_writer = writer(csv_file)
    headers = ['HomeTeam', 'AwayTeam', 'Result']
    # write the headers
    csv_writer.writerow(headers)
    # write all the variables in each row

    ### Preditions
    # P = probability for home/draw/away-result
    probabilities = soup.find('table', {'class': "schema tblen"}) \
        .find('tr', {"class": "tr_0"}) \
        .find_all('td', {"class": ""})
    result = "" # specific game outcome
    allResults = [] # array with all outcomes
    counter = 1 # counter for making sure to only use the desired probabilities and not other info
    for probability in probabilities:
        # find the maximum probability and set the winner accordingly
        if ((probabilities[0].get_text() >= probabilities[1].get_text()) &
                (probabilities[0].get_text() >= probabilities[2].get_text())):
            result = "Home"
        elif ((probabilities[1].get_text() >= probabilities[0].get_text()) &
              (probabilities[1].get_text() >= probabilities[2].get_text())):
            result = "Draw"
        else:
            result = "Away"
        probabilities = probabilities[3:]
        allResults.append(result)

        # print(str(counter) + " " + result) # Print all results
        counter += 1
        if (counter >= 10): break

    ### Teams
    homeTeam = ""
    awayTeam = ""
    counter = 0
    for team in matchDay:
        ### Teams
        teamIndex = matchDay.index(team)
        # home team always is at at even index
        if (teamIndex % 2 == 0): homeTeam = team
        # whereas the away team always is positioned at an odd index
        else: awayTeam = team

        if( # check if home & away team are defined
            (homeTeam != "") & (awayTeam != "") &
            # and make sure that the teams do not get used twice because only one team is updated in each iteration
            (awayTeam != matchDay[teamIndex - 1]) & (homeTeam != matchDay[teamIndex - 2])):
            # write the data into the csv
            csv_writer.writerow([homeTeam, awayTeam, allResults[counter]])
            counter+=1
        # because we only want to have the predictions for next week, we filter out the predictions from last
        # matchday by saying we want to stop after we have got all 18 teams, who play on that matchday
        if (teamIndex >= 17): break


# soup.body.title
# or find('h3') [prints first elem] or findAll() [findAll('div)[indexORe.g.'href']]
# soup.find(id='idName') or class_='className'
# soup.select('idName')  --- returns a list so just add a [0] if needed
# soup.find(attrs={"attributE": "valuE"})
# print without html-tags:
# soup.find(id='idName').get_text()

# navigate
### soup.body.contents[1].contents[2].find_next_sibling().find_previous_sibling().find_next_sibling('p').find_parent()

# !!! get rid of linebreaks ('\n') by using .replace('\n', '')