from builtins import open, int, str, max
from .models import Degree

import _csv


def prepare_reqs(requirements):
    to_return = {}
    for y, reqs in requirements.items():
        global write_next, course_count, current_sem
        write_next = ""
        course_count = 1
        for r in reqs:
            to_add_to_sem = {}
            current_sem = ""
            if course_count > 4:
                current_sem = str(y) + "." + "2"
            else:
                current_sem = str(y) + "." + "1"

            if current_sem not in to_return:
                to_return[current_sem] = []

            if not (write_next == ""):
                to_return[write_next][(course_count - 2) % 2]["title"] = r

                course_count = course_count - 1
                write_next = ""
            else:
                if r.isupper():
                    write_next = current_sem
                    to_add_to_sem['code'] = r
                    to_return[current_sem].append(to_add_to_sem)
                else:
                    write_next = ""
                    to_add_to_sem["title"] = r
                    to_return[current_sem].append(to_add_to_sem)

            if course_count == 8:
                course_count = 1
            else:
                course_count += 1

    return to_return


def fill_degree_table():
    with open("degree/data/degree-info.csv") as degree_names:
        d = _csv.reader(degree_names, delimiter=";")
        degree_names = []
        for r in d:
            degree_names.append(r)
        with open('degree/data/program-reqs-table.csv') as degree_info:
            degrees = _csv.reader(degree_info)
            global current_code, current_name, requirements
            current_code = ""
            current_name = ""
            requirements = {}
            first_pass = True
            global year
            year = 0
            row_no = 0
            for row in degrees:

                code = row[0].lstrip()
                data = row[1].lstrip()
                if not (code.strip() == "" or code.strip() == "Code"):
                    if first_pass:
                        current_name = degree_names[row_no]
                        current_code = code
                        first_pass = False
                        continue
                    else:
                        row_no += 1
                    final_reqs = prepare_reqs(requirements)
                    name = lookup_name(current_code, degree_names)
                    d = Degree(code=current_code, name=name, requirements=final_reqs)
                    d.save()
                    year = 0
                    current_code = code
                    requirements = {}
                    continue

                if (year > 0 and not (data.strip() == "") and not "units" in data and not (
                        "year" in data or "Year" in data)):
                    requirements[year].append(data)

                if ("Year" in data[0:10]) or ("year" in data[0:10]):
                    l = [int(data) for data in data.split() if data.isdigit()]

                    if not (l == []):
                        year += 1
                    requirements[year] = []


def lookup_name(code, l):
    for pair in l:
        if (code == pair[0]):
            return pair[1]
    return "unknown"


def initialise_database():
    fill_degree_table()
