import json
import re

# add list 1 first
with open('cbe-list-1.csv') as f:
    lines = f.readlines()

codes = []

for line in lines:
    if line.isspace() or len(line) < 8:
        continue
    code = line[:8]
    if re.match("[A-Z]{4}[0-9]{4}", code) is None:
        continue
    codes.append(code)

list_1 = {'type': "CBE List 1", 'courses': codes}

meta_data = {}
index = {'_index': 'courselists', '_type': '_doc', '_id': 1}
meta_data['index'] = index

print(json.dumps(meta_data))
print(json.dumps(list_1))


# add list 2
with open('cbe-list-2.txt') as f:
    lines = f.readlines()

codes = []

for line in lines:
    if line.isspace() or len(line) < 8:
        continue
    if ',' in line:
        courses = line.split(",")
        for i in range(len(courses)):
            courses[i] = courses[i].strip()
        codes.append(courses)
    else:
        codes.append([line[:8]])

list_2 = {'type': "CBE List 2", 'courses': codes}

meta_data = {}
index = {'_index': 'courselists', '_type': '_doc', '_id': 2}
meta_data['index'] = index
print(json.dumps(meta_data))
print(json.dumps(list_2))

