from bs4 import BeautifulSoup
import requests
import json

# Scrapes Alexa site for Top 500 URLS from 20 out of 123 countries
class AlexaScraper():
    def __init__(self):
        self.baseURL = "https://www.alexa.com/topsites/"

        # Maps country code to country name
        # (ex, KEY: AF, VALUE: Afghanistan)
        self.countryNames = {}

        # Maps country code to list of top 500 urls
        # (ex, KEY: AF, VALUE: [www.google.com, ...])
        self.countryURLS = {}

    # Populates dictionary of all countries + the path to the
    # country data after the base URL from Alexa index page
    def getAllCountries(self):
        page = requests.get(self.baseURL + "countries")
        soup = BeautifulSoup(page.content, "html.parser")
        columns = soup.find_all("ul", class_="countries span3")
        for col in columns:
            countryLinks = col.find_all("a")
            for link in countryLinks:
                countryName = link.get_text()
                countryCode = link["href"].split("/")[1]
                self.countryNames[countryCode] = countryName

    # Given a county code, returns the 500 top sites for that country
    def getTop500ForCountry(self, countryCode, cookies):
        countrySites = []
        for pageNum in range(20):
            URL = f"{self.baseURL}countries;{pageNum}/{countryCode}"
            page = requests.get(
                f"{self.baseURL}countries;{pageNum}/{countryCode}",
                cookies = cookies)
            soup = BeautifulSoup(page.content, "html.parser")
            siteCells = soup.find_all("div", class_="td DescriptionCell")
            for siteCell in siteCells:
                site = siteCell.find_all("a")[0].get_text().lower()
                if site not in countrySites:
                    countrySites.append(site)
                    print(site)
                else:
                    print("DUPE")

def convertDictToJson(dict, jsonFileName):
    with open(jsonFileName, "w") as outfile:
        json.dump(dict, outfile, indent = 4)

def convertRawScrapedDataToDict():
    countryURLDict = {}

    with open("../data/countryCodesToNames.json", "r") as infile:
        countryCodesDict = json.load(infile)

    fileObj = open("../data/rawScrapedAlexaData_AfghanistanToCameroon.json", "r")
    URLS = fileObj.read().splitlines()  # puts the file into an array
    fileObj.close()

    for idx, countryCode in enumerate(list(countryCodesDict.keys())):
        offset = idx * 500
        if offset + 500 <= len(URLS):
            countryURLDict[countryCode] = URLS[offset:offset + 500]
        else:
            break

    return countryURLDict

def runProgram():
   # Hardcodes cookies to scrape top 500 URLS for each country. Stops working after 20 countries.
   # Must hardcode your own cookies (after logging in)
   cookies = {
       "attr_first": "%7B%22source%22%3A%22(direct)%22%2C%22medium%22%3A%22(none)%22%2C%22campaign%22%3A%22(not%20set)%22%2C%22term%22%3A%22(not%20provided)%22%2C%22content%22%3A%22(not%20set)%22%2C%22lp%22%3A%22www.alexa.com%2Ftopsites%2Fglobal%3B5%22%2C%22date%22%3A%222021-02-9%22%2C%22timestamp%22%3A1612916553026%7D",
       "session_key": "0feIaZWxtZQ%2BUPG%2FLH48WTfEXkyiNdff68YJjFLsJx57XlwjJgPhE%2BLLGxNl51nRfsEtwJ5ckJkxTuP1B%2BYeWdJZ49thPNSAsdS27ZyvpH9ni4OgiyXjchB4QiBQCbtIF7wEZPca0UlFNU16D8KGcu32l7SjUrOrJkTHiesjmzJLgDhrBsFAqXzpEANoM5qXla43ficU%2BZfQ7Sb2ErLdtPYMiLBimMRiWKK48jufASg%3D",
        "_gat_UA-2146411-12": "1",
       "session_www_alexa_com": "479d7553-3253-4617-97ca-329042886b63",
       "session_www_alexa_com_daily": "1614387595",
       "jwtScribr": "eJyrViopVrIyNDM0MTE1sTAw0bMw0VHKzQEKGRjoKBVnpgBllcwtTS3MzPUSU8oS85JTU5RAEiWpIBmgKj0gNxnGV6oFAFjuFa4%3D.LFmALFWNfVueJqlS5lvFe_HboWOyc1GWDpUX14WdDJQ",
   }
   alexaScraper = AlexaScraper()
   alexaScraper.getAllCountries()
   convertDictToJson(alexaScraper.countryNames, 'countryCodesToNames.json')
   countryCodes = alexaScraper.countryNames.keys()
   for countryCode in countryCodes[:20]:
       alexaScraper.countryURLS[countryCode] = alexaScraper.getTop500ForCountry(countryCode, cookies)
   convertDictToJson(alexaScraper.countryURLS, "alexaTop500Sites_AfghanistanToCameroon.json")

  # #  Used to convert some raw scraped data into a JSON of country codes to URLS after Amazon blocked us
  #  countryURLDict = convertRawScrapedDataToDict()
  #  convertDictToJson(countryURLDict, "alexaTop500Sites_AfghanistanToCameroon.json")

if __name__ == "__main__":
    runProgram()