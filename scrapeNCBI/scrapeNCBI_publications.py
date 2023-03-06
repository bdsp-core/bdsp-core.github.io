# run this to download and parse the publications 
import requests
from bs4 import BeautifulSoup 

# there are 6 pages
URL = "https://www.ncbi.nlm.nih.gov/myncbi/m.%20brandon.westover.1/bibliography/public/?page=" + str(1)
# https://www.ncbi.nlm.nih.gov/myncbi/m.%20brandon.westover.1/bibliography/public/?page=1
pubdata = []

for i in range(1,6):
    URL = "https://www.ncbi.nlm.nih.gov/myncbi/m.%20brandon.westover.1/bibliography/public/?page=" + str(i)
    print(URL)
    page = requests.get(URL)
    soup = BeautifulSoup(page.text)
    mydivs = soup.find_all("div", {"class": "ncbi-docsum"})

    for div in mydivs:
        try:
            thisdata = {}
            thisdata["title"] = "\"" + div.find("a").text.strip() + "\""
            thisdata["image"] = ''
            thisdata["description"] = ''
            thisdata["authors"] = div.find("span", {"class": "authors"}).text.strip()
            link = "https://pubmed.ncbi.nlm.nih.gov/" + div.find("a").get("href").replace("pubmed", "").replace("/","")

            junk_stuff = ["source", "pubdate", "volume", "issue", "pages", "doi", "pubstatus", "pmid", "pmcid"]
            bigjunk = ""
            for junk in junk_stuff:
                try:
                    bigjunk += div.find("span", {"class": junk}).text.strip().replace("PubMed Central ","").replace("PubMed ", "").replace("\n","").replace("    ","")+ " "
                except:
                    pass
            display = bigjunk
            
            thisdata["link"] = {"url": link, "display": display}
            thisdata["highlight"] = 0

            pubdata.append(thisdata)
        except:
            pass

# print(pubdata)

# write yml file
import yaml

# - title: Development of expert-level automated detection of epileptiform discharges during electroencephalogram interpretation
#   image: dummy.png
#   description: "A deep neural network was trained using 9571 scalp electroencephalogram recordings. The algorithm appeared to perform at or above the accuracy, sensitivity, and specificity of fellowship-trained clinical experts."
#   authors:
#     Jing J, Sun H, Kim JA, Herlopian A, Karakis I, Ng M, Halford JJ, Maus D, Chan F, Dolatshahi M, Muniz C, Chu C, Sacca V, Pathmanathan J, Ge W, Dauwels J, Lam A, Cole AJ, Cash SS, Westover MB.
#   link:
#     url: https://doi.org/10.1001/jamaneurol.2019.3485
#     display: "JAMA Neurology. 2020 Jan 1;77(1):103-8. doi: 10.1001/jamaneurol.2019.3485. PMID: 31633740 PMCID: PMC6806668."
#   highlight: 0
with open('result.yml', 'w') as yaml_file:
    yaml.dump(pubdata, yaml_file, default_flow_style=False, sort_keys=False)

import json
with open("result.json", "w") as f:
    json.dump(pubdata, f, indent=2)

import csv
tags = ["eeg", "spike"]
blank_tags = [0 for t in tags]
with open("new_tags.csv", "w") as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(["TITLE"]+tags)
    for entry in pubdata:
        csvwriter.writerow([entry["title"].replace('"', '')]+blank_tags)

