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
PUBLISH_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{
  "network_id": "network-12345678",
  "name": "ExampleNetwork",
  "description": "Example network for testing",
  "country": "Worldwide",
  "required_openagents_version": "0.3.0",
  "host": "127.0.0.1",
  "port": 8765,
  "authentication": {
    "type": "none"
  },
  "installed_protocols": [
    "openagents.protocols.communication.simple_messaging",
    "openagents.protocols.discovery.network_discovery"
  ],
  "required_adapters": [
    "openagents.protocols.communication.simple_messaging"
  ],
  "tags": ["example", "test"],
  "categories": ["example"],
  "discoverable": true
}' http://localhost:5000/apis/publish)

echo $PUBLISH_RESPONSE | python -m json.tool

# Extract the management token from the response
MANAGEMENT_TOKEN=$(echo $PUBLISH_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin).get('management_token', ''))")

# 3. List networks again (should have one network)
echo -e "\n3. Listing networks (should have one network)..."
curl -s http://localhost:5000/apis/list_networks | python -m json.tool

# 4. Send a heartbeat
echo -e "\n4. Sending a heartbeat..."
curl -s -X POST -H "Content-Type: application/json" -d "{
  \"network_id\": \"network-12345678\",
  \"num_agents\": 3,
  \"management_token\": \"$MANAGEMENT_TOKEN\"
}" http://localhost:5000/apis/heartbeat | python -m json.tool

# 5. List networks again
echo -e "\n5. Listing networks again..."
curl -s http://localhost:5000/apis/list_networks | python -m json.tool

# 6. Unpublish the network
echo -e "\n6. Unpublishing the network..."
curl -s -X POST -H "Content-Type: application/json" -d "{
  \"network_id\": \"network-12345678\",
  \"management_token\": \"$MANAGEMENT_TOKEN\"
}" http://localhost:5000/apis/unpublish | python -m json.tool

# 7. List networks again (should be empty)
echo -e "\n7. Listing networks (should be empty again)..."
curl -s http://localhost:5000/apis/list_networks | python -m json.tool

# 8. Try to publish a network with the same ID (should fail)
echo -e "\n8. Trying to publish a network with the same ID (should fail)..."
curl -s -X POST -H "Content-Type: application/json" -d '{
  "network_id": "network-12345678",
  "name": "ExampleNetwork",
  "description": "Example network for testing",
  "country": "Worldwide",
  "required_openagents_version": "0.3.0",
  "host": "127.0.0.1",
  "port": 8765,
  "authentication": {
    "type": "none"
  },
  "installed_protocols": [
    "openagents.protocols.communication.simple_messaging",
    "openagents.protocols.discovery.network_discovery"
  ],
  "required_adapters": [
    "openagents.protocols.communication.simple_messaging"
  ],
  "tags": ["example", "test"],
  "categories": ["example"],
  "discoverable": true
}' http://localhost:5000/apis/publish | python -m json.tool

# Kill the server
echo -e "\nStopping the server..."
kill $SERVER_PID

echo -e "\nTest completed!" 