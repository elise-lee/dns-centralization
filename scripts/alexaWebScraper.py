from bs4 import BeautifulSoup
import requests
import json
import time

# Scrapes Alexa site for Top 500 URLS for 115 countries
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
            time.sleep(2)
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
        return countrySites

def convertDictToJson(dict, jsonFileName):
    with open(jsonFileName, "w") as outfile:
        json.dump(dict, outfile, indent = 4)

def joinFiles():
    dict = {}
    files = [
        "alexaTop500SitesRegional0_10.json",
        "alexaTop500SitesRegional11_37.json",
        "alexaTop500SitesRegional.json"
    ]
    for f in files:
        with open(f, "r") as infile:
            f_dict = json.load(infile)
            dict.update(f_dict)
    convertDictToJson(dict, "alexaTop500SitesCountries.json")


def runProgram():
   # joinFiles()

   # Hardcodes cookies to scrape top 500 URLS for each country. Stops working after 20 countries.
   # Must hardcode your own cookies (after logging in)
   cookies = {
        "session_key": "gOc7EFh0%2Bctah5oMrngehl7ND2wdP8TkQArghbsJ01NETC%2F1L9%2Bjz5GT%2Fvc2qtf%2B5Jmt4TnHo0I8ONxw6kIxGDNLwnXrYv7NLUzY9i4eG1IDLO4XNw0hz3WdKp5hbg%2FubMM6jiM68Kpnx5r9zPmL%2BUdy97mAAbnukOS%2BGYGt3syZZIrceE5ksRZ70pO300RFwiOMQKrwqBVBOHTQWi%2FubCQaZInWu%2FJ31435NOCJGck%3D",
        "session_www_alexa_com": "479d7553-3253-4617-97ca-329042886b63",
        "jwtScribr": "eJyrViopVrIyNDM0MTM2MTc01DMzM9VRys0BihkY6CgVZ6YApZXMLU0tzMz1ElPKEvOSU1OUQBIlqSAZoCo9IDcZxleqBQBprxXg.iCgWlaFSdrNN02jEO0ISQIAz_zwKVQeDP1q8HZ7h2YI",
   }
   alexaScraper = AlexaScraper()
   alexaScraper.getAllCountries()
   convertDictToJson(alexaScraper.countryNames, 'countryCodesToNames.json')
   countryCodes = alexaScraper.countryNames.keys()
   for countryCode in list(countryCodes)[38:]:
       try:
           alexaScraper.countryURLS[countryCode] = alexaScraper.getTop500ForCountry(countryCode, cookies)
       except Exception as e:
           convertDictToJson(alexaScraper.countryURLS, "alexaTop500SitesRegional.json")
           print(e)
           return
   convertDictToJson(alexaScraper.countryURLS, "alexaTop500SitesRegional.json")



if __name__ == "__main__":
    runProgram()