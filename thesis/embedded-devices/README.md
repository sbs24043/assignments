1. Start the server:
./server-run.sh

2. Start the clients:
./client-run.sh "node-1" 9094 0 2
./client-run.sh "node-2" 9095 1 2

3. Run
flwr run .

4. Clean up

sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q)