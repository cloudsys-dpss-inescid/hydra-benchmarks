#!/usr/bin/bash
set -e

# This script must be placed in the same directory with dataset's csv files
# Example of use:
# bash split.sh d01 8
# This script accepts two arguments: dataset id and number of splits

# Splitting file
dataset_id=$1
num_files=$2
dataset_file="invocations_per_function_md.anon.${dataset_id}.csv"
total_lines=$(wc -l <${dataset_file})
total_lines=$((total_lines-1))   # do not consider the header line
((lines_per_file = (total_lines + num_files - 1) / num_files))

tail -n +2 ${dataset_file} | split -d -l ${lines_per_file} - ${dataset_id}_split_
for file in ${dataset_id}_split_*
do
    head -n 1 ${dataset_file} > tmp_file
    cat "$file" >> tmp_file
    mv -f tmp_file "$file"
done

echo "Total lines     = ${total_lines}"
echo "Lines  per file = ${lines_per_file}"

# Running python processes

for file in ${dataset_id}_split_*
do
    python3 process_split.py "$file" > /dev/null &
done
wait

python3 merge_splits.py "$dataset_id"

# Cleanup

for file in ${dataset_id}_split_*
do
    rm "$file"
done

for file in result_${dataset_id}_split_*
do
    rm "$file"
done
