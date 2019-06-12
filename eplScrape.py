import json
import re
import pandas as pd
from bs4 import BeautifulSoup as soup
import urllib.request as uReq
import requests
successful = 0
failed = 0
final_data = []
playerStatDict = {}
base_url = "https://footballapi.pulselive.com/football/players?pageSize=30&compSeasons=210&altIds=true&page={}&type=player&id=-1&compSeasonId=210"
request_header = {"Origin":"https://www.premierleague.com",'Referer':'https://www.premierleague.com/players'}
stats_URL = "https://www.premierleague.com/players/{}/{}/stats"
for i in range(0,31):
        print('-----PROCESSING FRAME {}------'.format(i))
        request = uReq.Request(base_url.format(i),headers=request_header)
        request = uReq.urlopen(request)
        #use requests over urllib
        #add time delay to avoid overloading the server with requests
        #webpage doesn't seem to deploy a rate limiter
        response = request.read()
        request.close()
        data = (json.loads(response))
        data = data['content']
        for d in data:
                playerName = d['name']['display']
                print('Processing {} data:'.format(playerName))
                Position = d['info']['position']
                Specialization = d['info']['positionInfo']
                if('country' in d['nationalTeam']):
                        playerCountry = d['nationalTeam']['country']
                else:
                        playerCountry = d['nationalTeam']['isoCode']
                if('currentTeam' in d.keys()):
                    playerClub = d['currentTeam']['club']['name']
                else:
                    playerClub = d['previousTeam']['club']['name']
                ageCalc = d['age'].split()
                if(len(ageCalc)>3):
                        playerAge = round((int(ageCalc[0]) + int(ageCalc[2])/365),2)
                else:
                        playerAge = round(int(ageCalc[0]))
                playerName_URL = playerName.encode("ascii",errors = "ignore")
                playerID_URL = int(d['id'])
                try:
                        stats_request = requests.get(stats_URL.format(playerID_URL,playerName_URL))
                        stats_soup = soup(stats_request.text, 'html.parser')
                        stats = stats_soup.find_all('span','stat')
                        stats
                        playerStatDict.update({'Name':playerName,'Age':playerAge, 'Country':playerCountry, 'Club':playerClub, 'Position':Position, 'Specialization':Specialization})
                        for x in stats:
                                playerStat = x.text
                                if('Successful 50/50s' in playerStat):
                                        playerStat = re.split('(?<=\d[a-zA-Z])\s(?=\d)',playerStat,1)
                                else:
                                        playerStat = re.split('\s(?=\d)',playerStat,1)
                                if(len(playerStat) == 2):
                                        playerStat[1] = playerStat[1].replace(',','')
                                        playerStat[1] = playerStat[1].replace('%','')
                                        playerStat[1] = float(playerStat[1])
                                        playerStat[0] = playerStat[0].strip() 
                                        playerStatDict.update({playerStat[0]:playerStat[1]})
                        final_data.append(playerStatDict.copy())
                        print('Successful !')
                        successful += 1
                except KeyboardInterrupt:
                        pass
print('Total successful players : {}'.format(successful))
print('Total failed players : {}'.format(failed))
final_data = pd.DataFrame(final_data)
final_data.to_csv('D:/EPL_Data.csv',index='False')