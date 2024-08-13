#!/bin/bash

# File containing the trace IDs (one per line)
TRACE_FILE="simulation_trace_ids.txt"
raw_dataset_dir="../../../azure-dataset/input/"
#N_PARTS=50
# Number of lines to read from the CSV file
#NUM_LINES=1000
#START_NUM_LINES=5760

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
    #echo "sending points for $trace_id"
    

    local file_path="../data_manager/data/complete_traces/traces_datapoints/${trace_id}.csv"

    # Check if the file exists
    if [[ ! -f "$file_path" ]]; then
        cd ../predictor/dataset_traces/
        python -c "import trace_generator; trace_generator.generate_and_plot_trace_id('${trace_id}', '${raw_dataset_dir}', '')"        
        cd ../../simulator/
    fi

    local lines_in_file=$(wc -l < "$file_path")
    local line_to_begin=$START_NUM_LINES
    local lines_end_interval=lines_start_interval 

    local batch_lines_to_send=800

    local lines_sended=0

    while [ $lines_sended -lt $NUM_LINES ] && [ $((line_to_begin + lines_sended)) -lt $lines_in_file ]; do
        lines_to_send=$((batch_lines_to_send))
        remaining_lines_in_file=$((lines_in_file - (line_to_begin + lines_sended)))
        remaining_lines_to_read=$((NUM_LINES - lines_sended))

        if [ $lines_to_send -gt $remaining_lines_in_file ]; then
            lines_to_send=$remaining_lines_in_file
        fi

        if [ $lines_to_send -gt $remaining_lines_to_read ]; then
            lines_to_send=$remaining_lines_to_read
        fi

        lines_start_index=$((line_to_begin - lines_sended))
        #echo "send $lines_to_send lines, starting in $lines_start_index"

        post_data="["
        first_line_in_trace=true
        # Read the specified number of lines from the CSV file
        while IFS=',' read -r item_id timestamp target; do
            # Ignore the header line of the CSV
            if [[ "$item_id" == "item_id" ]]; then
                continue
            fi
            
            # Ignore empty lines, I do not know why there are some in the file
            if [[ "$target" == "" ]]; then
                continue
            fi

            if [ "$first_line_in_trace" = false ] ; then
                post_data=$post_data","
            fi
            first_line_in_trace=false

            # Format the timestamp into the desired format ("2019-01-01 00:00:00")
            timestamp_formatted=$(date -d "$timestamp" +"%Y-%m-%d %H:%M:%S")

            post_data=$post_data'{\"timestamp\":\"'$timestamp_formatted'\", \"item_id\":\"'$item_id'\", \"target\":\"'$target'\"}'
            # Build the JSON data for the POST body

        done < <(sed -n "$lines_start_index,$(($lines_start_index + $lines_to_send - 1))p" "$file_path")


        post_data=$post_data"]"
        data='{"dataframe":"'$post_data'", "trace_id":"'$trace_id'", "invocation_duration":"2", "memory_used_invocation":"100", "compilation_cost":"100"}'
        curl -X POST "http:///$address:$port/add_dataframe" -H "Content-Type: application/json" -d "$data" #> /dev/null 2>&1
        
        lines_sended=$((lines_sended + lines_to_send))
    done

}


# Function to process a list of trace IDs
process_trace_ids() {
    local my_id="$1"
    shift
    local trace_ids=("$@")
    local address="localhost"
    local port="8055"
    local counter=0

    # Clear the log file
    > "debug/service-$my_id.log"

    
    echo "Processing trace IDs for part $my_id:"
    for trace_id in "${trace_ids[@]}"; do
        #echo "Thread ID: $my_id - Trace ID: $trace_id"
        
        
        trace_id=$(echo "$trace_id" | tr -d '\r\n') #clean the \r 
        #process_request_on_isolated_service "$my_id" "$trace_id"
        send_trace_data $trace_id $address $port >> "debug/service-$my_id.log" 2>&1

        #{ time curl -s -X GET "http://$address:$port/compute_leaderboard" ; } >> "debug/service-$my_id.log" 2>&1

        # remove previux request
        #data='{"trace_id":"'$trace_id'"}'
        #curl -X POST "http:///$address:$port/remove_trace_by_id" -H "Content-Type: application/json" -d "$data"  > /dev/null 2>&1


    done


}


upload_all_traces() {

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

}

simulate() {

    cd ../service/
    ./run_server_container.sh $port $container_name
    cd ../simulator/

    # Wait until the server is ready
    wait_for_server $address $port

    # Set predictor mode
    data='{"predictor_mode":"'$PREDICTOR_MODE'"}'
    curl -X POST "http:///$address:$port/set_predictor_mode" -H "Content-Type: application/json" -d "$data"  > /dev/null 2>&1    

    tmp_start_index=$START_NUM_LINES
    for (( j=0; j<NUMBER_OF_LEADERBOARDS; j++ )); do

        # check if I am going to send points and then compute leaderboard at the end of simulate dataset, 14 days = 20160 minutes
        if [ $((tmp_start_index + NUM_LINES)) -ge 20160 ]; then
            break
        fi

        upload_all_traces 
        echo "compute_leaderboard"
        time curl -s -X GET "http://$address:$port/compute_leaderboard" >> "${result_dir}/leaderboard-${PREDICTOR_MODE}-${NUM_LINES}-${tmp_start_index}.log" 2>&1
        tmp_start_index=$(($tmp_start_index + $NUM_LINES)) #adding more 200 points to the service
        
    done
    
    #read -p "Press Enter to continue: " fullname

    docker stop $container_name

}

port="8055"
container_name="timeseries-predictor-container"
address="localhost"


# Read the trace IDs into an array
mapfile -t trace_ids < "$TRACE_FILE"
result_dir=$(mktemp -d results/forcast-$(whoami)-XXXXXXXX)




N_PARTS=50
START_NUM_LINES=10080
NUMBER_OF_LEADERBOARDS=4

## run for autogluon models
PREDICTOR_MODE="custom_autogluon" #average, oracle and custom_autogluon 
NUM_LINES=1600
simulate

NUM_LINES=1440
simulate

NUM_LINES=2880
simulate

NUM_LINES=4320
simulate

## run for oracle
PREDICTOR_MODE="oracle"
NUM_LINES=1600
simulate

NUM_LINES=1440
simulate

NUM_LINES=2880
simulate

NUM_LINES=4320
simulate

## run for average
PREDICTOR_MODE="average"
NUM_LINES=1600
simulate

NUM_LINES=1440
simulate

NUM_LINES=2880
simulate

NUM_LINES=4320
simulate

#echo "All trace IDs processed."
echo Folder containing the execution log: $result_dir
