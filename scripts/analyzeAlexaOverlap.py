from pathlib import Path
import csv
import json
from prettytable import PrettyTable

class OverlapCalculator():
    def __init__(self):
        # Root directory
        self.rootDir = Path(__file__).parent.parent

        # URL for each of top 500 global Alexa sites
        self.globalURLs = {}

        # Maps countries to an array of their top 50 Alexa sites
        self.countryURLS = {}

        # Maps countries to their percentage overlap with the global 50
        self.countryOverlap = {}

    # Populates self.globalURLS and self.countryURLS
    def ingestData(self):
        self.globalURLs = self.getAlexa500Global()
        self.countryURLS = self.getAlexaTop50Countries()

    # Populates self.globalURLS from CSV
    def getAlexa500Global(self):
        globalURLS = set()
        csvPath = f"{self.rootDir}/data/alexaTop500SitesGlobal.csv"
        with open(csvPath, mode="r") as csvFile:
            csvReader = csv.reader(csvFile)
            header = True
            for row in csvReader:
                if header:
                    header = False
                    continue
                globalURLS.add(row[1])
        return globalURLS

    # Populates self.countryURLS from JSON
    def getAlexaTop50Countries(self):
        countryURLS = {}
        jsonPath = f"{self.rootDir}/data/alexaTop50SitesCountries.json"
        with open(jsonPath, mode="r") as jsonFile:
            jsonData = json.load(jsonFile)
        for country, sites in jsonData.items():
            URLS = []
            for site in sites:
                URLS.append(site['Site'])
            countryURLS[country] = URLS
        return countryURLS

    # Calculate the overlap between each country's top 50 and the global top 500
    def calculateOverlap(self):
        NUM_SITES_PER_COUNTRY = 50
        for country, sites in self.countryURLS.items():
            numOverlap = 0
            for site in sites:
                if site in self.globalURLs:
                    numOverlap += 1
            self.countryOverlap[country] = numOverlap / NUM_SITES_PER_COUNTRY

    # Print table of countries with their respective overlaps
    def printOverlap(self):
        table = PrettyTable(["Country", "Percentage Overlap"])

        # Sort from highest to lowest overlap
        sortedCountryOverlap = sorted(self.countryOverlap.items(),
                                      key=lambda kv: kv[1],
                                      reverse=True)

        for country, overlap in sortedCountryOverlap:
            overlapFormatted = f"{round(overlap * 100, 1)}%"
            table.add_row([country, overlapFormatted])

        print("ALEXA SITE OVERLAP BETWEEN COUNTRY TOP 50 and GLOBAL TOP 500")
        print(table)

def runProgram():
    overlapCalculator = OverlapCalculator()
    overlapCalculator.ingestData()
    overlapCalculator.calculateOverlap()
    overlapCalculator.printOverlap()

if __name__ == "__main__":
    runProgram()
