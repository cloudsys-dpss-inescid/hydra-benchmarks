
 #!/bin/bash




export SERVER_IP=10.15.0.24 #vitamina04 10.15.0.24
export GRAALVISOR_PORT=8081
export LOCAL_THREADS=1
export WMULTIPLIER=16
export WMULTIPLIER=206



rm results/remote_client.log 
touch results/remote_client.log 



./http_post $SERVER_IP $GRAALVISOR_PORT payload.post $LOCAL_THREADS $WMULTIPLIER results/  >> results/remote_client.log  2>&1