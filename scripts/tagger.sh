#!/bin/bash

# Define a function named "print_help"
function print_help {
  echo "Usage: tagger.sh [-h] input_directory output_directory database_file"
  echo ""
}

# Check if the script has received three arguments
if [ $# -ne 3 ]; then
    print_help
    exit 1
fi

# check -h
if [ $1 == "-h" ]; then
    print_help
    exit 1
fi

for file in $1/*.jpg
do
    python3 tagger.py $file $2 $3
    echo $file
done