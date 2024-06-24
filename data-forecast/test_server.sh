#!/bin/bash

# URL do seu servidor e endpoint
export URL="http://localhost:8085/add_invocation"
export raw_dataset_dir="/home/claudiocorreia/backupStuff/AzureDataset/OriginalTraces/"

send_trace_data() {
    local trace_id="$1"
    
    # Number of lines to read from the CSV file
    NUM_LINES=400

    # Construct the file path using the trace_id
    local file_path="predictor/dataset_traces/traces_datapoints/${trace_id}.csv"

    # Check if the file exists
    if [[ ! -f "$file_path" ]]; then
        cd predictor/dataset_traces/
        python -c "import trace_generator; trace_generator.generate_and_plot_trace_id('${trace_id}', '${raw_dataset_dir}', '')"        
        cd ../../
    fi

    # Read the specified number of lines from the CSV file
    head -n $NUM_LINES "$file_path" | while IFS=',' read -r item_id timestamp target; do
        # Ignore the header line of the CSV
        if [[ "$item_id" == "item_id" ]]; then
            continue
        fi

        # Format the timestamp into the desired format ("2019-01-01 00:00:00")
        timestamp_formatted=$(date -d "$timestamp" +"%Y-%m-%d %H:%M:%S")

        # Build the JSON data for the POST body
        data='{"timestamp":"'$timestamp_formatted'", "trace_id":"'$item_id'", "invocation_count":"'$target'"}'

        # Send the POST request using curl
        echo "Sending POST for timestamp $timestamp_formatted with target $target  "
        curl -X POST $URL -H "Content-Type: application/json" -d "$data"
        echo
    done
}

send_trace_data "c69576eccda1d707aa642f3989a794831cd88dd4368e07c93d54f26245d33f94"
send_trace_data "0bbf3ed03a8bd9360b056421dc63bf3ad0a12f34f158a23ed762fe78256fa4c8"

curl -X GET http://localhost:8085/compute_leaderboard

