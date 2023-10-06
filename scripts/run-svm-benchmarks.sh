#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

dbread_cache="$ARGO_HOME/../benchmarks/src/java/gv-database-read/build/libdbread.so"
dbread_nocache="$ARGO_HOME/../benchmarks/src/java/gv-database-read-no-cache/build/libdbread.so"
tmp_dir="/tmp/test-proxy-logs"
sudo rm -r $tmp_dir &> /dev/null
mkdir $tmp_dir &> /dev/null

# no isolate caching, no persistent resources
GV_PORT=8082 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=false FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_25perc.csv &> $tmp_dir/exec_no_cache_no_pers_25perc.log &
GV_PORT=8083 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=false FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_50perc.csv &> $tmp_dir/exec_no_cache_no_pers_50perc.log &
GV_PORT=8084 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=false FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_75perc.csv &> $tmp_dir/exec_no_cache_no_pers_75perc.log &
GV_PORT=8085 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=false FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_90perc.csv &> $tmp_dir/exec_no_cache_no_pers_90perc.log &

# with isolate caching, no persistent resources
GV_PORT=8086 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_25perc.csv &> $tmp_dir/exec_cache_no_pers_25perc.log &
GV_PORT=8087 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_50perc.csv &> $tmp_dir/exec_cache_no_pers_50perc.log &
GV_PORT=8088 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_75perc.csv &> $tmp_dir/exec_cache_no_pers_75perc.log &
GV_PORT=8089 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_nocache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_90perc.csv &> $tmp_dir/exec_cache_no_pers_90perc.log &

# with isolate caching, with persistent resources
GV_PORT=8090 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_cache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_25perc.csv &> $tmp_dir/exec_cache_pers_25perc.log &
GV_PORT=8091 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_cache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_50perc.csv &> $tmp_dir/exec_cache_pers_50perc.log &
GV_PORT=8092 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_cache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_75perc.csv &> $tmp_dir/exec_cache_pers_75perc.log &
GV_PORT=8093 app_dir="/tmp/apps$GV_PORT/" ISOLATE_CACHING=true FUNCTION_CODE="$dbread_cache" bash $(DIR)/benchmark-svm-load.sh /home/sergiyivan/lse/argo/benchmarks/azure-dataset/output/d02_1f_721_780_90perc.csv &> $tmp_dir/exec_cache_pers_90perc.log &
