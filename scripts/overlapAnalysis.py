import json
import matplotlib as mpl 
mpl.use('agg')
import matplotlib.pyplot as plt
import os

import csv
_list=['5k','10k','25k','50k']
for x in _list:
	reader = csv.reader(open('AlexaOverlaps -Global'+x+'.csv', 'r'))
	d = {}
	i=0
	for row in reader:
		if i==0:
			i+=1
			continue
		c,k,v1 = row
		d[k] = v1
		i+=1
	print (i)
	with open(x+".json",'w') as fp:
		json.dump(d,fp,indent=4)

def plotOverlap():
	onek=json.load(open("1k.json"))
	fivek=json.load(open("5k.json"))
	tenk=json.load(open("10k.json"))
	twenty5k=json.load(open("25k.json"))
	fiftyk=json.load(open("50k.json"))
	index=0
	percentages=[]
	indexes=[]
	for country in onek:
		percentages.append(float(onek[country][:-1]))
		indexes.append(index)
		index+=1
	plt.plot(indexes,percentages,color='c',marker='.',label="1k")

	index=0
	percentages=[]
	indexes=[]
	for country in fivek:
		percentages.append(float(fivek[country][:-1]))
		indexes.append(index)
		index+=1
	plt.plot(indexes,percentages,color='m',marker='.',label="5k")

	index=0
	percentages=[]
	indexes=[]
	for country in tenk:
		percentages.append(float(tenk[country][:-1]))
		indexes.append(index)
		index+=1
	plt.plot(indexes,percentages,color='y',marker='.',label="10k")

	index=0
	percentages=[]
	indexes=[]
	for country in twenty5k:
		percentages.append(float(twenty5k[country][:-1]))
		indexes.append(index)
		index+=1
	plt.plot(indexes,percentages,color='b',marker='.',label="20k")

	index=0
	percentages=[]
	indexes=[]
	for country in fiftyk:
		percentages.append(float(fiftyk[country][:-1]))
		indexes.append(index)
		index+=1
	plt.plot(indexes,percentages,color='g',marker='.',label="50k")

	plt.legend()
	plt.title("Overlap of alexa sites in this set with 500 regional sites")
	plt.xlabel('country')
	plt.ylabel('percentage overlap')
	plt.margins(0.02)
	# plt.axis([0, None, None, None])
	if not os.path.exists("graphs"):
		os.mkdir("graphs")
	# print ("graphs/lighthouseTTFB"+cdn+feature)

	plt.savefig("graphs/percentageOverlap")
	plt.clf()

plotOverlap()

