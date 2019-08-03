#!/bin/bash
# usage: populate_indices.sh <host address>

if [ $# -eq 0 ]
  then
    echo "ERROR: No host address provided (e.g. localhost)"
    echo "usage: populate_indices.sh <host address>"
    exit 1
fi 

curl -X DELETE "$1:9200/cbelists"
curl -X DELETE "$1:9200/majors"
curl -X DELETE "$1:9200/minors"
curl -X DELETE "$1:9200/specialisations"
curl -X DELETE "$1:9200/courses"
curl -X DELETE "$1:9200/courseupdated"


declare -a BULKS=("@course_bulk" "@degree_bulk" "@major_updated_bulk" "@minor_updated_bulk" "@specialisation_updated_bulk"  "@courselists_bulk" "@course_updated_bulk")

for bulk in "${BULKS[@]}"
do
    curl -s -H "Content-Type: application/x-ndjson" -XPOST $1:9200/_bulk --data-binary $bulk; echo 
done
