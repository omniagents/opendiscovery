import os
import json
import time
from datetime import datetime, timedelta
import threading

# File lock to prevent race conditions
file_lock = threading.Lock()

# Path to the data file
DATA_FILE = os.getenv('DATA_FILE', 'networks.json')
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), DATA_FILE)

# In-memory cache of networks
_networks = {}

def _load_networks():
    """Load networks from the data file."""
    global _networks
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r') as f:
                _networks = json.load(f)
        else:
            _networks = {}
    except Exception as e:
        print(f"Error loading networks: {e}")
        _networks = {}

def _save_networks():
    """Save networks to the data file."""
    try:
        with open(DATA_PATH, 'w') as f:
            json.dump(_networks, f, indent=2)
    except Exception as e:
        print(f"Error saving networks: {e}")

# Load networks on module import
_load_networks()

def get_networks():
    """Get all networks."""
    with file_lock:
        return _networks.copy()

def get_network(network_id):
    """Get a specific network by ID."""
    with file_lock:
        return _networks.get(network_id)

def add_network(network_data):
    """Add or update a network."""
    network_id = network_data.get('network_profile', {}).get('name')
    if not network_id:
        raise ValueError("Network must have a name in network_profile")
    
    with file_lock:
        # Add timestamp for heartbeat tracking
        network_data['last_heartbeat'] = time.time()
        _networks[network_id] = network_data
        _save_networks()
    
    return network_id

def update_heartbeat(network_id):
    """Update the heartbeat timestamp for a network."""
    with file_lock:
        if network_id in _networks:
            _networks[network_id]['last_heartbeat'] = time.time()
            _save_networks()
            return True
        return False

def remove_network(network_id):
    """Remove a network by ID."""
    with file_lock:
        if network_id in _networks:
            del _networks[network_id]
            _save_networks()
            return True
        return False

def cleanup_inactive_networks(timeout_minutes):
    """Remove networks that haven't sent a heartbeat in the specified time."""
    current_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    with file_lock:
        networks_to_remove = []
        
        for network_id, network_data in _networks.items():
            last_heartbeat = network_data.get('last_heartbeat', 0)
            if current_time - last_heartbeat > timeout_seconds:
                networks_to_remove.append(network_id)
        
        for network_id in networks_to_remove:
            del _networks[network_id]
        
        if networks_to_remove:
            _save_networks()
            print(f"Removed {len(networks_to_remove)} inactive networks") 