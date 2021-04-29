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
	redundant=0
	TrueRedundant=0
	multipleThirdParty=0
	for website in dnsResults[country]:
		#how many websites are redundantly provisioned with dns
		if len(dnsResults[country][website]["ns_type"])>=1:
			redundant+=1
			if "private" in dnsResults[country][website]["ns_type"]:
				TrueRedundant+=1
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

				if len(uniqueThirdPartyNS)>1:
					multipleThirdParty+=1
			
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
	sorteddnsproviders=dict(sorted(dnsproviders.items(), key=lambda item: item[1]))
	my_keys = sorted(dnsproviders, key=dnsproviders.get, reverse=True)[:5]

	if country not in resultsdict:
		resultsdict[country]={}
	resultsdict[country]["3rdPartyReliance"]=thirdParty
	resultsdict[country]["criticallyDependant"]=singleThird
	resultsdict[country]["3rdndPrivate"]=thirdNdPrivate
	resultsdict[country]["redundant"]=redundant
	resultsdict[country]["TrueRedundant"]=TrueRedundant
	resultsdict[country]["multipleThirdParty"]=multipleThirdParty
	resultsdict[country]["dnsproviders"]=sorteddnsproviders
	resultsdict[country]["populardnsproviders"]=my_keys


	# print ("\n\n",country,"; websites using third party dns: ",thirdParty,"; websites critically dependant on a 3rd party provider: ",singleThird,"; websites third party and private dns: ",thirdNdPrivate,"; websites being multipleThirdParty dns: ",multipleThirdParty,"; websites being redundantly provisioned by dns: ",redundant,"; Total no of 3rd party dns providers: ",len(dnsproviders),"; no of 3rd party providers that are used by multiple domains: ",len(popular),"\n\n",sorteddnsproviders,"\n\n",(popular),"\n")
	# break
#1 How many websites in each country are reliant on third party DNS provider? (done)
#2 How many websites in each country have multiple dns providers?
#3 How many websites using third party dns in each country have multiple dns providers? (done)
#4 How many use both third party and private? (done)
#5 Third party providers used by multiple domains in each country (count of those providers) (done) 
#6 number of websites using above type of third party providers across countries
#7 freq of websites relying on popular third party providers 

def thirdPartyDNSProviderPlots(_dict):
	# top1=[]
	# top2=[]
	# top3-[]
	# top4=[]
	# top5=[]
	providerDict={}

	for country in _dict:
		for provider in _dict[country]["populardnsproviders"]:
			count=_dict[country]["dnsproviders"][provider]
			if provider not in providerDict:
				providerDict[provider]=[]
			providerDict[provider].append(count)
	# print (providerDict)

	# my_keys = sorted(providerDict, key=providerDict.get, reverse=True)[:5]
	# print ("my_keys",my_keys)

	colors=['c','b','m','y','g','r']
	indexes=[]
	maxvalues=[]
	for provider in providerDict:
		maxvalues.append(len(providerDict[provider]))
		# print (provider,len(providerDict[provider]))

	maxvalues.sort()
	maxvalues=maxvalues[-6:]
	# print (maxvalues)
	popularProviders=[]

	import statistics
	for provider in providerDict:
		if len(providerDict[provider]) in maxvalues:
			popularProviders.append(provider)
			# index+=1
	print ("Popular: ",popularProviders)
	index=0
	for provider in popularProviders:
		print (provider,max(providerDict[provider]),sum(providerDict[provider])/len(providerDict[provider]),min(providerDict[provider]))
		print (provider,sum(providerDict[provider])/len(providerDict[provider]),statistics.stdev(providerDict[provider]))
		
		# indexes=[]
		# for x in range(len(providerDict[provider])):
		# 	indexes.append(x)
		# y=providerDict[provider]
		# print (colors[index])
		# plt.plot(indexes,sorted(y),color=colors[index],marker='.',linewidth=2,label=provider)
		# index+=1
	
	plt.legend()
	plt.grid()
	plt.title("Number of Websites using the given provider")
	plt.xlabel('Countries')
	plt.ylabel('Website Count')
	plt.margins(0.02)
	# plt.axis([0, None, None, None])
	if not os.path.exists("graphs"):
		os.mkdir("graphs")
	# print ("graphs/lighthouseTTFB"+cdn+feature)

	plt.savefig("graphs/provider")
	plt.clf()
# thirdPartyDNSProviderPlots(resultsdict)

def thirdPartyDNSPlots(_dict,metric,label,color):
	index=0
	print (len(countryList))
	indexes=[]
	metrics=[]
	

	for country in _dict:
		indexes.append(index)
		index+=1
		metrics.append(100*_dict[country][metric]/500)
	metrics.sort()
	# print (metrics)
	_max=metrics[-1]
	_min=metrics[0]
	print (_max,_min,sum(metrics)/len(metrics))
	for country in _dict:
		if _max == 100*_dict[country][metric]/500:
			_maxC=country
		if _min == 100*_dict[country][metric]/500:
			_minC=country
	print (metric," country with Max Value: ",_maxC," country with Max Value: ",_minC)
	plt.plot(indexes,metrics,color=color,marker='.',linewidth=2,label=label)

	plt.legend()
	plt.grid()
	# plt.title(title)
	plt.xlabel('Countries')
	plt.ylabel('Percentage')
	plt.margins(0.02)
	# plt.axis([0, None, None, None])
	if not os.path.exists("graphs"):
		os.mkdir("graphs")
	# print ("graphs/lighthouseTTFB"+cdn+feature)

	plt.savefig("graphs/"+metric)
	plt.clf()

def thirdPartyDNSPlots2(_dict):
	index=0
	print (len(countryList))
	indexes=[]
	
	thirdNdPrivate=[]
	redundant=[]
	multipleThirdParty=[]
	trulyRedundant=[]
	maxes=[]
	mins=[]
	maxesC=[]
	minsC=[]

	

	for country in _dict:
		indexes.append(index)
		index+=1
		# metrics.append(100*_dict[country][metric]/500)
		thirdNdPrivate.append(100*_dict[country]["3rdndPrivate"]/500)	
		redundant.append(100*_dict[country]["redundant"]/500)	
		multipleThirdParty.append(100*_dict[country]["multipleThirdParty"]/500)	
		trulyRedundant.append(100*_dict[country]["TrueRedundant"]/500)



	maxes.append(max(thirdNdPrivate))
	maxes.append(max(redundant))
	maxes.append(max(multipleThirdParty))
	maxes.append(max(trulyRedundant))


	mins.append(min(thirdNdPrivate))
	mins.append(min(redundant))
	mins.append(min(multipleThirdParty))
	mins.append(min(trulyRedundant))

	# for country in _dict:
	# 	if 100*_dict[country]["3rdndPrivate"]/500 in maxes:
	# 		maxesC.insert(0, country)
	# 	if 100*_dict[country]["redundant"]/500 in maxes:
	# 		maxesC.insert(1, country)
	# 	if 100*_dict[country]["multipleThirdParty"]/500 in maxes:
	# 		maxesC.insert(2, country)
	# 	if 100*_dict[country]["TrueRedundant"]/500 in maxes:
	# 		maxesC.insert(3, country)

	# 	if 100*_dict[country]["3rdndPrivate"]/500 in mins:
	# 		print (country,100*_dict[country]["3rdndPrivate"]/500,mins)
	# 		minsC.insert(0, country)
	# 	if 100*_dict[country]["redundant"]/500 in mins:
	# 		print (country,100*_dict[country]["redundant"]/500,mins)
	# 		minsC.insert(1, country)
	# 	if 100*_dict[country]["multipleThirdParty"]/500 in mins:
	# 		minsC.insert(2, country)
	# 	if 100*_dict[country]["TrueRedundant"]/500 in mins:
	# 		minsC.insert(3, country)

	

	# metrics.sort()
	# criticallyDependant.sort()
	thirdNdPrivate.sort()
	redundant.sort()
	multipleThirdParty.sort()
	trulyRedundant.sort()

	arrays=[thirdNdPrivate,redundant,multipleThirdParty,trulyRedundant]
	metrics=["3rdndPrivate","redundant","multipleThirdParty","TrueRedundant"]
	ind=0
	for _metric in metrics:
		_max=arrays[ind][-1]
		_min=arrays[ind][0]
		print (_max,_min,sum(arrays[ind])/len(arrays[ind]))

		ind+=1
		# print(_max,_min,)
		for country in _dict:
			# print (_metric,_dict[country][_metric])
			if _max ==100* _dict[country][_metric]/500:
				_maxC=country
			if _min == 100*_dict[country][_metric]/500:
				_minC=country
		print (_metric," country with Max Value: ",_maxC," country with Min Value: ",_minC)
		maxesC.append(_maxC)
		minsC.append(_minC)
	print (maxesC,minsC)
	# plt.plot(indexes,metrics,color='c',marker='.',linewidth=2,label=label)
	# plt.plot(indexes,criticallyDependant,color='r',marker='.',linewidth=2,label="Critical Dependency")

	plt.plot(indexes,thirdNdPrivate,color='c',marker='.',linewidth=2,label="3rd + Private")
	plt.plot(indexes,redundant,color='y',marker='.',linewidth=2,label="Redundancy")
	plt.plot(indexes,multipleThirdParty,color='b',marker='.',linewidth=2,label="multiple third")
	plt.plot(indexes,trulyRedundant,color='g',marker='.',linewidth=2,label="True Redundancy")


	plt.text(-0.5,thirdNdPrivate[0]+1,minsC[0])
	plt.text(-0.5,redundant[0]+2,minsC[1])
	plt.text(-0.5,multipleThirdParty[0]+2,minsC[2])
	plt.text(-0.5,trulyRedundant[0]+2,minsC[3])

	plt.text(48-0.5,thirdNdPrivate[-1]+2,maxesC[0])
	plt.text(48-0.5,redundant[-1]+2,maxesC[1])
	plt.text(48-0.5,multipleThirdParty[-1]+2,maxesC[2])
	plt.text(48-0.5,trulyRedundant[-1]-0.2,maxesC[3])


	plt.legend()
	plt.grid()
	# plt.title(title)
	plt.xlabel('Countries')
	plt.ylabel('Percentage')
	plt.margins(0.02)
	# plt.axis([0, None, None, None])
	if not os.path.exists("graphs"):
		os.mkdir("graphs")
	# print ("graphs/lighthouseTTFB"+cdn+feature)

	plt.savefig("graphs/DNSPlots")
	plt.clf()

def thirdPartyReliancePlotbyRegion(_dict,countryList,metric,title):
	index=0

	print (len(countryList))
	indexList=[0,1,2,3,7,11,21,23,30,33,35,43,45,46,47,48,49]
	for country in countryList:
		if country not in _dict:
			index+=1
			continue
		if index<=6:
			plt.plot(index,100*_dict[country][metric]/500,color='c',marker='.',linewidth=2,label="America")

			# print (country,'c')
		elif index>=7 and index<=32:
			plt.plot(index,100*_dict[country][metric]/500,color='y',marker='.',linewidth=2,label="Europe")
			# print (country,'y')

		elif index>=33 and index<=44:
			plt.plot(index,100*_dict[country][metric]/500,color='m',marker='.',linewidth=2,label="Asia Pacific")
			# print (country,'m')
		elif index>=45:
			plt.plot(index,100*_dict[country][metric]/500,color='g',marker='.',linewidth=2,label="Africa and Middle East")	
		if index in indexList:
			plt.text(index,(100*_dict[country][metric]/500)+0.2,country)

			# print (country,'g')	
		index+=1
	# if legend=="yes":
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = dict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys(),loc="upper center")

	# plt.legend()
	plt.grid()
	plt.title(title)
	plt.xlabel('Countries')
	plt.ylabel('Percentage of Websites')
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
		plt.plot(index,_dict[country][metric],color=color,marker='.',linewidth=2,label=overlap)		
		index+=1
	
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = dict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys())

	# plt.legend()
	plt.grid()
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
thirdPartyReliancePlotbyOverlap(resultsdict,countryList,"3rdndPrivate","Number of websites that use third party DNS and private DNS")


countryList=[]
with open("countryList.txt","r") as f:
	for country in f:
		countryList.append(str(country)[:-1])
# thirdPartyReliancePlotbyRegion(resultsdict,countryList)
# print (countryList)
print ("Graphsss")
thirdPartyReliancePlotbyRegion(resultsdict,countryList,"3rdPartyReliance","Percentage of websites using third Party DNS")
thirdPartyReliancePlotbyRegion(resultsdict,countryList,"criticallyDependant","Percentage of websites critically dependent on a single third party DNS")
thirdPartyReliancePlotbyRegion(resultsdict,countryList,"3rdndPrivate","Percentage of websites that use third party DNS and private DNS")

thirdPartyDNSPlots2(resultsdict)
thirdPartyDNSPlots(resultsdict,"3rdPartyReliance","Third Party Dependency",'c')
thirdPartyDNSPlots(resultsdict,"criticallyDependant","Critical Dependency",'r')

for country in resultsdict:
	if resultsdict[country]["redundant"]!=resultsdict[country]["TrueRedundant"]:
		print (country,resultsdict[country]["redundant"],resultsdict[country]["TrueRedundant"])
			
