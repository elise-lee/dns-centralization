from pathlib import Path
import csv
import json
from prettytable import PrettyTable

class OverlapCalculator():
    def __init__(self):
        # Root directory
        self.rootDir = Path(__file__).parent.parent

        # URL for each of top 500 global Alexa sites
        self.globalURLs = []

        # Maps countries to an array of their top 50 Alexa sites
        self.countryURLS = {}

        # Maps countries to their percentage overlap with the global 50
        self.countryOverlap = {}

        # Maps country code to country name
        self.countryCodesToNames = {}

    # Populates self.globalURLS and self.countryURLS
    def ingestData(self):
        self.globalURLs = self.getAlexaGlobal()
        self.countryURLS = self.getAlexaCountries()
        self.countryCodesToNames = self.getCountryCodesToNames()

    # Populates self.globalURLS from CSV
    def getAlexaGlobal(self):
        globalURLS = []
        path = f"alexa_100k/websites_44699.txt"
        with open(path, mode="r") as globalFile:
            lines = globalFile.readlines()
            for line in lines:
                if "DataUrl" in line:
                    cleanLine = line.strip()
                    url = cleanLine.split('"')[3]
                    globalURLS.append(url)
        return globalURLS

    # Populates self.countryURLS from JSON
    def getAlexaCountries(self):
        countryURLS = {}
        jsonPath = f"{self.rootDir}/data/alexaTop500SitesCountries.json"
        with open(jsonPath, mode="r") as jsonFile:
            jsonData = json.load(jsonFile)
        for country, sites in jsonData.items():
            URLS = []
            for site in sites:
                URLS.append(site)
            countryURLS[country] = URLS
        return countryURLS

    def getCountryCodesToNames(self):
        countryCodesToNames = {}
        jsonPath = f"{self.rootDir}/data/countryCodesToNames.json"
        with open(jsonPath, mode="r") as jsonFile:
            jsonData = json.load(jsonFile)
        for code, name in jsonData.items():
            countryCodesToNames[code] = name
        return countryCodesToNames

    # Calculate the overlap between each country's sites and the global sites
    # Parameter numGlobalSites is the number of global sites we want to consider
    # when we calculate overlap, defaults to all
    def calculateOverlap(self, numGlobalSites=None):
        if not numGlobalSites or numGlobalSites > len(self.globalURLs):
            numGlobalSites = len(self.globalURLs)
        globalSites = self.globalURLs[:numGlobalSites]
        NUM_SITES_PER_COUNTRY = 500
        for country, sites in self.countryURLS.items():
            numOverlap = 0
            for site in sites:
                if site in globalSites:
                    numOverlap += 1
            self.countryOverlap[country] = numOverlap / NUM_SITES_PER_COUNTRY

    # Print table of countries with their respective overlaps
    def printOverlap(self):
        table = PrettyTable(["Country Name", "Country Code", "Percentage Overlap"])

        # Sort from highest to lowest overlap
        sortedCountryOverlap = sorted(self.countryOverlap.items(),
                                      key=lambda kv: kv[1],
                                      reverse=True)

        for countryCode, overlap in sortedCountryOverlap:
            overlapFormatted = f"{round(overlap * 100, 1)}%"
            countryName = self.countryCodesToNames[countryCode]
            table.add_row([countryName, countryCode, overlapFormatted])

        print("ALEXA SITE OVERLAP BETWEEN COUNTRY AND GLOBAL")
        print(table)

    # Exports overlap to a CSV file
    def exportOverlapToCSV(self, fileName="overlap.csv"):
        # Sort from highest to lowest overlap
        sortedCountryOverlap = sorted(self.countryOverlap.items(),
                                      key=lambda kv: kv[1],
                                      reverse=True)

        with open(fileName, mode="w") as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=",")
            for countryCode, overlap in sortedCountryOverlap:
                overlapFormatted = f"{round(overlap * 100, 1)}%"
                countryName = self.countryCodesToNames[countryCode]
                csvWriter.writerow([countryName, countryCode, overlapFormatted])



def runProgram():
    overlapCalculator = OverlapCalculator()
    overlapCalculator.ingestData()
    for slice in [20000, 40000]:
        overlapCalculator.calculateOverlap(slice)
        overlapCalculator.exportOverlapToCSV(f"alexaOverlap{slice}Global.csv")

if __name__ == "__main__":
    runProgram()
