import subprocess
from pathlib import Path
import json
import tldextract
import dns.resolver
import time

class CAFinder:
    def __init__(self):
        # Populates map of CA to CA URL
        self.caMap = self.getCaMap()

        self.count = 0
        self.OCSP = 0

        # Initialize the following dictionary, populated during getCAType,
        # to be used for seeing which are most popular CAs for each country
        # - KEY: CountryCode
        # - VALUE: DICT:
        #     - KEY: Name of certificate authority,
        #     - VALUE: Count of websites with that certificate authority
        self.caCountByCountry = {}

    # Given a website, returns the type of the CA (unknown, private, or third-party)
    # 𝑐𝑎 ← 𝑔𝑒𝑡𝐶𝐴(𝑤)
    # 𝑐𝑎_𝑢𝑟𝑙 ← 𝑔𝑒𝑡𝐶𝐴_𝑈𝑅𝐿(𝑐𝑎,𝑤)
    # c𝑎.𝑡𝑦𝑝𝑒 ← 𝑢𝑛𝑘𝑛𝑜𝑤𝑛
    # if 𝑡𝑙𝑑(𝑐𝑎_𝑢𝑟𝑙) = 𝑡𝑙𝑑(𝑤) then
    #   𝑐𝑎.𝑡𝑦𝑝𝑒 ← 𝑝𝑟𝑖𝑣𝑎𝑡𝑒
    # elseif 𝑖𝑠𝐻𝑇𝑇𝑃𝑆(𝑤) & 𝑡𝑙𝑑(𝑐𝑎_𝑢𝑟𝑙) ∈ 𝑆𝐴𝑁(𝑤) then
    #   𝑐𝑎.𝑡𝑦𝑝𝑒 ← 𝑝𝑟𝑖𝑣𝑎𝑡𝑒
    # else if 𝑆𝑂𝐴(𝑐𝑎_𝑢𝑟𝑙) ≠ 𝑆𝑂𝐴(𝑤) then
    #   𝑐𝑎.𝑡𝑦𝑝𝑒 ← 𝑡h𝑖𝑟𝑑
    # end if
    def getCAType(self, website, countryCode=None, debug=False):
        self.count = self.count + 1

        CA, OCSP = self.getCA(website)
        if CA:
          CA_URL = self.getCA_URL(CA)
        else:
            if debug: print(f"{self.count}. {website}, returning early, type: HTTP")
            return "http"

        if OCSP:
            self.OCSP = self.OCSP + 1

        # Return early for special cases
        if CA_URL == "FIRST":
            if debug: print(f"{self.count}. {website}, returning early, type: first, OCSP: {self.OCSP}")
            return "first"
        elif CA_URL == "THIRD":
            if debug: print(f"{self.count}. {website}, returning early, type: third, OCSP: {OCSP}")
            return "third"
        elif CA_URL is None:
            if debug: print(f"{self.count}. {website}, returning early, type unknown, OCSP: {OCSP}")
            return "unknown"

        type = "unknown"

        try:
            tld_CA_URL = self.tld(CA_URL)
            if tld_CA_URL == self.tld(website):
                type = "private"
            elif tld_CA_URL in self.SAN(website): # Automatically "checks" for non-HTTPS by catching error
                type = "private"
            elif self.SOA(CA_URL) != self.SOA(website):
                type = "third"
        except Exception as e:
            if debug: print(f"Exception {e} with {website}")

        # Keep track of CA count per country
        if countryCode:
            if countryCode not in self.caCountByCountry:
                self.caCountByCountry[countryCode] = {}

            if CA not in self.caCountByCountry[countryCode]:
                self.caCountByCountry[countryCode][CA] = 1
            else:
                self.caCountByCountry[countryCode][CA] += 1

        if debug: print(f"{self.count}. {website}, CA: {CA}, type: {type}, OCSP: {OCSP}")

        return type


    # Helper: Given a website, returns the CA
    def getCA(self, website, retries=1):
        try:
            output = subprocess.check_output(["openssl", "s_client", "-connect", website + ":443", "-status"],
                                             timeout=5, input="", stderr=subprocess.STDOUT).decode("utf-8")
            rootCA = output.split("O = ")[1].split(" =")[0][:-4]

            if rootCA.startswith("\""):
                rootCA = rootCA[1:]
            if rootCA.endswith("\""):
                rootCA = rootCA[:-1]

            if "OCSP Response Status: successful" in output:
                OSCP = True
            else:
                OSCP = False

            return rootCA.strip(), OSCP

        except Exception as e:
            # print("openssl error in root_ca with", website, e)
            if retries > 0:
                self.getCA(website, retries - 1)
            return None, None

    # Helper: Given a CA name, return the CA URL
    def getCA_URL(self, website):
        if website in self.caMap:
            return self.caMap[website]
        print((f"UNIQUE CA: {website}"))
        return None

    # Helper: Given a website, return the top-level domain
    def tld(self, website):
        return tldextract.extract(website).domain

    # Helper: Return SAN list for website
    def SAN(self, website):
        SANList = []
        try:
            cmd = 'openssl s_client -connect ' + website + ':443 </dev/null 2>/dev/null | openssl x509 -noout -text | grep DNS'
            mycmd = subprocess.getoutput(cmd)
            list = str(mycmd).split(' DNS:')
            for item in list:
                SANList.append(item[:-1])
        except Exception as e:
            pass
        return SANList

    # Helper: Return SOA for url
    def SOA(self, website):
        return dns.resolver.query(website,'SOA')[0].mname

    # Helper: Populate CA Map
    def getCaMap(self):
        with open("caToUrl.json", mode="r") as jsonFile:
            return json.load(jsonFile)


# MISC SCRIPTS USING CA FINDER  -------------------------------------------------
def uniqueCATestGlobal():
    caFinder = CAFinder()
    testSites = []
    jsonPath = f"{Path(__file__).parent.parent}/data/alexaTop500SitesCountries.json"
    with open(jsonPath, mode="r") as jsonFile:
        jsonData = json.load(jsonFile)
    for country, sites in jsonData.items():
        for site in sites:
            testSites.append(site)
    uniqueCAs = set()
    for site in testSites:
        CA = caFinder.getCA(site)
        if CA and CA not in uniqueCAs:
            uniqueCAs.add(CA)
            print(CA)

def uniqueCATestUS():
    caFinder = CAFinder()
    jsonPath = f"{Path(__file__).parent.parent}/data/alexaTop500SitesCountries.json"
    with open(jsonPath, mode="r") as jsonFile:
        jsonData = json.load(jsonFile)
    uniqueCAs = set()
    for site in jsonData["US"]:
        CA = caFinder.getCA(site)

        if CA and CA not in uniqueCAs and CA not in caFinder.caMap:
            uniqueCAs.add(CA)
            print((f"UNIQUE CA: {CA} for {site}, "))
        else:
            print(f"CA: {CA} for {site}")

def getCACentralization(countryCode):
    caFinder = CAFinder()

    jsonPath = f"{Path(__file__).parent.parent}/data/alexaTop500SitesCountries.json"
    with open(jsonPath, mode="r") as jsonFile:
        jsonData = json.load(jsonFile)

    third = 0
    private = 0
    unknown = 0
    http = 0
    for site in jsonData[countryCode]:
        type = caFinder.getCAType(site, countryCode)
        if type == "third":
            third += 1
        elif type == "first" or type == "private":
            private += 1
        elif type == "unknown":
            unknown += 1
        elif type == "http":
            http += 1

    print(f"Results for {countryCode}")
    print(f"HTTPS: {1-http/500}")
    print(f"Third: {third/500}")
    print(f"OCSP: {caFinder.OCSP/500}")

    with open(f"../results/CA centralization/{countryCode}.json", "w") as outFile:
        json.dump(caFinder.caCountByCountry[countryCode], outFile, indent=4)

# RUN PROGRAM (CALL SCRIPTS) -------------------------------------------------
def runProgram():
    countryCode = "HU"
    print(f"STARTING FOR {countryCode}:")
    start = time.time()
    getCACentralization(countryCode)
    end = time.time()
    print(f"Execution took {round((end-start)/60)} minutes")


if __name__ == "__main__":
    runProgram()
