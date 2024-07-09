#!/bin/bash

# File containing the trace IDs (one per line)
TRACE_FILE="simulation_trace_ids.txt"
raw_dataset_dir="../../../azure-dataset/input/"
N_PARTS=80

echo "Running simulator!"

wait_for_server() {
    
    printf 'Connecting to server.'
    until $(nc -z $1 $2 2>/dev/null); do
        printf '.'
        sleep 2
    done

    echo "Server is up!"
}

send_trace_data() {
    local trace_id=$(echo "$1" | tr -d '\r\n') #I no longer need to clean the data
    local address="$2"
    local port="$3"
    echo "sending points for $trace_id"
    
    # Number of lines to read from the CSV file
    NUM_LINES=200
    local file_path="../predictor/dataset_traces/traces_datapoints/${trace_id}.csv"

    # Check if the file exists
    if [[ ! -f "$file_path" ]]; then
        cd ../predictor/dataset_traces/
        python -c "import trace_generator; trace_generator.generate_and_plot_trace_id('${trace_id}', '${raw_dataset_dir}', '')"        
        cd ../../simulator/
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

        curl -X POST "http:///$address:$port/add_invocation" -H "Content-Type: application/json" -d "$data" > /dev/null 2>&1

    done
}

process_request_on_isolated_service() {
    
    local my_id="$1"
    local trace_id="$2"
    local address="localhost"
    local port=$(printf 7"%03d" $my_id) #"8055"
    local container_name="timeseries-predictor-container-${my_id}"
    
    cd ../service/
    ./run_server_container.sh $port $container_name
    cd ../simulator/

    # Wait until the server is ready
    wait_for_server $address $port

    #echo " aqui ----- ${trace_id}"
    send_trace_data $trace_id $address $port

    echo "leaderboard:"
    { time curl -s -X GET "http://$address:$port/compute_leaderboard" ; } >> "debug/service-$my_id.log" 2>&1

    docker stop $container_name

}

# Function to process a list of trace IDs
process_trace_ids() {
    local my_id="$1"
    shift
    local trace_ids=("$@")
    local address="localhost"
    local port=$(printf 7"%03d" $my_id) #"8055"
    local container_name="timeseries-predictor-container-${my_id}"
    local counter=0

    # Clear the log file
    > "debug/service-$my_id.log"


    cd ../service/
    ./run_server_container.sh $port $container_name
    cd ../simulator/

    # Wait until the server is ready
    wait_for_server $address $port
    
    #echo "Processing trace IDs for part $my_id:"
    for trace_id in "${trace_ids[@]}"; do
        
        echo "Thread ID: $my_id - Trace ID: $trace_id"
        
        trace_id=$(echo "$trace_id" | tr -d '\r\n') #clean the \r 
        #process_request_on_isolated_service "$my_id" "$trace_id"
        send_trace_data $trace_id $address $port

        { time curl -s -X GET "http://$address:$port/compute_leaderboard" ; } >> "debug/service-$my_id.log" 2>&1

        # remove previux request
        data='{"trace_id":"'$trace_id'"}'

        curl -X POST "http:///$address:$port/remove_trace_by_id" -H "Content-Type: application/json" -d "$data"  > /dev/null 2>&1
        
        
        counter=$((counter + 1))
        if (( counter % 20 == 0 )); then #relaunch container
            counter=0
            docker stop $container_name

            cd ../service/
            ./run_server_container.sh $port $container_name
            cd ../simulator/

            # Wait until the server is ready
            wait_for_server $address $port

        fi

    done


    docker stop $container_name


}

# Read the trace IDs into an array
mapfile -t trace_ids < "$TRACE_FILE"

# Calculate the number of trace IDs per part
total_trace_ids=${#trace_ids[@]}
ids_per_part=$(( (total_trace_ids + N_PARTS - 1) / N_PARTS ))

# Divide the trace IDs into N parts and process each part in the background
for (( i=0; i<N_PARTS; i++ )); do
    start_index=$(( i * ids_per_part ))
    end_index=$(( start_index + ids_per_part ))
    
    # Extract the subset of trace IDs for this part
    part_trace_ids=("${trace_ids[@]:start_index:ids_per_part}")

    # Call the processing function in the background
    process_trace_ids "$i" "${part_trace_ids[@]}" &
done

# Wait for all background processes to complete
wait

echo "All trace IDs processed."

