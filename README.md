# OpenDiscovery

A Flask server that allows people to publish and discover OpenAgents networks.

## Features

- Publish OpenAgents networks
- Unpublish networks
- Send heartbeats to keep networks active
- List available networks
- Homepage showing currently active networks

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp app/.env.example .env
   ```
   Then edit the `.env` file with your configuration.

4. Run the server:
   ```
   python run.py
   ```

## Pages

- `/` - Homepage showing currently active networks (sent heartbeat in last 15 minutes)

## API Endpoints

All endpoints are available under `/apis/`:

- `POST /apis/publish` - Publish a network
  - Accepts a JSON with the network profile
  - Checks for duplicate network_id (returns 409 Conflict if found)
  - Optional field `management_code` can be provided to re-publish a network with the same ID
    - If the management code matches the stored management token, the network will be updated
    - This allows recovery from errors or re-publishing after a crash
  - Required fields in the network profile:
    - `network_id`: Unique identifier for the network
    - `name`: Network name
    - `description`: Description of the network
    - `country`: Country where the network is hosted
    - `required_openagents_version`: Minimum version of OpenAgents required
    - `host`: Host address of the network
    - `port`: Port number of the network
    - `authentication`: Authentication configuration
    - `installed_protocols`: List of protocol names installed on the network
    - `required_adapters`: List of adapter names required by the network
  - Returns:
    - `success`: Boolean indicating success
    - `network_id`: The network ID
    - `management_token`: A token required for heartbeat and unpublish operations
    - `message`: Success message
  - Example:
    ```json
    {
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
    }
    ```

- `POST /apis/unpublish` - Unpublish a network
  - Request body: `{"network_id": "network-12345678", "management_token": "token_received_during_publish"}`
  - Requires the management token received during publish

- `POST /apis/heartbeat` - Send a heartbeat for a network
  - Request body: `{"network_id": "network-12345678", "num_agents": 5, "management_token": "token_received_during_publish"}`
  - Requires the management token received during publish

- `GET /apis/list_networks` - List all active networks
  - Returns networks that have sent a heartbeat in the last 15 minutes
  - Includes the last heartbeat time and number of agents for each network

## Storage

The application stores network information locally in a JSON file. The path to this file can be configured in the `.env` file using the `DATA_FILE` variable. 