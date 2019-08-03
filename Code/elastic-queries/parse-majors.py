import pandas as pd
import re
import numpy as np
import json

data = pd.read_excel('Tabulated Major,Minor,Spec.xlsx')

doc_index = 0

codes = set()

for index, row in data.iterrows():
    if str(row[0]) == "nan" or str(row[1]) == "nan":
        continue
    
    text_desc = ' '.join(row[2].split())
    text_desc = text_desc.replace('(', '')
    text_desc = text_desc.replace(')', '')

    if row[0] in codes:
        continue

    codes.add(row[0])
    
    meta_data = {}
    meta_index = {}
    meta_index['_index'] = 'majors'
    meta_index['_type'] = '_doc'
    meta_index['_id'] = int(doc_index + 1)
    meta_data['index'] = meta_index
    doc_index += 1
    
#    if row[0] != "CPMK-MAJ":
#        continue

    
# different phrases include
# R1: "_ units from completion of the following courses:"
# R2: "A _ of _ units of courses at _ level" <-- 1000/3000 etc.
# R3: "A _ of _ units may come from completion of courses from the following list:"
# R4: "_ units from completion of the following compulsory courses"
# R5: "_ units from completion of courses from the following list:"
# R6: "_ units from completion of courses from the subject area _" <-- STAT, BUSN etc.
# 
    
#     print(z)
#     print("**")
    major = {}
    major['code'] = row[0]
    major['name'] = row[1]
    compositions = []

    # For all regexes,
    #   get matches in string
    #   split along the matches
    #      search for course code in each split
    
    regexes = [
        "([0-9]* units from completion of the following courses:)",
        "(A (maximum)*(minimum)* of [0-9]* units of courses at [0-9]* level)",
        "(A (maximum)?(minimum)? of [0-9]* units (must)*(may)* come from completion of courses from the following list:)",
        "([0-9]* units from completion of the following compulsory courses:)",
        "([0-9]* units from completion of courses from the following list:)",
        "([0-9]* units from completion of courses from the subject area [A-Z]{4})",
    ]
    
    # Not parsing the regexes in a loop because the JSON formed depends on the regex.
    # In hindsight, it probably was better to go off with a loop. But since the deed has been done, I'll live with it
    
    # REGEX 0
    partitions = re.findall(regexes[0], text_desc)
    indices = []
    for c, match in enumerate(partitions):
        indices.append(partitions[:(c + 1)].count(match))

    for c, partition in enumerate(partitions):
        if type(partition) is tuple:
            partition = partition[0]
        rules = {}
        rules['type'] = "minimum"
        rules['units'] = int((partition.split())[0])
        courses = []
        bad_text = (text_desc.split(partition))[indices[c]]
        
        # get a rough idea of where the next section begins
        try:
            approx_index = bad_text.index("course")
        except:
            approx_index = 10000 # this is the end, hold your breath and count to 10
        
        bad_text = bad_text[:approx_index]
        words = bad_text.split()
        total_section_units = 0
        for element in words:
            m = re.match("(^[A-Z]{4}[0-9]{4}$)", element)
            if m:
                course = {}
                course['code'] = m.groups()[0]
                course['units'] = 6
                total_section_units += course['units']
                courses.append(course)
        rules['course'] = courses
        if total_section_units == rules['units']:
            rules['type'] = 'fixed'
        compositions.append(rules)
     
    
    # REGEX 1
    partitions = re.findall(regexes[1], text_desc)
    indices = []
    for c, match in enumerate(partitions):
        indices.append(partitions[:(c + 1)].count(match))

    for c, partition in enumerate(partitions):
        if type(partition) is tuple:
            partition = partition[0]
        p_split = partition.split()
        rules = {}
        rules['type'] = p_split[1]
        rules['units'] = int(p_split[3])
        courses = [{'level': p_split[8]}]
        rules['course'] = courses
        compositions.append(rules)
    
    # REGEX 2
    partitions = re.findall(regexes[2], text_desc)
    indices = []
    for c, match in enumerate(partitions):
        indices.append(partitions[:(c + 1)].count(match))

    for c, partition in enumerate(partitions):
        if type(partition) is tuple:
            partition = partition[0]
        p_split = partition.split()
        rules = {}
        rules['type'] = p_split[1]  # maximum/minimum 
        rules['units'] = int(p_split[3])
        courses = []
        bad_text = (text_desc.split(partition))[indices[c]]
        
        # get a rough idea of where the next section begins
        try:
            approx_index = bad_text.index("course")
        except:
            approx_index = 10000 # this is the end, hold your breath and count to 10
        
        bad_text = bad_text[:approx_index]
        words = bad_text.split()
        for element in words:
            m = re.match("(^[A-Z]{4}[0-9]{4}$)", element)
            if m:
                course = {}
                course['code'] = m.groups()[0]
                course['units'] = 6

                courses.append(course)
        rules['course'] = courses
        compositions.append(rules)
        
    # REGEX 3
    partitions = re.findall(regexes[3], text_desc)
    indices = []
    for c, match in enumerate(partitions):
        indices.append(partitions[:(c + 1)].count(match))

    for c, partition in enumerate(partitions):
        if type(partition) is tuple:
            partition = partition[0]
        rules = {}
        rules['type'] = "minimum"
        rules['units'] = int((partition.split())[0])
        courses = []
        bad_text = (text_desc.split(partition))[indices[c]]
        
        # get a rough idea of where the next section begins
        try:
            approx_index = bad_text.index("course")
        except:
            approx_index = 10000 # this is the end, hold your breath and count to 10
        
        bad_text = bad_text[:approx_index]
        words = bad_text.split()
        total_section_units = 0
        for element in words:
            m = re.match("(^[A-Z]{4}[0-9]{4}$)", element)
            if m:
                course = {}
                course['code'] = m.groups()[0]
                course['units'] = 6
                total_section_units += course['units']
                courses.append(course)
        rules['course'] = courses
        if total_section_units == rules['units']:
            rules['type'] = 'fixed'
        compositions.append(rules)
        
    # REGEX 4
    partitions = re.findall(regexes[4], text_desc)
    indices = []
    for c, match in enumerate(partitions):
        indices.append(partitions[:(c + 1)].count(match))

    for c, partition in enumerate(partitions):
        if type(partition) is tuple:
            partition = partition[0]
        rules = {}
        rules['type'] = "minimum"
        rules['units'] = int((partition.split())[0])
        courses = []
        bad_text = (text_desc.split(partition))[indices[c]]
        
        # get a rough idea of where the next section begins
        try:
            approx_index = bad_text.index("course")
        except:
            approx_index = 10000 # this is the end, hold your breath and count to 10
        
        bad_text = bad_text[:approx_index]
        words = bad_text.split()
        total_section_units = 0

        # check
        
        for element in words:
            m = re.match("(^[A-Z]{4}[0-9]{4}$)", element)
            if m:
                course = {}
                course['code'] = m.groups()[0]
                course['units'] = 6
                total_section_units += course['units']
                courses.append(course)
        rules['course'] = courses
        if total_section_units == rules['units']:
            rules['type'] = 'fixed'
        compositions.append(rules)
        
    # REGEX 5
    partitions = re.findall(regexes[5], text_desc)
    indices = []
    for c, match in enumerate(partitions):
        indices.append(partitions[:(c + 1)].count(match))

    for c, partition in enumerate(partitions):
        if type(partition) is tuple:
            partition = partition[0]
        p_split = partition.split()
        rules = {}
        rules['type'] = "minimum"
        rules['units'] = int(p_split[0])
        courses = [{'area': p_split[10]}]
        rules['course'] = courses
        compositions.append(rules)
    
    major['composition'] = compositions
    print(json.dumps(meta_data))
    print(json.dumps(major))
