#!/bin/bash

# Server URL and endpoint
export URL="http://localhost:8085/add_invocation"
export raw_dataset_dir="/home/claudiocorreia/backupStuff/AzureDataset/OriginalTraces/"

# Function to check if the server is ready
wait_for_server() {
    
    printf 'Connecting to server.'
    until $(nc -z localhost 8085 2>/dev/null); do
        printf '.'
        sleep 2
    done

    echo "Server is up!"
}

# Launch the container in the background and redirect output to server.log
./run_server_container.sh

# Wait until the server is ready
wait_for_server $URL

#Exaempl ao to usesend_trace_data "0bbf3ed03a8bd9360b056421dc63bf3ad0a12f34f158a23ed762fe78256fa4c8"
send_trace_data() {
    local trace_id=$(echo "$1" | tr -d '\r\n')
    echo "sending points for $trace_id"
    
    # Number of lines to read from the CSV file
    NUM_LINES=200

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
        
        # Ignore empty lines, I do not know why there are some in the file
        #if [[ "$target" == "" || "$target" == "0" ]]; then
        if [[ "$target" == "" ]]; then
            continue
        fi

        # Format the timestamp into the desired format ("2019-01-01 00:00:00")
        timestamp_formatted=$(date -d "$timestamp" +"%Y-%m-%d %H:%M:%S")

        # Build the JSON data for the POST body
        data='{"timestamp":"'$timestamp_formatted'", "trace_id":"'$item_id'", "invocation_count":"'$target'", "invocation_duration":"2", "memory_used_invocation":"100", "compilation_cost":"100"}'

        # Send the POST request using curl
        #echo "Sending POST for timestamp $timestamp_formatted with target $target  "
        curl -X POST $URL -H "Content-Type: application/json" -d "$data" > /dev/null 2>&1
        #echo
    done
}

# Read the file line by line from a online traces
traces_location="online_trace_ids.txt"
export -f send_trace_data
#using xargs to parallelize this part, the -P defines how many threads
cat "$traces_location" | xargs -I {} -P 40 bash -c 'send_trace_data "$@"' _ {}

#remove a trace
#curl -X POST http://localhost:8085/remove_trace_by_id -H "Content-Type: application/json" -d '{"trace_id":"0bbf3ed03a8bd9360b056421dc63bf3ad0a12f34f158a23ed762fe78256fa4c8"}'

# Request leaderboard
echo "leaderboard:"
time curl -X GET http://localhost:8085/compute_leaderboard

sleep 1

docker stop timeseries-predictor-container
