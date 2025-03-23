#!/bin/bash

test_names=()
process_times=()

for dir in ../results/benchmark/java/*/; do
    [ -d "$dir" ] || continue

    # Extract just the directory name without path or trailing slash
    dir_name=${dir%/}      # Remove trailing slash
    dir_name=${dir_name##*/}  # Remove everything before the last /

    # Only proceed if dir_name contains '-snapshot'
    [[ "$dir_name" == *-snapshot-* ]] || continue

    # Remove the first 3 characters of dir_name and strip everything after "-svm"
    dir_name=$(echo "$dir_name" | sed -E 's/^...//; s/-svm.*//')

    test_names+=("\"$dir_name\"")

    total_time=0
    count=0

    subdir="${dir}/5/"
    echo $subdir
        # Extract from normal.log
        app_log="$subdir/app.log"
        if [ -f "$app_log" ]; then
            extracted_numbers=($(grep -e "process time" "$app_log" | grep -o '"process time (us)":[0-9]\+' | grep -o '[0-9]\+'))
	    echo "${extracted_numbers[@]}"

	    for num in "${extracted_numbers[@]}"; do
                total_time=$((total_time + num))
		count=$((count + 1))
	    done

	    average=$((total_time / count))
	    echo $average
	    process_times+=($average)
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
