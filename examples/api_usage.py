#!/usr/bin/env python3
"""
Example script demonstrating how to use the OpenDiscovery API.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000/apis"

def publish_network(profile):
    """Publish a network using the network profile.
    
    Returns:
        dict: Response containing network_id and management_token if successful
    """
    response = requests.post(
        f"{BASE_URL}/publish", 
        json=profile
    )
    return response.json()

def unpublish_network(network_id, management_token):
    """Unpublish a network.
    
    Args:
        network_id: The ID of the network
        management_token: The token received during publish
    """
    response = requests.post(
        f"{BASE_URL}/unpublish",
        json={
            "network_id": network_id,
            "management_token": management_token
        }
    )
    return response.json()

def send_heartbeat(network_id, num_agents, management_token):
    """Send a heartbeat for a network.
    
    Args:
        network_id: The ID of the network
        num_agents: The current number of agents in the network
        management_token: The token received during publish
    """
    response = requests.post(
        f"{BASE_URL}/heartbeat",
        json={
            "network_id": network_id,
            "num_agents": num_agents,
            "management_token": management_token
        }
    )
    return response.json()

def list_networks():
    """List all active networks (sent heartbeat in last 15 minutes)."""
    response = requests.get(f"{BASE_URL}/list_networks")
    return response.json()

def main():
    # Example network profile
    example_profile = {
        "network_id": "network-12345678",
        "name": "ExampleNetwork",
        "description": "Example network for testing",
        "tags": ["example", "test"],
        "categories": ["example"],
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
        "discoverable": True,
        "icon": "https://example.com/icon.png",
        "website": "https://example.com"
    }
    
    # Example usage
    print("1. Publishing a network...")
    result = publish_network(example_profile)
    print(json.dumps(result, indent=2))
    
    if result.get("success"):
        network_id = result.get("network_id")
        management_token = result.get("management_token")
        
        print("\n2. Listing all networks...")
        result = list_networks()
        print(json.dumps(result, indent=2))
        
        print("\n3. Sending a heartbeat...")
        result = send_heartbeat(network_id, 3, management_token)
        print(json.dumps(result, indent=2))
        
        print("\n4. Listing networks again...")
        result = list_networks()
        print(json.dumps(result, indent=2))
        
        print("\n5. Unpublishing the network...")
        result = unpublish_network(network_id, management_token)
        print(json.dumps(result, indent=2))
        
        print("\n6. Listing all networks after unpublishing...")
        result = list_networks()
        print(json.dumps(result, indent=2))
        
        # Example of trying to publish a network with the same ID (should fail)
        print("\n7. Trying to publish a network with the same ID (should fail)...")
        result = publish_network(example_profile)
        print(json.dumps(result, indent=2))
    else:
        print("Failed to publish network")

if __name__ == "__main__":
    main() 