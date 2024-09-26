from bs4 import BeautifulSoup
import requests
import pandas as pd

# initial database
pokeDB = []

# helper function to strip text
def replacer(word):
    word = word.replace("\r", "")
    word = word.replace("\n", "")
    word = word.replace("\t", "")
    return word

# scraper function
def scrape(link):
    
    # temporary storage
    pokeIDdb = []
    pokeNamesdb = []
    
    # grab link
    url = link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # grabs pokemon number
    pokeIDs = soup.select(".fooinfo:nth-child(1)")
    for pokeID in pokeIDs:
        pokeIDdb.append(replacer(pokeID.text))
        
    # grabs pokemon name
    pokeNames = soup.select(".fooinfo:nth-child(3)")
    for pokeName in pokeNames:
        pokeNamesdb.append(replacer(pokeName.text))
    
    # combines the two lists together
    zipped = list(zip(pokeIDdb, pokeNamesdb))
    for item in zipped:
        pokeDB.append({"ID": item[0], "Name": item[1]})
    
    
if __name__ == "__main__":
    
    # scrapes through all the generations
    for n in range(1, 10):
        baseURL = f"https://www.serebii.net/pokemon/gen{n}pokemon.shtml"
        print(f"Scraping {baseURL} now!")
        scrape(baseURL)
    
    # converts to dataframe and into a csv file
    pokeDF = pd.DataFrame(pokeDB)
    pokeDF.to_csv('data/pNameID.csv', index=False)
    
    

 
