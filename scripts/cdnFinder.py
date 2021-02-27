from selenium import webdriver
import json
from browsermobproxy import Server
from bs4 import BeautifulSoup
import os, time
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request
from os.path import isfile, join
import utils


class Url_processor:
	def __init__(self,country):
		self.cdn_mapping = {}
		self.resources_mapping = utils.load_json(join(project_path, "analysis", "measurements", country, "alexaResources"+country+".json"))

		self.options = webdriver.ChromeOptions()
		self.options.add_argument("--ignore-ssl-errors=yes")
		self.options.add_argument("--ignore-certificate-errors")
		# self.options.add_argument("--headless")

		self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.options)

	def __del__(self):
		self.driver.quit()

	def restart_drive(self):
		print("Restarting...")
		self.driver.quit()
		self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.options)

	def dump(self, fn_prefix):
		utils.dump_json(self.cdn_mapping, join(fn_prefix,"PopularcdnMapping.json"))



	# Find cdn given a file of the domains
	# Takes a list of unique domains
	# Returns a dictionary containing the found CDNs for each domain
	def find_cdn(self):
		domains = []
		for resource in self.resources_mapping:
			if utils.url_to_domain(resource) not in domains:
				domains.append(utils.url_to_domain(resource))
		i = 0
		self.driver.get("https://www.cdnplanet.com/tools/cdnfinder/")
		total = len(domains)
		for resource in domains:
			if i > 0 and i % 50 == 0:
				self.restart_drive()
				self.driver.get("https://www.cdnplanet.com/tools/cdnfinder/")

			print("%.2f%% completed" % (100 * i / total))

			for _ in range(3):
				try:
					self.driver.find_element_by_xpath("//*[@id=\"tool-form-main\"]").clear()
					self.driver.find_element_by_xpath("//*[@id=\"tool-form-main\"]").send_keys(resource)
					self.driver.find_element_by_xpath("//*[@id=\"hostname-or-url\"]").click()
					self.driver.find_element_by_xpath("//*[@id=\"tool-form\"]/button").click()
					time.sleep(3)

					doc = BeautifulSoup(self.driver.page_source, "html.parser")
					domain=doc.findAll('code', attrs={"class" : "simple"})
					cdn=doc.findAll('strong')
					site=domain[0].text
					cdn=cdn[0].text
					print (site,cdn)
					if "Amazon" in cdn:
						cdn="Amazon"
					if cdn=="Amazon" or cdn=="Akamai" or cdn=="Google" or cdn=="Cloudflare" or cdn=="Fastly":
						if cdn not in self.cdn_mapping:
							self.cdn_mapping[cdn]=[]
						self.cdn_mapping[cdn].append(resource)
					break
				except Exception as e:
					print(str(e))
					time.sleep(2)


			time.sleep(2)
			i += 1

	def collectPopularCDNResources(self,country):
		unique=[]
		with open(join(project_path, "analysis", "measurements", country, "AlexaUniqueResources.txt"),"w") as f:
			for cdn in self.cdn_mapping:
				for domain in self.cdn_mapping[cdn]:
					for resource in self.resources_mapping:
						if domain in resource:
							if resource not in unique:
								f.write(resource+"\n")
								unique.append(resource)
							
			f.close()
		
def runResourceCollector(country):
		up=Url_processor(country)
		up.find_cdn()
		up.collectPopularCDNResources(country)
		up.dump(join(project_path, "analysis", "measurements", country))
		# up.dump("measurements/"+country)
		del up

if __name__ == "__main__":
	runResourceCollector('India')
