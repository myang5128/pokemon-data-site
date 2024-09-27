import pandas as pd
import requests
import os
import re

#
# This grabs the Pokemon Name, ID, Capture Rate, Base Happiness, Egg Groups, Flavor Text, Growth Rate, Generation, Age Status
#

# preps a pokemon name for api searching
def linkReplacer(word):
    word = word.replace(".", "")
    return word.lower()

# preps a pokemon id for api searching
def strip_hash_and_leading_zeros(s):
    s = s.lstrip('#')
    s = s.lstrip('0')
    return s

def getPokemonEggGroups(eggList):
    eggOne = eggList[0]['name'] if eggList else None
    eggTwo = eggList[1]['name'] if len(eggList) > 1 else None
    return eggOne, eggTwo

def cleanFlavorText(text):
    text = text.replace('\x0c', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('"', '')
    return text

def getFlavorText(textList):
    flavors = {}
    
    for flavorEntry in textList:
        if flavorEntry['language']['name'] == 'en':
            text = cleanFlavorText(flavorEntry['flavor_text'])
            version = flavorEntry['version']['name']
            flavors[version] = text
            
    return flavors

# helper function for checking pokemon generation
def getGeneration(dex_id):
    if dex_id <= 151:
        return 'Generation I'
    elif dex_id <= 251:
        return 'Generation II'
    elif dex_id <= 386:
        return 'Generation III'
    elif dex_id <= 493:
        return 'Generation IV'
    elif dex_id <= 649:
        return 'Generation V'
    elif dex_id <= 721:
        return 'Generation VI'
    elif dex_id <= 809:
        return 'Generation VII'
    else:
        return 'Generation VIII'

def getJson(url):
    # sends an api request
    request = requests.get(url)
    status = request.status_code
    if status == 404:
        print(f"{url} did not work!")
        return None
    else:
        print(f"Doing {url} right now!")
    data = request.json()
    
    # grabs identifiers
    name = data['name']
    pokeID = data['id']
    
    # grabs generation
    generation = getGeneration(pokeID)
    
    # pulls in existing csv
    curFile = pd.read_csv(f'data/{generation}/{name}/stats.csv')
    
    curFile['Generation'] = generation
    
    # grabs base happiness
    baseHappiness = data['base_happiness']
    curFile['Base Happiness'] = baseHappiness
    
    # grabs capture rate
    captureRate = data['capture_rate']
    curFile['Capture Rate'] = captureRate
    
    # get age status
    isBaby = data['is_baby']
    isLegend = data['is_legendary']
    isMythical = data['is_mythical']
    curFile['Baby'] = isBaby
    curFile['Legendary'] = isLegend
    curFile['Mythical'] = isMythical
    
    # get growth rate
    growthRate = data['growth_rate']['name']
    curFile['Growth Rate'] = growthRate
    
    # grab egg groups
    eggOne, eggTwo = getPokemonEggGroups(data['egg_groups'])
    curFile['Egg Group One'] = eggOne
    curFile['Egg Group Two'] = eggTwo
    
    # resave file
    curFile.to_csv(f'data/{generation}/{name}/stats.csv', index=False)
    
    # grab flavor texts
    flavorDB = []
    flavor_texts = getFlavorText(data['flavor_text_entries'])
    for version, text in flavor_texts.items():
        flavorInfo = {
            "Game": version,
            "Flavor Text": text
        }
        flavorDB.append(flavorInfo)
    flavorDB = pd.DataFrame(flavorDB)
    #flavorDB['Flavor Text'] = flavorDB['Flavor Text'].apply(cleanFlavorText)
    flavorDB.to_csv(f"data/{generation}/{name}/flavortext.csv", index=False)
    
if __name__ == "__main__":
    pName = pd.read_csv("data/pokemonNameID.csv")
    
    for index, row in pName.iterrows():
        pokeID = strip_hash_and_leading_zeros(row['ID'])
        url = f"https://pokeapi.co/api/v2/pokemon-species/{pokeID}"
        getJson(url)
    