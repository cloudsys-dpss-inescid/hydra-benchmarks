#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/benchmarks.sh

function test_gv_benchmarks {
    TEST_SET=""
    read -p "Test Graalvisor's Java benchmarks (y or Y, everything else as no)? " -n 1 -r
    echo    # move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        TEST_SET="$TEST_SET $JV_GV_BENCHMARKS"
    fi
    read -p "Test Graalvisor's Python benchmarks (y or Y, everything else as no)? " -n 1 -r
    echo    # move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        TEST_SET="$TEST_SET $PY_GV_BENCHMARKS"
    fi
    read -p "Test Graalvisor's JavaScript benchmarks (y or Y, everything else as no)? " -n 1 -r
    echo    # move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        TEST_SET="$TEST_SET $JS_GV_BENCHMARKS"
    fi
    read -p "Print times of restore? " -n 1 -r PRINT_TIMES
    echo    # move to a new line
    if [[ $PRINT_TIMES =~ ^[Yy]$ ]]
    then
        export ITERATIONS=5
        echo $PRINT_TIMES
    fi

    for benchmark in $TEST_SET
    do
        for backend in "svm" #"container" "vm"
        do
            echo "$(tput bold)Benchmark: $benchmark in $backend $(tput sgr0)"
            rm -rf $ADIR
            export SANDBOX="default"; $(DIR)/benchmark-graalvisor.sh $backend $benchmark test 1 | grep "Req output:"
            export SANDBOX="process"; $(DIR)/benchmark-graalvisor.sh $backend $benchmark test 1 | grep "Req output:"
            if [[ $benchmark == *"gv_java_classify"* || $benchmark == *"videoprocessing"* ]]; then
                echo "Skipping $benchmark (not supported)"
                continue
            fi
            if [[ $benchmark == *"_thumbnail"* || $benchmark == *"gv_python_dynamichtml"* || $benchmark == *"gv_python_compression"* ]]; then
                echo "Skipping $benchmark (not supported)"
                continue
            fi
            export WARMUP=1
            # Create the snapshot.
            export SANDBOX=snapshot; $(DIR)/benchmark-graalvisor.sh $backend $benchmark test 0 | grep "Req output:"
            # Restore from the snapshot.
            export SANDBOX=snapshot; $(DIR)/benchmark-graalvisor.sh $backend $benchmark test 0 | grep "Req output:"
            unset WARMUP
        done
    done
    unset SANDBOX
    # after running benchmarks, print restore times
    if [[ $PRINT_TIMES =~ ^[Yy]$ ]]
    then
	    get_times
    fi
}

function get_times {
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
}

function test_ow_benchmarks {
    TEST_SET=""
    read -p "Test OpenWhisk's Java benchmarks (y or Y, everything else as no)? " -n 1 -r
    echo    # move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        TEST_SET="$TEST_SET $JV_CR_BENCHMARKS"
    fi
    read -p "Test OpenWhisk's Python benchmarks (y or Y, everything else as no)? " -n 1 -r
    echo    # move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        TEST_SET="$TEST_SET $PY_CR_BENCHMARKS"
    fi
    read -p "Test OpenWhisk's JavaScript benchmarks (y or Y, everything else as no)? " -n 1 -r
    echo    # move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        TEST_SET="$TEST_SET $JS_CR_BENCHMARKS"
    fi

    for benchmark in $TEST_SET
    do
        for backend in "container" "vm"
        do
            $(DIR)/benchmark-cruntime.sh $backend $benchmark test 1
        done
    done
}

function measure_benchmark_resources {
    declare -A conc_mem_table
    declare -A conc_cpu_table
    conc_mem_table[1]=2048
    conc_cpu_table[1]=100000
    conc_mem_table[2]=1024
    conc_cpu_table[2]=50000
    conc_mem_table[4]=512
    conc_cpu_table[4]=25000
    conc_mem_table[8]=256
    conc_cpu_table[8]=12500

    for concurrency in 1 2 4 8;
    do
        for benchmark in $GV_BENCHMARKS $CR_BENCHMARKS;
        do
            concurrency_table["$benchmark"]=$concurrency
            mem_table["$benchmark"]=${conc_mem_table["$concurrency"]}
            cpu_table["$benchmark"]=${conc_cpu_table["$concurrency"]}
        done
        efficiency
    done
}

function cold_start_latency {
    export EXPERIMENT="coldstart"
    cr_benchmark=cr_python_hw
    gv_benchmark=gv_python_hw

    function context_snapshot {
        export WARMUP=1
        export SANDBOX=context-snapshot
        rm -rf $ADIR/*.memsnap $ADIR/*.metasnap
        $(DIR)/benchmark-graalvisor.sh svm $gv_benchmark test 0
        unset SANDBOX
        unset WARMUP
    }

    function process_snapshot {
        export SNAPSHOT=$SDIR/$gv_benchmark
        rm -rf $SNAPSHOT
        $(DIR)/benchmark-graalvisor.sh svm $gv_benchmark test 1
        unset SNAPSHOT
    }

    function vm_snapshot {
        export SNAPSHOT=$SDIR/$gv_benchmark
        rm -rf $SNAPSHOT.{disk,mem,snap}
        $(DIR)/benchmark-graalvisor.sh vm $gv_benchmark test 1
        unset SNAPSHOT
    }

    # TODO - use cgroups?
    $(DIR)/benchmark-cruntime.sh   container $cr_benchmark test 1
    $(DIR)/benchmark-cruntime.sh   vm        $cr_benchmark test 1
    $(DIR)/benchmark-graalvisor.sh svm       $gv_benchmark test 1
    $(DIR)/benchmark-graalvisor.sh container $gv_benchmark test 1
    $(DIR)/benchmark-graalvisor.sh vm        $gv_benchmark test 1
    export ITERATIONS=2 # Note: one iteration to dump, another to restore.
    context_snapshot
    process_snapshot
    vm_snapshot
    unset ITERATIONS
}

# Memory (fixed HW resources of 1 core and 2GB of memory, measure ops/s/mb)
function efficiency {

    # Graalvisor
    function efficiency_gv {
        function efficiency_gv_java {
            for benchmark in $JV_GV_BENCHMARKS;
            do
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                $(DIR)/benchmark-graalvisor.sh container $benchmark benchmark ${concurrency_table["$benchmark"]}
                unset WMULTIPLIER
            done
        }

        function efficiency_gv_javascript {
            for benchmark in $JS_GV_BENCHMARKS;
            do
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                if [ "$SANDBOX" = "context-snapshot" ]; then
                    export WARMUP=${concurrency_table["$benchmark"]}
                    rm -f $ADIR/*.memsnap  $ADIR/*.metasnap
                    $(DIR)/benchmark-graalvisor.sh container $benchmark test ${concurrency_table["$benchmark"]}
                fi
                $(DIR)/benchmark-graalvisor.sh container $benchmark benchmark ${concurrency_table["$benchmark"]}
                unset WARMUP
                unset WMULTIPLIER
            done
        }

        function efficiency_gv_python {
            for benchmark in $PY_GV_BENCHMARKS;
            do
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                if [ "$SANDBOX" = "context-snapshot" ]; then
                    export WARMUP=${concurrency_table["$benchmark"]}
                    rm -f $ADIR/*.memsnap $ADIR/*.metasnap
                    $(DIR)/benchmark-graalvisor.sh container $benchmark test ${concurrency_table["$benchmark"]}
                fi
                $(DIR)/benchmark-graalvisor.sh container $benchmark benchmark ${concurrency_table["$benchmark"]}
                unset WARMUP
                unset WMULTIPLIER
            done
        }

        export SANDBOX=isolate; efficiency_gv_java
        export SANDBOX=process; efficiency_gv_java
        export SANDBOX=context-snapshot; efficiency_gv_javascript
        export SANDBOX=context-snapshot; efficiency_gv_python
        export SANDBOX=process; efficiency_gv_javascript
        export SANDBOX=process; efficiency_gv_python
        unset WARMUP
        unset SANDBOX
    }

    # Graalvisor with a single invocation at a time.
    function efficiency_gv_single {
        function efficiency_gv_java_single {
            for benchmark in $JV_GV_BENCHMARKS;
            do
                export VM_MEM=${mem_table["$benchmark"]}
                export CGROUP_CPU_QUOTA=${cpu_table["$benchmark"]}
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                $(DIR)/benchmark-graalvisor.sh container $benchmark benchmark 1
                unset WMULTIPLIER
                unset CGROUP_CPU_QUOTA
                unset VM_MEM
            done
        }

        function efficiency_gv_javascript_single {
            for benchmark in $JS_GV_BENCHMARKS;
            do
                export VM_MEM=${mem_table["$benchmark"]}
                export CGROUP_CPU_QUOTA=${cpu_table["$benchmark"]}
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                $(DIR)/benchmark-graalvisor.sh container $benchmark benchmark 1
                unset CGROUP_CPU_QUOTA
                unset VM_MEM
            done
        }

        function efficiency_gv_python_single {
            for benchmark in $PY_GV_BENCHMARKS;
            do
                export VM_MEM=${mem_table["$benchmark"]}
                export CGROUP_CPU_QUOTA=${cpu_table["$benchmark"]}
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                $(DIR)/benchmark-graalvisor.sh container $benchmark benchmark 1
                unset WMULTIPLIER
                unset CGROUP_CPU_QUOTA
                unset VM_MEM
            done
        }

        export SANDBOX=isolate; efficiency_gv_java_single
        export SANDBOX=context; efficiency_gv_javascript_single
        export SANDBOX=context; efficiency_gv_python_single
        unset WARMUP
        unset SANDBOX
    }

    # Graalvisor with vm snapshotting
    function efficiency_gv_snapshot {
        snapshots=$HOME/tmp/snapshots
        mkdir -p $snapshots

        function efficiency_gv_java {
            for benchmark in $JV_GV_BENCHMARKS;
            do
                export VM_MEM=${mem_table["$benchmark"]}
                export CGROUP_CPU_QUOTA=${cpu_table["$benchmark"]}
                export SNAPSHOT=$snapshots/$benchmark
                if [ $benchmark = "gv_java_classify" ];
                then
                    # Tensorflow cannot be loaded two! We use test 0 because of that.
                    bash -c "export ITERATIONS=1; $(DIR)/benchmark-graalvisor.sh vm $benchmark test 0"
                else
                    bash -c "export ITERATIONS=1; $(DIR)/benchmark-graalvisor.sh vm $benchmark test 1"
                fi
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                $(DIR)/benchmark-graalvisor.sh vm $benchmark benchmark 1
                rm $SNAPSHOT.{disk,mem,snap}  &> /dev/null
                unset WMULTIPLIER
                unset SNAPSHOT
                unset CGROUP_CPU_QUOTA
                unset VM_MEM
            done
        }

        function efficiency_gv_javascript {
            for benchmark in $JS_GV_BENCHMARKS;
            do
                export VM_MEM=${mem_table["$benchmark"]}
                export CGROUP_CPU_QUOTA=${cpu_table["$benchmark"]}
                export SNAPSHOT=$snapshots/$benchmark
                bash -c "export ITERATIONS=1; $(DIR)/benchmark-graalvisor.sh vm $benchmark test 100"
                $(DIR)/benchmark-graalvisor.sh vm $benchmark benchmark 1
                rm $SNAPSHOT.{disk,mem,snap} &> /dev/null
                unset SNAPSHOT
                unset CGROUP_CPU_QUOTA
                unset VM_MEM
            done
        }

        function efficiency_gv_python {
            for benchmark in $PY_GV_BENCHMARKS;
            do
                export VM_MEM=${mem_table["$benchmark"]}
                export CGROUP_CPU_QUOTA=${cpu_table["$benchmark"]}
                export SNAPSHOT=$snapshots/$benchmark
                bash -c "export ITERATIONS=1; $(DIR)/benchmark-graalvisor.sh vm $benchmark test 100"
                export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
                $(DIR)/benchmark-graalvisor.sh vm $benchmark benchmark 1
                rm $SNAPSHOT.{disk,mem,snap} &> /dev/null
                unset WMULTIPLIER
                unset SNAPSHOT
                unset CGROUP_CPU_QUOTA
                unset VM_MEM
            done
        }

        export SANDBOX="isolate"; efficiency_gv_java; unset SANDBOX
        export SANDBOX="context"; efficiency_gv_javascript; unset SANDBOX
        export SANDBOX="context"; efficiency_gv_python; unset SANDBOX
    }

    # Openwhisk runtimes
    function efficiency_cr {
        for benchmark in $CR_BENCHMARKS;
        do
            export VM_MEM=${mem_table["$benchmark"]}
            export CGROUP_CPU_QUOTA=${cpu_table["$benchmark"]}
            export WMULTIPLIER=${wmultiplier_table["$benchmark"]}
            $(DIR)/benchmark-cruntime.sh container $benchmark benchmark 1
            unset WMULTIPLIER
            unset CGROUP_CPU_QUOTA
            unset VM_MEM
        done
    }

    export ITERATIONS=1 # Note: by default this should be 5.
    export CGROUP="experiments"
    export PIN_CORE="true"
    # Disabling turbo will make some benchmarks more stable. However, it will make everything much slower.
    export DISABLE_TURBO="false"
    export EXPERIMENT="asplos25-spring"
    unset WARMUP
    unset SNAPSHOT

    efficiency_gv
    efficiency_gv_single
    #efficiency_gv_snapshot
    efficiency_cr

    # Clear variables.
    unset ITERATIONS
    unset CGROUP
    unset PIN_CORE
    unset DISABLE_TURBO
    unset EXPERIMENT
}

read -p "Run efficiency experiment (y or Y, everything else as no)? " -n 1 -r
echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    efficiency
    exit 0
fi

read -p "Run basic graalvisor tests (y or Y, everything else as no)? " -n 1 -r
echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    test_gv_benchmarks
    exit 0
fi

read -p "Run basic openwhisk tests (y or Y, everything else as no)? " -n 1 -r
echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    test_ow_benchmarks
    exit 0
fi

read -p "Run benchmark resources experiment (y or Y, everything else as no)? " -n 1 -r
echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    measure_benchmark_resources
    exit 0
fi

read -p "Run cold start latency experiment (y or Y, everything else as no)? " -n 1 -r
echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    cold_start_latency
    exit 0
fi
