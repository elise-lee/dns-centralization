import json
import tldextract
import matplotlib as mpl 
mpl.use('agg')
import matplotlib.pyplot as plt
import os

dnsResults=json.load(open("dnsCentralizationResults.json"))
resultsdict={}
# countryList=[]
for country in dnsResults:
	thirdParty=0
	centralizedBool=0
	dnsproviders={}
	CritDep=0
	thirdNdPrivate=0
	singleThird=0
	for website in dnsResults[country]:
		# for ns_type in dnsResults[country][website]["ns_type"]:
		# 	if ns_type=="third":
		# 		#how many websites use thirdparty dns
		# 		thirdParty+=1 
		# 		centralizedBool=1
		# 		break

		# if centralizedBool==1:
		if "third" in dnsResults[country][website]["ns_type"]:
			# print (website,dnsResults[country][website]["ns_type"])
			uniqueThirdPartyNS=[]
			index=0

			#how many websites use thirdparty dns
			thirdParty+=1 

			# websites using both third party and private
			if "private" in dnsResults[country][website]["ns_type"]:
				thirdNdPrivate+=1

			# websites critically dependant on a single 3rd party provider		
			if len(dnsResults[country][website]["ns_type"])==1:
				singleThird+=1

			for ns_type in dnsResults[country][website]["ns_type"]:
				ns=dnsResults[country][website]["provider"][index]
				index+=1
				if ns_type!="third":
					continue
				domain=tldextract.extract(ns).domain
				# print (ns,domain)
				#running tldextract returns empty string
				if domain=="":
					domain=ns
				if "awsdns" in domain:
					domain="awsdns"
				if "cloudflare"in domain:
					domain="cloudflare"
				#finding unique thridy party dns providers used by a website
				if domain not in uniqueThirdPartyNS:
					uniqueThirdPartyNS.append(domain)

			# # websites critically dependant on a single 3rd party provider		
			# if len(uniqueThirdPartyNS)==1:
			# 	CritDep+=1
			#freq of third party providers used by all domains
			for dns in uniqueThirdPartyNS: 
				if dns not in dnsproviders:
					dnsproviders[dns]=0
				dnsproviders[dns]+=1
	popular=[]
	#providers that are used by multiple domains
	for dns in dnsproviders:
		if dnsproviders[dns]>1:
			popular.append(dns)

	# countryList.append(country)
	if country not in resultsdict:
		resultsdict[country]={}
	resultsdict[country]["3rdPartyReliance"]=thirdParty
	resultsdict[country]["criticallyDependant"]=singleThird

	print ("\n\n",country,"; no of websites using third party dns: ",thirdParty,"; websites critically dependant on a single 3rd party provider: ",singleThird,"; websites using both third party and private: ",thirdNdPrivate,"; Total no of 3rd party dns providers: ",len(dnsproviders),"; no of 3rd party providers that are used by multiple domains: ",len(popular),"\n\n",dnsproviders,"\n\n",(popular),"\n")
	# break
#1 How many websites in each country are reliant on third party DNS provider? (done)
#2 How many websites in each country have multiple dns providers?
#3 How many websites using third party dns in each country have multiple dns providers? (done)
#4 How many use both third party and private? (done)
#5 Third party providers used by multiple domains in each country (count of those providers) (done) 
#6 number of websites using above type of third party providers across countries
#7 freq of websites relying on popular third party providers 


def thirdPartyReliancePlotbyRegion(_dict,countryList,metric,title):
	index=0

	print (len(countryList))
	for country in countryList:
		if country not in _dict:
			index+=1
			continue

		if index<=6:
			plt.plot(index,_dict[country][metric],color='c',marker='.',label="America")
		elif index>=7 and index<=32:
			plt.plot(index,_dict[country][metric],color='y',marker='.',label="Europe")
		elif index>=33 and index<=44:
			plt.plot(index,_dict[country][metric],color='m',marker='.',label="Asia Pacific")
		elif index>=45 and index<=48:
			plt.plot(index,_dict[country][metric],color='g',marker='.',label="Africa and Middle East")		
		index+=1
	
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = dict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys())

	# plt.legend()
	plt.title(title)
	plt.xlabel('Countries')
	plt.ylabel('Count')
	plt.margins(0.02)
	# plt.axis([0, None, None, None])
	if not os.path.exists("graphs"):
		os.mkdir("graphs")
	# print ("graphs/lighthouseTTFB"+cdn+feature)

	plt.savefig("graphs/Region"+metric)
	plt.clf()

def thirdPartyReliancePlotbyOverlap(_dict,countryList,metric,title):
	index=0

	print (len(countryList))
	for country in countryList:
		
		if country not in _dict:
			index+=1
			continue
		if country=='CA':
			color='g'
			overlap='high'
		elif country=='ZA':
			color='c'
			overlap='medium'
		elif country=='SE':
			color='r'
			overlap='low'
		plt.plot(index,_dict[country][metric],color=color,marker='.',label=overlap)		
		index+=1
	
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = dict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys())

	# plt.legend()
	plt.title(title)
	plt.xlabel('Countries')
	plt.ylabel('Count')
	plt.margins(0.02)
	# plt.axis([0, None, None, None])
	if not os.path.exists("graphs"):
		os.mkdir("graphs")
	# print ("graphs/lighthouseTTFB"+cdn+feature)

	plt.savefig("graphs/Overlap"+metric)
	plt.clf()

countryList=[]
with open("countryListOverlap.txt","r") as f:
	for country in f:
		if str(country)[:-1] in resultsdict:
			countryList.append(str(country)[:-1])
thirdPartyReliancePlotbyOverlap(resultsdict,countryList,"3rdPartyReliance","Number of websites using third Party DNS")
thirdPartyReliancePlotbyOverlap(resultsdict,countryList,"criticallyDependant","Number of websites critically dependant on a single third party DNS")


countryList=[]
with open("countryList.txt","r") as f:
	for country in f:
		countryList.append(str(country)[:-1])
# thirdPartyReliancePlotbyRegion(resultsdict,countryList)

thirdPartyReliancePlotbyRegion(resultsdict,countryList,"3rdPartyReliance","Number of websites using third Party DNS")
thirdPartyReliancePlotbyRegion(resultsdict,countryList,"criticallyDependant","Number of websites critically dependant on a single third party DNS")

			
