import json
import csv
import matplotlib.pyplot as plt
import os

class CaAnalyzer:
    def __init__(self):
        # Key: Country code:
        # Value:
        #   - Key: CA Name
        #   - Value: Frequency of CA
        self.countryCaMap = {}
        self.countryCodes = self.getCountryCodes()

    def getCountryCodes(self):
        with open("../data/nordAndAlexaCountryCodes.txt", "r") as infile:
            countryCodes = [x.rstrip() for x in infile.readlines()]
        return countryCodes

    def ingestCountryData(self):
        for countryCode in self.countryCodes:
            with open(f"../results/CA centralization/{countryCode}.json", "r") as infile:
                frequencies = json.load(infile)

                def combineCA(main, alias):
                    if alias in frequencies:
                        if main in frequencies:
                            frequencies[main] += frequencies[alias]
                        else:
                            frequencies[main] = frequencies[alias]
                        del frequencies[alias]

                combineCA("GlobalSign", "GlobalSign nv-sa")
                combineCA("GoDaddy.com, Inc.", "The Go Daddy Group, Inc.")

                self.countryCaMap[countryCode] = frequencies

    def getPopularPerCountry(self):
        with open("../results/CA centralization/popularCAPerCountry.csv", "w") as outfile:
            csvWriter = csv.writer(outfile, delimiter=",")
            for country, frequencies in self.countryCaMap.items():
                caName, caCount = max(frequencies.items(), key=lambda a: a[1])
                csvWriter.writerow([country, caName, caCount])

    def getNumInTop5(self):
        with open("../results/CA centralization/percentageInTop5.csv", "w") as outfile:
            csvWriter = csv.writer(outfile, delimiter=",")
            for country, frequencies in self.countryCaMap.items():
                sortedCas = [x[0] for x in sorted(frequencies.items(), key=lambda a: a[1], reverse=True)]
                top5 = sortedCas[:5]
                print(f"{country} {', '.join(top5)}")
                numInTop5 = 0
                for ca in top5:
                    if ca in frequencies:
                        numInTop5 += frequencies[ca]
                csvWriter.writerow([country, numInTop5])


    def rankCaByPopularity(self):
        allCa = {}
        for _, frequencies in self.countryCaMap.items():
            for ca, count in frequencies.items():
                if ca in allCa:
                    allCa[ca] += count
                else:
                    allCa[ca] = count

        sortedCa = sorted(allCa.items(), key=lambda a: a[1], reverse=True)
        sumCa = 16193 # Total number of third party CAs seen for all countries

        with open("../results/CA centralization/caRankedByPopularity.csv", "w") as outfile:
            csvWriter = csv.writer(outfile, delimiter=",")
            for ca, frequency in sortedCa:
                csvWriter.writerow([ca, frequency, frequency/sumCa])


def thirdPartyReliancePlotbyRegion():
    with open("../results/CA centralization/criticallyDependent.txt", "r") as infile:
        criticallyDependent = [float(x[:-2])*5 for x in infile.readlines()]

    for index, point in enumerate(criticallyDependent):
        if index <= 6:
            plt.plot(index, point, color='c', marker='.', label="America")
        elif index >= 7 and index <= 32:
            plt.plot(index, point, color='y', marker='.', label="Europe")
        elif index >= 33 and index <= 44:
            plt.plot(index, point, color='m', marker='.', label="Asia Pacific")
        elif index >= 45 and index <= 48:
            plt.plot(index, point, color='g', marker='.', label="Africa and Middle East")

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    # plt.legend()
    plt.title("CA Critical Dependency Across Regions")
    plt.xlabel('Countries')
    plt.ylabel('Count')
    plt.margins(0.02)
    # plt.axis([0, None, None, None])
    if not os.path.exists("graphs"):
        os.mkdir("graphs")
    # print ("graphs/lighthouseTTFB"+cdn+feature)

    plt.savefig("graphs/RegionCACriticalDependency")
    plt.clf()

def runProgram():
    thirdPartyReliancePlotbyRegion()
    # caAnalyzer = CaAnalyzer()
    # caAnalyzer.ingestCountryData()
    # caAnalyzer.getPopularPerCountry()
    # caAnalyzer.rankCaByPopularity()
    # caAnalyzer.getNumInTop5()

if __name__ == "__main__":
    runProgram()