import dns
import dns.resolver
import tldextract
import json
from selenium import webdriver
import json
from browsermobproxy import Server
from bs4 import BeautifulSoup
import os, time
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request
from os.path import isfile, join
import selenium.webdriver.remote.utils as utils
import subprocess
import sys
import os
import pydig
from pathlib import Path

project_path=os.path.dirname(os.path.abspath(__file__))

# project_path = utils.project_path()
# project_path='/Users/sanaasif/miniconda3/lib/python3.8/site-packages'

from collections import defaultdict
import socket
import ssl

def get_SAN(website):
	SANList=[]
	try:
		cmd='openssl s_client -connect '+website+':443 </dev/null 2>/dev/null | openssl x509 -noout -text | grep DNS'
		mycmd=subprocess.getoutput(cmd)
		list=str(mycmd).split(' DNS:')
		for item in list:
			SANList.append(item[:-1])
	except Exception as e:
		print ("not support HTTPS")

	return SANList
#--code for internal resources----------------
class Har_generator:
	def __init__(self):
		self.hars = []
		# self.server = Server(path="./BrowserMobProxy/bin/browsermob-proxy", options=dict)
		# self.server=Server(join(project_path,"browsermobproxy"))
		self.server = Server(join(project_path, "browsermob-proxy-2.1.4", "bin", "browsermob-proxy"))
		self.server.start()
		self.proxy = self.server.create_proxy(params={"trustAllServers": "true"})
		options = webdriver.ChromeOptions()
		options.add_argument("--proxy-server={}".format(self.proxy.proxy))	
		options.add_argument("--ignore-ssl-errors=yes")
		options.add_argument("--ignore-certificate-errors")
		options.add_argument("--headless")
		options.add_argument("--no-cache")

		self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

	def __del__(self):
		self.server.stop()
		self.driver.quit()

	# loads up a site
	# takes a site url
	# returns a json har object
	def get_har(self, site):
		# print("in get_har")
		
		try:
			name = site
			self.proxy.new_har(name)
			self.driver.get("https://"+site)
			time.sleep(1)
			return self.proxy.har
		except Exception as e:
			print(str(e))
			return None

		
	# calls get_har for each site
	# takes a list of site urls
	# returns a dictionary of site url and json har objects
	def get_hars(self, sites):
		x = 0
		hars = []
		for site in sites:
			# print("%d: Working on %s" % (x, site))
			har = self.get_har(site)
			hars.append(har)
			self.hars.append(har)
			x = x + 1
		return hars

class Resource_collector:
	def __init__(self):
		self.resources = []

	def dump(self, fn_prefix,country):
		# print(join(fn_prefix,"alexaResources"+country+".json"))	
		utils.dump_json(self.resources, join(fn_prefix,"alexaResources"+country+".json"))

		# utils.dump_json(self.resources, join(project_path,fn_prefix,"alexaResources"+country+".json"))


	# extracts all the resources from each har object
	# takes a list of har json objects
	# stores in the object resources
	def collect_resources(self, har):
		# print("in collect resources")
		# for har in hars:
		if har and "log" in har.keys() and "entries" in har["log"].keys():
			for entry in har["log"]["entries"]:
				resource = entry["request"]["url"]
				if resource not in self.resources:
					self.resources.append(str(resource))
		return self.resources



def get_internal_resources(website):
	# print("in find_internal_resources")
	#phantomjs to render resources
		#tld matching
		#SAN list of the SSL certificate 
		#public suffix lists
		#SOA records

	#OR use hars to find resources!
	hm = Har_generator()
	rc = Resource_collector()
	hars = hm.get_har(website)
	# print("hars:")
	# print(hars)
	return rc.collect_resources(hars)

#-----done with internal resources code ---------------------



def find_CDN_from_CNAME(cdn_cname,cname=True):
	#make dict for cdn_map mapping each cdn to the cnames
	# print("in find_CDN_from_CNAME")
	cdn_map={}
	file1 = open('cdnMap', 'r')
	Lines = file1.readlines()

	# Strips the newline character
	for line in Lines:
		cdn=line.split(",")
		# print(cdn[0])
		cdn_map[cdn[0]]=[]
		sites=cdn[1].split(" ")
		for site in sites:
			if '\n' in site:
				site=site.replace('\n','')
			cdn_map[cdn[0]].append(site)

	# print("keys: ", cdn_map.keys())
	# print("cdn_cname: ", cdn_cname)
	for cdn in cdn_map.keys():
		if cname:
			for cn in cdn_map[cdn]:
				if cn is not '':
					if cdn_cname in cn:
						# print("cdn_cname:"+cdn_cname+" in cn:"+cn)
						return cdn
					if cn in cdn_cname:
						# print("cdn_cname:"+cdn_cname+" in cn:"+cn)
						return cdn
		else:
			# print("hellooooo")
			if cdn==cdn_cname:
				# print("here")
				# print(cdn_map[cdn])
				return cdn_map[cdn]
	return None

#---find CDN -- Rashna's code -----------------------------------
def url_to_domain(url):
    ext = tldextract.extract(url)
    if ext[0] == '':
        ext = ext[1:]
    return ".".join(ext)

class Url_processor:
	def __init__(self,country,resources):
		self.cdn_mapping = {}
		if resources is not None:
			self.resources_mapping=resources
		else:
			self.resources_mapping = load_json(join(project_path, "analysis", "measurements", country, "alexaResources"+country+".json"))
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



	# Find cdn given a file of the resources
	# Takes a list of unique domains
	# Returns a dictionary containing the found CDNs for each domain
	def find_cdn(self):
		domains = []
		domains.append(self.resources_mapping)
		# for resource in self.resources_mapping:
		# 	if utils.url_to_domain(resource) not in domains:
		# 		domains.append(utils.url_to_domain(resource))
		i = -1
		self.driver.get("https://www.cdnplanet.com/tools/cdnfinder/")
		total = len(domains)
		for resource in domains:
			i+=1
			if i > 0 and i % 50 == 0:
				self.restart_drive()
				self.driver.get("https://www.cdnplanet.com/tools/cdnfinder/")

			print("%.2f%% completed" % (100 * i / total))
			print(i)
			# for _ in range(3):
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
			except Exception as e:
				print(str(e))
				time.sleep(2)


			time.sleep(2)
		return self.cdn_mapping

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

def find_CDN_from_CNAME_Rashna(cname):
	up=Url_processor(None,cname)
	cdn_mapping=up.find_cdn()
	for cdn in cdn_mapping.keys():
		if cname in cdn_mapping[cdn]:
			return cdn
	# up.collectPopularCDNResources(country)
	# up.dump(join(project_path, "analysis", "measurements", country))

#----------Rashna's code for finding CDN ends-------------------------------------


def CDN_centralization(websites_array):
	cdns=={}
	total=len(websites_array)
	for website in websites_array:
		cdn=find_CDN(website)
		if cdn in cdns:
			cdns[cdn]+=1
		else:
			cdns[cdn]=1

	for cdn in cdns.keys():
		cdns[cdn]/=total


def get_CNAMES(website):
	# print("in get_CNAMES\n")
	# print("querying the website: "+website)
	# cnames=subprocess.check_output(['dig',website,'CNAME'])
	# cnames=str(cnames,"utf-8")
	# print(cnames)
	print(url_to_domain(website))
	return True,[]
	try:
		print("in try!!")
		cnames=subprocess.check_output(['dig',website+'.'])
		cnames=str(cnames,"utf-8")
		# print(cnames)
		if "ANSWER: 0" in cnames:
			# print("answer 0")
			return False, []
		else:
			# print(cnames)
			return True
		if 'cname' in cnames:
			# print("cname present")
			array=cnames.split()
			check=0
			for i in array:
				if check==1:
					print(i)
					return True,[i]
				if i=='cname':
					check=1
		else:
			# print("cname not present - returning domain instead")
			return False,[]
	except:
		# print("in except of cname -- returning domain instead")
		return False,[]



def get_tld(website):
	tld = tldextract.extract(website)
	# print("tld is "+tld.domain)
	return tld.domain


def if_https(website):
	# print ("in if https")
	try:
		output = subprocess.check_output(["bash", 'https/check.sh',website])
		# print(output)
		output = str(output,"utf-8")
		print(output)
	except subprocess.CalledProcessError as e:
		print ("Oops error for website", line, e)


def CDN_private_third(cdn,website):
	# print ("in private third")
	resolver = dns.resolver.Resolver()

	#isHTTPS?
	#SAN?
	#if for all cnames then wont third_party keep changing? whats the point
	third_party=None
	find_CDN=False
	cnames=find_CDN_from_CNAME(cdn,False)
	print("cnames for private third")
	# print(cnames)
	for cname in cnames:
		# print("cname: "+cname)
		cn_tld=get_tld(cname)
		if cn_tld==get_tld(website):
			# print("tlds are the same")
			return False

		SANList=get_SAN(website)
		for san in SANList:
			if cn_tld in san:
				return False

		try:
			soa_w_answers = resolver.query(website,'SOA')
			soa_w=soa_w_answers[0].mname
			# print("soa_w: "+str(soa_w))
			try:
				# cn=subprocess.check_output(['dig',website,'SOA'])
				# if 'ANSWER: 1' in cn:

				# cn=str(output,"utf-8")
				# print(cn)
				# return None
				answer = resolver.query(cname, 'SOA')
				soa_cname=answer[0].mname
				# print("soa_cname: " + str(soa_cname))
				if soa_w!=soa_cname:
					return True
				else:
					return False
				# if answer.rrset is None:
				#    soa_ns=str(answer.response.authority[0]).split(" ")[0]
			except Exception as e:
				print("error on cname")

		except Exception as e:
			print("error on website")

			


	return third_party





def read_websites_country(country,filename):
	f = open(filename,'r') 
	data = json.load(f) 
	websites=data[country]
	f.close()
	return websites

def popular_cdns(cdns_popularity):
	# print(cdns_popularity)
	sorted_cdns=sorted(cdns_popularity.items(), key=lambda x: x[1], reverse=True)
	# sorted_cdns={k: v for k, v in sorted(cdns_popularity.items(), key=lambda item: item[1], reverse=True)}
	i=0
	total=0
	highest=0
	websites=0
	for k,v in sorted_cdns:
		if i==0:
			highest=k
			websites=v
		total+=v
		i+=1
	if total==0:
		return 0,0
	return highest,websites*100/total

def dump_json(data, fn):
    with open(fn, 'w') as fp:
        json.dump(data, fp)

def main(argv):
	#set country
	country=argv[1]
	filename='../data/alexaTop500SitesCountries.json'

	critical_dependency={}
	cdns_popularity={}
	total_cdns={}
	num=10
	website_iter=0

	websites=read_websites_country(country,filename)
	cdns_popularity[country]={}
	critical_dependency[country]={}
	total_cdns[country]={}
	for website in websites:
		# if website_iter==num:
		# 	break
		website_iter+=1
		total_cdns[country][website]={}
		print("country: "+country+" ,website: "+website+" ,num: "+str(website_iter))
		internal_resources=get_internal_resources(website)
		cnames=[]
		cnames.append(url_to_domain(website))
		for resource in internal_resources:
			domain=url_to_domain(resource)
			if domain not in cnames:
				cnames.append(domain)
			# present,cn=get_CNAMES(resource)
			# if present:
			# 	for _cn in cn:
			# 		if 'www.' in _cn:
			# 			_cn=_cn.replace('www.','')
			# 		if 'https://' in _cn:
			# 			_cn=_cn.replace('https://','')
			# 		if _cn not in cnames:
			# 			cnames.append(_cn)


		for i in range(len(cnames)):
			if 'www.' in cnames[i]:
				cnames[i]=cnames[i].replace('www.','')

		# continue
		cdns=[]
		# print(cnames)
		for cname in cnames:
			cdn=find_CDN_from_CNAME(cname,True)
			if cdn not in cdns:
				if cdn!=None:
					cdns.append(cdn)
					if cdn in cdns_popularity[country].keys():
						cdns_popularity[country][cdn]+=1
					else:
						cdns_popularity[country][cdn]=1


		for cdn in cdns:
			private_third=CDN_private_third(cdn,website)
			if private_third==True:
				total_cdns[country][website][cdn]="ThirdParty"
			elif private_third==False:
				total_cdns[country][website][cdn]='Private'
			else:
				total_cdns[country][website][cdn]='Unknown'

		if len(cdns)==1:
			if cdns[0] in critical_dependency[country]:
				critical_dependency[country][cdns[0]]['yes']+=1
			else:
				critical_dependency[country][cdns[0]]={'yes':1,'no':0}


		else:
			for cdn in cdns:
				if cdn in critical_dependency[country]:
					critical_dependency[country][cdn]['no']+=1
				else:
					critical_dependency[country][cdn]={'yes':0,'no':1}



		dump_json(total_cdns,'results/total_cdns'+country+'.json')
		dump_json(critical_dependency,'results/critical_dependency_'+country+'.json')
		dump_json(cdns_popularity,'results/cdns_popularity_'+country+'.json')
		
		print("critical_dependency")
		print(critical_dependency[country])
		print("cdn popularity")
		print(cdns_popularity[country])


		# cdn,percentage=popular_cdns(cdns_popularity[country])
		


		# print("country "+country+"s most popular CDN is " + cdn + " with a percentage of "+str(percentage)+" websites hosted on it")

		#aggregate third_party info for all websites in a country.. and then for all countries in a particular set and then check percentage
		#find popular CDN in each country

		#for critical dependency, aggregate for all websites in a country, and then all countries in a set, and then check percentage





				#critical dependency of website on cdn


	#result should be 
	#website={private:[CDNs],third:[CDNs]}
	#no indirect dependencies detected here because its directly matching to cdn..?
	#for critically dependant servers (website needs 1 cdn only) , find which ones have third party dependency

	#Questions:
	#what to do when process name is long and weird and doesnt give a cname..?
if __name__ == "__main__":
    main(sys.argv)





