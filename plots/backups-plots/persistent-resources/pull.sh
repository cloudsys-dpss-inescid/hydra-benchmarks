#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

MODE=$1

# Copy memory files.
scp sergiyivan@angainor:/tmp/test-proxy-8082/lambda.rss $(DIR)/"$MODE"/memory_no_cache_no_pers_25.rss
scp sergiyivan@angainor:/tmp/test-proxy-8083/lambda.rss $(DIR)/"$MODE"/memory_no_cache_no_pers_50.rss
scp sergiyivan@angainor:/tmp/test-proxy-8084/lambda.rss $(DIR)/"$MODE"/memory_no_cache_no_pers_75.rss
scp sergiyivan@angainor:/tmp/test-proxy-8085/lambda.rss $(DIR)/"$MODE"/memory_no_cache_no_pers_90.rss

scp sergiyivan@angainor:/tmp/test-proxy-8086/lambda.rss $(DIR)/"$MODE"/memory_cache_no_pers_25.rss
scp sergiyivan@angainor:/tmp/test-proxy-8087/lambda.rss $(DIR)/"$MODE"/memory_cache_no_pers_50.rss
scp sergiyivan@angainor:/tmp/test-proxy-8088/lambda.rss $(DIR)/"$MODE"/memory_cache_no_pers_75.rss
scp sergiyivan@angainor:/tmp/test-proxy-8089/lambda.rss $(DIR)/"$MODE"/memory_cache_no_pers_90.rss

scp sergiyivan@angainor:/tmp/test-proxy-8090/lambda.rss $(DIR)/"$MODE"/memory_cache_pers_25.rss
scp sergiyivan@angainor:/tmp/test-proxy-8091/lambda.rss $(DIR)/"$MODE"/memory_cache_pers_50.rss
scp sergiyivan@angainor:/tmp/test-proxy-8092/lambda.rss $(DIR)/"$MODE"/memory_cache_pers_75.rss
scp sergiyivan@angainor:/tmp/test-proxy-8093/lambda.rss $(DIR)/"$MODE"/memory_cache_pers_90.rss

# Copy logs.
scp -r sergiyivan@angainor:/tmp/test-proxy-logs $(DIR)/"$MODE"

# Copy latency files.
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8082.txt $(DIR)/"$MODE"/latency_no_cache_no_pers_25.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8083.txt $(DIR)/"$MODE"/latency_no_cache_no_pers_50.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8084.txt $(DIR)/"$MODE"/latency_no_cache_no_pers_75.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8085.txt $(DIR)/"$MODE"/latency_no_cache_no_pers_90.txt

scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8086.txt $(DIR)/"$MODE"/latency_cache_no_pers_25.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8087.txt $(DIR)/"$MODE"/latency_cache_no_pers_50.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8088.txt $(DIR)/"$MODE"/latency_cache_no_pers_75.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8089.txt $(DIR)/"$MODE"/latency_cache_no_pers_90.txt

scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8090.txt $(DIR)/"$MODE"/latency_cache_pers_25.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8091.txt $(DIR)/"$MODE"/latency_cache_pers_50.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8092.txt $(DIR)/"$MODE"/latency_cache_pers_75.txt
scp -r sergiyivan@angainor:/home/sergiyivan/lse/argo/benchmarks/scripts/latencies127_0_0_1:8093.txt $(DIR)/"$MODE"/latency_cache_pers_90.txt
