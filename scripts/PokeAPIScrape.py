import pandas as pd
import requests
import os

# preps a pokemon name for api searching
def linkReplacer(word):
    word = word.replace(".", "")
    return word.lower()

# preps a pokemon id for api searching
def strip_hash_and_leading_zeros(s):
    s = s.lstrip('#')
    s = s.lstrip('0')
    return s

# separates pokemon movesets into games
def separate_moves_by_game(moves_json):
    moves_by_game = {}
    
    for move_entry in moves_json:
        move_name = move_entry['move']['name']
        
        for version_detail in move_entry['version_group_details']:
            version_group_name = version_detail['version_group']['name']
            level_learned_at = version_detail['level_learned_at']
            
            if level_learned_at >= 1:
                if version_group_name not in moves_by_game:
                    moves_by_game[version_group_name] = []
                moves_by_game[version_group_name].append({"move": move_name, "level": level_learned_at})
    
    for game in moves_by_game:
        moves_by_game[game].sort(key=lambda x: x['level'])
        
    return moves_by_game

# grabs abilities
def get_abilities(abilities_list):
    non_hidden_abilities = [a['ability']['name'] for a in abilities_list if not a['is_hidden']]
    hidden_abilities = [a['ability']['name'] for a in abilities_list if a['is_hidden']]
    
    ability_one = non_hidden_abilities[0] if non_hidden_abilities else None
    ability_two = non_hidden_abilities[1] if len(non_hidden_abilities) > 1 else None
    hidden_ability = hidden_abilities[0] if hidden_abilities else None

    return ability_one, ability_two, hidden_ability

# helper function for checking pokemon generation
def get_generation(dex_id):
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
 
# grabs and saves images    
def get_images(url, filePath, shiny):
    img_data = requests.get(url).content
    if shiny:
        filePath = filePath + '/shiny.png'
    else:
        filePath = filePath + '/default.png'
    with open(filePath, 'wb') as saver:
        #print(f"Saving {url} to {filePath}")
        saver.write(img_data)
        
# calls api and looks at json
def getJson(link):
    # sends an api request
    request = requests.get(link)
    status = request.status_code
    if status == 404:
        print(f"{link} did not work!")
        return None
    else:
        print(f"Doing {link} right now!")
    data = request.json()
    
    # grabs pokemon identifiers
    name = data['species']['name']
    dexId = data['id']
    
    # grabs ability list
    fullAbilitiesList = data['abilities']
    abilityOne, abilityTwo, hiddenAbility = get_abilities(fullAbilitiesList)
    
    # grab type lists
    typeLists = data['types']
    primaryType = typeLists[0]['type']['name']
    secondaryType = typeLists[1]['type']['name'] if len(typeLists) > 1 else None

    # grab stat lists
    statLists = data['stats']
    hpStat = statLists[0]['base_stat']
    attackStat = statLists[1]['base_stat']
    defenseStat = statLists[2]['base_stat']
    specialAttackStat = statLists[3]['base_stat']
    specialDefenseStat = statLists[4]['base_stat']
    speedStat = statLists[5]['base_stat']
    
    # grab move lists
    fullMovesList = data['moves']
    levelList = separate_moves_by_game(fullMovesList)

    # finds pokemon generation
    generation = get_generation(dexId)
    
    # Create directory for generation
    os.makedirs(f"data/{generation}", exist_ok=True)
    
    # Create directory for pokemon inside generation
    os.makedirs(f"data/{generation}/{name}", exist_ok=True)
    os.makedirs(f"data/{generation}/{name}/movesets", exist_ok=True)
    
    # saves info as csv 
    pokemon_info = {
        "Name": name,
        "ID": dexId,
        "Ability One": abilityOne,
        "Ability Two": abilityTwo,
        "Hidden Ability": hiddenAbility,
        "Primary Type": primaryType,
        "Secondary Type": secondaryType,
        "HP": hpStat,
        "Attack": attackStat,
        "Defense": defenseStat,
        "SpAttack": specialAttackStat,
        "SpDefense": specialDefenseStat,
        "Speed": speedStat,
    }
    pokemonInfoDF = pd.DataFrame([pokemon_info])
    pokemonInfoDF.to_csv(f"data/{generation}/{name}/stats.csv", index=False)
    
    # saves move data as csv       
    for game, moves in levelList.items():
        pokeMovesDB = []
        for move in moves:
            move_info = {
                "Move": move['move'],
                "Level Learned At": move['level']
            }
            pokeMovesDB.append(move_info)
        pokeMovesDB = pd.DataFrame(pokeMovesDB)
        pokeMovesDB.to_csv(f"data/{generation}/{name}/movesets/{game}.csv", index=False)
    
    # saves pokemon image to file    
    pokeImage = data['sprites']['front_default']
    pokeImageShiny = data['sprites']['front_shiny']
    imgPath = f"data/{generation}/{name}"
    os.makedirs(imgPath, exist_ok = True)
    get_images(pokeImage, imgPath, False)
    get_images(pokeImageShiny, imgPath, True)
    
if __name__ == "__main__":
    pName = pd.read_csv("data/pokemonNameID.csv")
    
    for index, row in pName.iterrows():
        pokeID = strip_hash_and_leading_zeros(row['ID'])
        url = f"https://pokeapi.co/api/v2/pokemon/{pokeID}"
        getJson(url)
