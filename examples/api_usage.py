#!/usr/bin/env python3
"""
Example script demonstrating how to use the OpenDiscovery API.
"""

import requests
import json
import time
import yaml
import os

# API base URL
BASE_URL = "http://localhost:5000/apis"

def publish_network(config_file):
    """Publish a network using a configuration file."""
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    
    response = requests.post(f"{BASE_URL}/publish", json=config_data)
    return response.json()

def publish_network_with_file(config_file):
    """Publish a network by uploading a configuration file."""
    with open(config_file, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/publish",
            files={'config': f}
        )
    return response.json()

def unpublish_network(network_id):
    """Unpublish a network."""
    response = requests.post(
        f"{BASE_URL}/unpublish",
        json={"network_id": network_id}
    )
    return response.json()

def send_heartbeat(network_id):
    """Send a heartbeat for a network."""
    response = requests.post(
        f"{BASE_URL}/heartbeat",
        json={"network_id": network_id}
    )
    return response.json()

def list_networks(filter_criteria=None):
    """List all networks, optionally filtered."""
    url = f"{BASE_URL}/list_networks"
    if filter_criteria:
        url += f"?filter={json.dumps(filter_criteria)}"
    
    response = requests.get(url)
    return response.json()

def main():
    # Example usage
    print("1. Publishing a network...")
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "examples/network_config.yaml")
    
    # Check if the example config exists
    if not os.path.exists(config_file):
        # Create an example config
        example_config = {
            "network": {
                "name": "ExampleNetwork",
                "protocols": [
                    {
                        "name": "openagents.protocols.communication.simple_messaging",
                        "enabled": True,
                        "config": {}
                    }
                ]
            },
            "service_agents": [
                {
                    "name": "Agent1",
                    "adapters": [
                        {
                            "name": "openagents.protocols.communication.simple_messaging",
                            "enabled": True,
                            "config": {}
                        }
                    ],
                    "services": [
                        {
                            "name": "echo",
                            "description": "Echo service that returns the input"
                        }
                    ],
                    "subscriptions": ["general"]
                }
            ],
            "network_profile": {
                "discoverable": True,
                "name": "ExampleNetwork",
                "description": "Example network for testing",
                "tags": ["example", "test"],
                "categories": ["example"],
                "country": "Worldwide"
            }
        }
        
        # Create the examples directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Save the example config
        with open(config_file, 'w') as f:
            yaml.dump(example_config, f)
    
    result = publish_network(config_file)
    print(json.dumps(result, indent=2))
    
    print("\n2. Listing all networks...")
    result = list_networks()
    print(json.dumps(result, indent=2))
    
    print("\n3. Sending a heartbeat...")
    result = send_heartbeat("ExampleNetwork")
    print(json.dumps(result, indent=2))
    
    print("\n4. Listing networks with filter...")
    result = list_networks({"tags": ["example"]})
    print(json.dumps(result, indent=2))
    
    print("\n5. Unpublishing the network...")
    result = unpublish_network("ExampleNetwork")
    print(json.dumps(result, indent=2))
    
    print("\n6. Listing all networks after unpublishing...")
    result = list_networks()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 