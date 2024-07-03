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

send_trace_data() {
    local trace_id="$1"
    
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

# Send trace data
#send_trace_data "c69576eccda1d707aa642f3989a794831cd88dd4368e07c93d54f26245d33f94"


# Read the file line by line from a online traces
traces_location="online_trace_ids.txt"
while IFS= read -r line
do
    trace_id=$(echo "$line" | tr -d '\r\n')
    echo "sending points for $trace_id"
    send_trace_data "$trace_id"
done < "$traces_location"
        
#send_trace_data "0bbf3ed03a8bd9360b056421dc63bf3ad0a12f34f158a23ed762fe78256fa4c8"
#send_trace_data "d620f3838e8985a166b8715a4071e63cb78c4a97b5fbc55f1afc07373493f160"
#send_trace_data "d2c14a262ab4b723d197cd12b7543518dbe8d29dd9b8cbd921c5003d3d7fc252"
#send_trace_data "d01f39bd08833e5f3c3b1f955d0b7ae61ae04b6aae9b6b73ab83365bb023ea3a"
#send_trace_data "d1e533e2931419c2f2fd52a331ac67ad8a69f533c56d1b12a0ac6cf46b426901"
#send_trace_data "d1cf09b1700cf827ee242a61b7744f71a5d5b9c2faf5ed915ad77a67d61dc6e9"
#send_trace_data "d0f0dd6a06162b4431c8ca772059f887cff5a3ef2d47bee83e020f364f67bc88"
#send_trace_data "cd127839cad8213d7c7b6359bafe76867670eff3c13befdc92595272c9e969ce"
#send_trace_data "cd7f16fcccee2be1f58f4e041bceaddb1b4de832eb22b1a8d6e6de1e76bed5ab"

#remove a trace
#curl -X POST http://localhost:8085/remove_trace_by_id -H "Content-Type: application/json" -d '{"trace_id":"0bbf3ed03a8bd9360b056421dc63bf3ad0a12f34f158a23ed762fe78256fa4c8"}'

# Request leaderboard
echo "leaderboard:"
time curl -X GET http://localhost:8085/compute_leaderboard

sleep 5

docker stop timeseries-predictor-container
