import json
import csv
import os.path
from os import path
import matplotlib.pyplot as plt

def read_json(filename):
	with open(filename) as json_file:
	    data = json.load(json_file)
	    return data




countries=[]

def get_countries_from_csv(filename):
	with open(filename) as csv_file:
	    csv_reader = csv.reader(csv_file, delimiter=',')
	    line_count = 0
	    for row in csv_reader:
	    	if line_count>0:
	    		countries.append(row[1])
	    	line_count+=1
	return countries

def total_cdns_analysis(dicts):
	# for each country, for each cdn find if private of third
	tp_fraction=[]
	for country in dicts.keys():
		total=0
		third=0
		for website in dicts[country].keys():
			for cdn in dicts[country][website].keys():
				if dicts[country][website][cdn]=='ThirdParty':
					third+=1
				total+=1
		tp_fraction.append(third*100/total)
	print("tp_fraction: ",tp_fraction)
	return tp_fraction


def cdn_criticality_analysis(dicts):
	# print(dicts)
	criticality_fraction=[]
	for country in dicts.keys():
		fraction=0
		total=0
		for cdn in dicts[country].keys():
			total+=1
			fraction+=dicts[country][cdn]["yes"]/(dicts[country][cdn]["no"]+dicts[country][cdn]["yes"])
		criticality_fraction.append(fraction*100/total)
	print("criticality function: ",criticality_fraction)
	return criticality_fraction




def cdn_popularity_analysis(dicts):
	#number of cdns that support 80% of websites?
	num_cdns=[]
	# print(dicts)
	for country in dicts.keys():
		total=0
		dicts[country]= {k: v for k, v in sorted(dicts[country].items(), key=lambda item: item[1],reverse=True)}
		for cdn in dicts[country].keys():
			total+=dicts[country][cdn]
		sum_=0
		iter_=0
		for cdn in dicts[country].keys():
			iter_+=1
			sum_+=dicts[country][cdn]
			if sum_/total>=0.8:
				break
		num_cdns.append(iter_)
	print("num cdns: ",num_cdns)
	num_cdns

def most_pop_cdns(dicts):
	cdns={}
	for country in dicts.keys():
		for cdn in dicts[country].keys():
			if cdn not in cdns:
				cdns[cdn]=0
			cdns[cdn]+=dicts[country][cdn]

	cdns= {k: v for k, v in sorted(cdns.items(), key=lambda item: item[1],reverse=True)}
	total=0
	for k in cdns.keys():
		total+=cdns[k]
	print("total: ",total)
	for k in cdns.keys():
		cdns[k]=cdns[k]*100/total
	return {k: v for k, v in sorted(cdns.items(), key=lambda item: item[1],reverse=True)}


def make_histogram(x,y,xlabel,ylabel,savefig):
	plt.bar(x,y,align='center') # A bar chart
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	# for i in range(len(y)):
	#     plt.hlines(y[i],0,x[i]) # Here you are drawing the horizontal lines
	plt.savefig(savefig)
	plt.show()


# def make_table(dict_):

def add_to_dict(dict1,dict2):
	for key in dict2.keys():
		if key not in dict1:
			dict1[key]={}
		for key2 in dict2[key].keys():
			dict1[key][key2]=dict2[key][key2]

countries=get_countries_from_csv('Centralization_Findings.csv')
print(countries)
total_cdns={}
cdn_criticality={}
cdn_popularity={}
for country in countries:
	if country=='': continue
	cdn_popularity_fn='results/cdns_popularity_'+country+'.json'
	cdn_criticality_fn='results/critical_dependency_'+country+'.json'
	total_cdns_fn='results/total_cdns'+country+'.json'
	if path.exists(cdn_criticality_fn):
		cdn_criticality[country]=read_json(cdn_criticality_fn)[country]
		total_cdns[country]=read_json(total_cdns_fn)[country]
		cdn_popularity[country]=read_json(cdn_popularity_fn)[country]
		# print(read_json(cdn_criticality_fn)[country])
	# print(cdn_criticality)
tp_fraction=total_cdns_analysis(total_cdns)
criticality_fraction=cdn_criticality_analysis(cdn_criticality)
# num=cdn_popularity_analysis(cdn_popularity)
num=[17, 16, 25, 26, 20, 21, 18, 22]
cdns=most_pop_cdns(cdn_popularity)
print(cdns)
# print(most_popular_cdns)
x=[i for i in range(len(tp_fraction))]
make_histogram(x,tp_fraction,'Countries','Fraction of third Party CDNs','tp_fraction.png')
make_histogram(x,criticality_fraction,'Countries','Fraction of Critical Dependency','criticality_fraction.png')
make_histogram(x,num,'Countries','Number of CDNs that host 80% of the websites','num_cdns.png')

# make_table(most_popular_cdns)




