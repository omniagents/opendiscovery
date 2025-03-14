from flask import Blueprint, request, jsonify, render_template
import yaml
import json
from app.utils.storage import (
    get_networks,
    get_network,
    add_network,
    update_heartbeat,
    remove_network
)
import time
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def homepage():
    """
    Render the homepage with a list of active networks.
    """
    try:
        # Get all networks
        networks = get_networks()
        
        # Filter to only include active networks (heartbeat in last 15 minutes)
        current_time = time.time()
        active_networks = {}
        for network_id, network_data in networks.items():
            last_heartbeat = network_data.get('last_heartbeat', 0)
            # Check if heartbeat was within the last 15 minutes (900 seconds)
            if current_time - last_heartbeat <= 900:
                active_networks[network_id] = network_data
        
        # Format networks for the template
        formatted_networks = []
        for network_id, network_data in active_networks.items():
            profile = network_data.get('network_profile', {})
            
            # Convert timestamp to human-readable format
            last_heartbeat = network_data.get('last_heartbeat', 0)
            last_heartbeat_time = datetime.fromtimestamp(last_heartbeat).strftime('%Y-%m-%d %H:%M:%S')
            
            formatted_networks.append({
                'network_id': network_id,
                'name': profile.get('name', 'Unnamed Network'),
                'description': profile.get('description', 'No description'),
                'country': profile.get('country', 'Unknown'),
                'host': profile.get('host', 'Unknown'),
                'port': profile.get('port', 'Unknown'),
                'num_agents': network_data.get('num_agents', 0),
                'last_heartbeat': last_heartbeat_time,
                'tags': profile.get('tags', []),
                'installed_protocols': profile.get('installed_protocols', []),
                'required_adapters': profile.get('required_adapters', [])
            })
        
        return render_template('homepage.html', networks=formatted_networks)
    
    except Exception as e:
        return f"Error loading networks: {str(e)}", 500

@api_bp.route('/publish', methods=['POST'])
def publish():
    """
    Publish a network to the discovery service.
    
    Expected payload:
    - JSON with the network profile
    
    Required network profile fields:
    - name: Network name
    - network_id: Unique identifier for the network
    - description: Description of the network
    - country: Country where the network is hosted
    - required_openagents_version: Minimum version of OpenAgents required
    - host: Host address of the network
    - port: Port number of the network
    - authentication: Authentication configuration
    - installed_protocols: List of protocol names installed on the network
    - required_adapters: List of adapter names required by the network
    """
    try:
        # Try to parse JSON from request body
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided.'
            }), 400
        
        # Get the network profile directly from the request
        network_profile = data
        
        # Validate network profile
        if not network_profile:
            return jsonify({
                'success': False,
                'error': 'Network profile is required.'
            }), 400
        
        # Validate required fields in network_profile
        required_fields = [
            'name', 
            'network_id', 
            'description', 
            'country', 
            'required_openagents_version', 
            'host', 
            'port', 
            'authentication',
            'installed_protocols',
            'required_adapters'
        ]
        
        missing_fields = [field for field in required_fields if field not in network_profile]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields in network profile: {", ".join(missing_fields)}'
            }), 400
        
        # Validate that installed_protocols and required_adapters are lists
        if not isinstance(network_profile.get('installed_protocols'), list):
            return jsonify({
                'success': False,
                'error': 'installed_protocols must be a list of protocol names'
            }), 400
            
        if not isinstance(network_profile.get('required_adapters'), list):
            return jsonify({
                'success': False,
                'error': 'required_adapters must be a list of adapter names'
            }), 400
        
        # Create a network data structure with just the profile
        network_data = {'network_profile': network_profile}
        
        # Add network to storage
        network_id = add_network(network_data)
        
        return jsonify({
            'success': True,
            'network_id': network_id,
            'message': f'Network {network_id} published successfully.'
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to publish network: {str(e)}'
        }), 500

@api_bp.route('/unpublish', methods=['POST'])
def unpublish():
    """
    Unpublish a network from the discovery service.
    
    Expected payload:
    {
        "network_id": "network_name"
    }
    """
    try:
        data = request.json
        if not data or 'network_id' not in data:
            return jsonify({
                'success': False,
                'error': 'network_id is required.'
            }), 400
        
        network_id = data['network_id']
        
        # Check if network exists
        if not get_network(network_id):
            return jsonify({
                'success': False,
                'error': f'Network {network_id} not found.'
            }), 404
        
        # Remove network from storage
        success = remove_network(network_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Network {network_id} unpublished successfully.'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to unpublish network {network_id}.'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to unpublish network: {str(e)}'
        }), 500

@api_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Send a heartbeat for a network to keep it active.
    
    Expected payload:
    {
        "network_id": "network_name",
        "num_agents": 5
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided.'
            }), 400
            
        if 'network_id' not in data:
            return jsonify({
                'success': False,
                'error': 'network_id is required.'
            }), 400
            
        if 'num_agents' not in data:
            return jsonify({
                'success': False,
                'error': 'num_agents is required.'
            }), 400
            
        network_id = data['network_id']
        num_agents = data['num_agents']
        
        # Validate num_agents is a positive integer
        try:
            num_agents = int(num_agents)
            if num_agents < 0:
                return jsonify({
                    'success': False,
                    'error': 'num_agents must be a positive integer.'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'num_agents must be a valid integer.'
            }), 400
        
        # Update heartbeat
        success = update_heartbeat(network_id, num_agents)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Heartbeat received for network {network_id} with {num_agents} agents.'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Network {network_id} not found.'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to process heartbeat: {str(e)}'
        }), 500

@api_bp.route('/list_networks', methods=['GET'])
def list_networks():
    """
    List all active networks.
    
    A network is considered active if it sent a heartbeat in the last 15 minutes.
    """
    try:
        # Get all networks
        networks = get_networks()
        
        # Filter to only include active networks (heartbeat in last 15 minutes)
        current_time = time.time()
        active_networks = {}
        for network_id, network_data in networks.items():
            last_heartbeat = network_data.get('last_heartbeat', 0)
            # Check if heartbeat was within the last 15 minutes (900 seconds)
            if current_time - last_heartbeat <= 900:
                active_networks[network_id] = network_data
        
        # Format response
        result = []
        for network_id, network_data in active_networks.items():
            # Create a copy of the network data
            network_copy = network_data.copy()
            
            # Convert timestamp to human-readable format
            last_heartbeat = network_copy.get('last_heartbeat', 0)
            last_heartbeat_time = datetime.fromtimestamp(last_heartbeat).strftime('%Y-%m-%d %H:%M:%S')
            network_copy['last_heartbeat_time'] = last_heartbeat_time
            
            result.append(network_copy)
        
        return jsonify({
            'success': True,
            'networks': result,
            'count': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to list networks: {str(e)}'
        }), 500 