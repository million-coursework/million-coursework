import pandas as pd
import re

d=pd.read_csv("program-reqs.csv", encoding='latin-1')

count_index = 1
degrees = set()

for index, row in d.iterrows():
    if True:
        code =str(row[0])
        requirements = str(row[1])
        degree_name = str(row[2])
        
        if degree_name in degrees:
            continue
        
        degrees.add(degree_name)
        
        # sanitize the strings
        code = code.replace('"', '')
        requirements = requirements.replace('"', '')
        degree_name = degree_name.replace('"', '')
        
        code = code.replace("åÊ", ' ')
        requirements = requirements.replace("åÊ", ' ')
        requirements = requirements.replace('\', ' ')
        requirements = requirements.replace('\\', ' ')
        degree_name = degree_name.replace('\\', ' ')
        code = code.replace('\\', ' ')
        requirements = ' '.join(requirements.split())
        degree_name = ' '.join(degree_name.split())
        code = ' '.join(code.split())
        requirements = requirements.replace('\t', ' ')
        degree_name = degree_name.replace('\t', ' ')
        code = code.replace('\t', ' ')
        requirements = requirements.replace('\n', ' ')
        degree_name = degree_name.replace('\n', ' ')
        code = code.replace('\n', ' ')
        requirements = requirements.replace('{', ' ')
        requirements = requirements.replace('{', ' ')
        requirements = requirements.replace('}', ' ')
        requirements = requirements.replace('}', ' ')
        
        regex = "^[A-Za-z0-9 ]*[A-Za-z0-9][A-Za-z0-9 ]*"
        re.match(regex, requirements)
        
        # form the JSON
        print("{ \"index\" : { \"_index\": \"degrees\", \"_type\": \"_doc\" ,\"_id\": \"" + str(count_index) +"\"}}")
        count_index += 1
        print("{ \"code\":\"" + code +"\", \"name\":\"" + degree_name + "\" }")
       
