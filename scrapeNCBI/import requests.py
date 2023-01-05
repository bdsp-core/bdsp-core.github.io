import requests
from bs4 import BeautifulSoup 

URL = "https://www.ncbi.nlm.nih.gov/myncbi/m.%20brandon.westover.1/bibliography/public/"
page = requests.get(URL)
soup = BeautifulSoup(page.text)
mydivs = soup.find_all("div", {"class": "ncbi-docsum"})

pubdata = []
for div in mydivs:
	thisdata = {}
	print(div.find_all("span")[0].get("authors"))
	thisdata["authors"] = div.find_all("span")[0].get("authors").text
	thisdata["link"] = "https://pubmed.ncbi.nlm.nih.gov/" + div.find_all("a")[0].get("href").replace("pubmed", "").replace("/","")
	thisdata["title"] = div.find("span", {"class": "source"}).text.strip()

	junk_stuff = ["pubdate", "volume", "issue", "pages", "doi", "pubstatus", "pmid", "pmcid"]
	junk = ""
	for junk in junk_stuff:
		junk += div.find("span", {"class": junk}).text.strip().replace("PubMed Central ","").replace("PubMed ", "")
	thisdata["display"] = thisdata["title"] + junk

	pubdata.append(thisdata)

# print(pubdata)