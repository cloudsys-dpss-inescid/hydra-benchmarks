#!/bin/bash

file="plot_restore.py"

if [ -f "$file" ]; then
    line_count=$(wc -l < "$file")
else
    line_count=0
fi

echo $line_count

if [ "$line_count" -eq 2 ]; then
    echo "Appending times with graalvisor modifications"
elif [ "$line_count" -eq 39 ]; then
    echo "You already have a working dataset. Delete?"
    read -rp "Delete $file? y/n: " user_answer

    if [ "$user_answer" = "y" ]; then
        echo "Deleting..."
	rm -f "$file"
    else
        echo "Dataset kept."
	exit
    fi

else
    echo "Deleting file..."
    rm -f "$file"
fi

echo -e "nyyyy" | ./run-experiment.sh

test_names=()
process_times=()

for dir in ../results/benchmark/java/*/1/; do
    [ -d "$dir" ] || continue
    dir_name=$(basename "$(dirname "$dir")")

    # Only proceed if dir_name contains '-snapshot'
    [[ "$dir_name" == *-snapshot-* ]] || continue

    # Remove the first 3 characters of dir_name and strip everything after "-svm"
    dir_name=$(echo "$dir_name" | sed -E 's/^...//; s/-svm.*//')

    test_names+=("\"$dir_name\"")


    # Extract from normal.log
    app_log="$dir/app.log"
    if [ -f "$app_log" ]; then
        extracted_numbers=($(grep -e "process time" "$app_log" | grep -o '[0-9]\+'))
        process_times+=("${extracted_numbers[0]:-0}")
    else
        echo "couldn't find 'process time' for $(dir_name)"
        process_times+=(0)
    fi
done

# Function to join arrays with commas
join_with_commas() {
    local IFS=,
    echo "$*"
}

# Output Python arrays
echo "benchmark_labels = [$(join_with_commas "${test_names[@]}")]"
echo "process_times = [$(join_with_commas "${process_times[@]}")]"

# if we deleted the file we want to set benchmark_labels and restored_times
# otherwise we want to save modified_times instead of restored_times
if [ ! -f "$file" ]; then
    echo "benchmark_labels = [$(join_with_commas "${test_names[@]}")]" >> "$file"
    echo "restore_times = [$(join_with_commas "${process_times[@]}")]" >> "$file"
    echo "Dont' forget to 1. Modify and recompile the application and 2. call this script again !!!"
else
    echo "modified_times = [$(join_with_commas "${process_times[@]}")]" >> "$file"
    cat "template.py" >> "$file"
    python3 $file
fi

