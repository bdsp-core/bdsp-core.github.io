import json
import pandas as pd


# NOTE!!! there is tags and new tags
# new_tags lacks the labels but is updated with the latest articles
# I advise extreme caution
df = pd.read_csv("tags.csv")
print(df)

with open("result.json", "r") as f:
    data = json.load(f)

tags = list(df.columns)[1:]
tagged_data = {"papers": [], "all_tags": tags}

for i in range(len(data)):
    this_entry = data[i]
    this_entry["tags"] = []
    for j in range(len(tags)):
        if df.iloc[i][j+1] == 1:
            this_entry["tags"].append(tags[j])
    tagged_data["posts"].append(this_entry)

print(tagged_data)

with open("tagged_results.json", "w") as f:
    json.dump(tagged_data, f, indent=2)

