#!/bin/bash

# Make the script executable
chmod +x test_server.sh

# Start the server in the background
echo "Starting the server..."
python run.py &
SERVER_PID=$!

# Wait for the server to start
echo "Waiting for the server to start..."
sleep 3

# Test the API endpoints
echo "Testing API endpoints..."

# 1. List networks (should be empty)
echo -e "\n1. Listing networks (should be empty)..."
curl -s http://localhost:5000/apis/list_networks | python -m json.tool

# 2. Publish a network
echo -e "\n2. Publishing a network..."
curl -s -X POST -H "Content-Type: application/json" -d @examples/network_config.yaml http://localhost:5000/apis/publish | python -m json.tool

# 3. List networks again (should have one network)
echo -e "\n3. Listing networks (should have one network)..."
curl -s http://localhost:5000/apis/list_networks | python -m json.tool

# 4. Send a heartbeat
echo -e "\n4. Sending a heartbeat..."
curl -s -X POST -H "Content-Type: application/json" -d '{"network_id": "ExampleNetwork"}' http://localhost:5000/apis/heartbeat | python -m json.tool

# 5. List networks with filter
echo -e "\n5. Listing networks with filter..."
curl -s "http://localhost:5000/apis/list_networks?filter=%7B%22tags%22%3A%5B%22example%22%5D%7D" | python -m json.tool

# 6. Unpublish the network
echo -e "\n6. Unpublishing the network..."
curl -s -X POST -H "Content-Type: application/json" -d '{"network_id": "ExampleNetwork"}' http://localhost:5000/apis/unpublish | python -m json.tool

# 7. List networks again (should be empty)
echo -e "\n7. Listing networks (should be empty again)..."
curl -s http://localhost:5000/apis/list_networks | python -m json.tool

# Kill the server
echo -e "\nStopping the server..."
kill $SERVER_PID

echo -e "\nTest completed!" 