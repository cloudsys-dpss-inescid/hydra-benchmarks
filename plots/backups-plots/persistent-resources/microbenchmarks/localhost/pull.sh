#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

# Copy result files.
scp sergiyivan@angainor:/tmp/test-proxy-8081/result.json $(DIR)/result_pers.json
scp sergiyivan@angainor:/tmp/test-proxy-8082/result.json $(DIR)/result_no_pers.json
