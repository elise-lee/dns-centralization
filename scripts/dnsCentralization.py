import dns.resolver
import tldextract
import subprocess
import shlex

def ThirdPartyDNS(website,dict):
	
	try:
		cmd='openssl s_client -connect '+website+':443 </dev/null 2>/dev/null | openssl x509 -noout -text | grep DNS'
		mycmd=subprocess.getoutput(cmd)
		list=str(mycmd).split(' DNS:')
		SANList=[]
		for item in list:
			SANList.append(item[:-1])
	except Exception as e:
		print ("not support HTTPS")

	answers = dns.resolver.query(website,'NS')
	nameservers=[]
	ns_type="unknown"

	for server in answers:
		nameservers.append(str(server.target))

	for ns in nameservers:
		# print (ns,website,tldextract.extract(website).domain,tldextract.extract(ns).domain)
		if tldextract.extract(website).domain==tldextract.extract(ns).domain:
			ns_type="private"
		if ns_type!="private":
			for item in SANList:
				if str(tldextract.extract(ns).domain) in item:
					ns_type="private"
					break
		if ns_type!="private":
			try:
				answer = dns.resolver.query(ns, 'SOA', raise_on_no_answer=False)
				if answer.rrset is None:
				   soa_ns=str(answer.response.authority[0]).split(" ")[0]

				soa_w_answers = dns.resolver.query(website,'SOA')
				soa_w=soa_w_answers[0].mname

				if soa_w!=soa_ns:
					ns_type="third"
			except Exception as e:
				print ("error",website,ns, str(e))
		if website not in dict:
			dict[website]=[]
		dict[website].append(ns_type)

websites=['amazon.com','google.com','youtube.com']
dict={}
for website in websites:
	ThirdPartyDNS(website,dict)
print (dict)
	
# 𝑁𝑆 ← 𝐷𝐼𝐺_𝑁𝑆(𝑤)
# for 𝑛𝑠 ∈ 𝑁 𝑆 do
# 𝑛𝑠.𝑡𝑦𝑝𝑒 ←𝑢𝑛𝑘𝑛𝑜𝑤𝑛
# if 𝑡𝑙𝑑 (𝑛𝑠) = 𝑡𝑙𝑑 (𝑤) then
# 𝑛𝑠.𝑡𝑦𝑝𝑒 ← 𝑝𝑟𝑖𝑣𝑎𝑡𝑒
# else if 𝑖𝑠𝐻𝑇𝑇 𝑃𝑆 (𝑤) & 𝑡𝑙𝑑 (𝑛𝑠) ∈ 𝑆𝐴𝑁 (𝑤) then
# 𝑛𝑠.𝑡𝑦𝑝𝑒 ← 𝑝𝑟𝑖𝑣𝑎𝑡𝑒
# else if 𝑆𝑂𝐴(𝑛𝑠) ≠ 𝑆𝑂𝐴(𝑤) then
# 𝑛𝑠.𝑡𝑦𝑝𝑒 ← 𝑡h𝑖𝑟𝑑
# else if 𝑐𝑜𝑛𝑐𝑒𝑛𝑡𝑟𝑎𝑡𝑖𝑜𝑛(𝑛𝑠) ≥ 50 then
# 𝑛𝑠.𝑡𝑦𝑝𝑒 ← 𝑡h𝑖𝑟𝑑