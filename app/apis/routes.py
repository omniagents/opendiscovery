from flask import Blueprint, request, jsonify
import yaml
import json
from app.utils.storage import (
    get_networks,
    get_network,
    add_network,
    update_heartbeat,
    remove_network
)

api_bp = Blueprint('api', __name__)

@api_bp.route('/publish', methods=['POST'])
def publish():
    """
    Publish a network to the discovery service.
    
    Expected payload:
    - YAML or JSON configuration of the network
    """
    try:
        # Check if the request has the file part
        if 'config' in request.files:
            file = request.files['config']
            content = file.read().decode('utf-8')
            
            # Parse YAML or JSON
            try:
                network_data = yaml.safe_load(content)
            except yaml.YAMLError:
                try:
                    network_data = json.loads(content)
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid file format. Must be YAML or JSON.'
                    }), 400
        else:
            # Try to parse JSON from request body
            network_data = request.json
            if not network_data:
                return jsonify({
                    'success': False,
                    'error': 'No network configuration provided.'
                }), 400
        
        # Validate network data
        if not network_data.get('network_profile'):
            return jsonify({
                'success': False,
                'error': 'Network configuration must include a network_profile.'
            }), 400
        
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
        
        # Update heartbeat
        success = update_heartbeat(network_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Heartbeat received for network {network_id}.'
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
    
    Query parameters:
    - filter: Optional JSON string with filter criteria
    """
    try:
        # Get all networks
        networks = get_networks()
        
        # Apply filters if provided
        filter_str = request.args.get('filter')
        if filter_str:
            try:
                filters = json.loads(filter_str)
                
                # Filter networks based on criteria
                filtered_networks = {}
                for network_id, network_data in networks.items():
                    match = True
                    
                    # Check network profile fields
                    profile = network_data.get('network_profile', {})
                    for key, value in filters.items():
                        if key == 'tags' and 'tags' in profile:
                            # Special handling for tags (check if any tag matches)
                            if not any(tag in profile['tags'] for tag in value):
                                match = False
                                break
                        elif key == 'categories' and 'categories' in profile:
                            # Special handling for categories
                            if not any(cat in profile['categories'] for cat in value):
                                match = False
                                break
                        elif key in profile and profile[key] != value:
                            match = False
                            break
                    
                    if match:
                        filtered_networks[network_id] = network_data
                
                networks = filtered_networks
            
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid filter format. Must be valid JSON.'
                }), 400
        
        # Format response
        result = []
        for network_id, network_data in networks.items():
            # Remove internal fields
            network_copy = network_data.copy()
            if 'last_heartbeat' in network_copy:
                del network_copy['last_heartbeat']
            
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