# OpenDiscovery

A Flask server that allows people to publish and discover OpenAgents networks.

## Features

- Publish OpenAgents networks
- Unpublish networks
- Send heartbeats to keep networks active
- List available networks

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

## API Endpoints

All endpoints are available under `/apis/`:

- `POST /apis/publish` - Publish a network
  - Accepts JSON or YAML configuration in request body or as a file upload with name 'config'
  - Network configuration must include a 'network_profile' section with a 'name' field

- `POST /apis/unpublish` - Unpublish a network
  - Request body: `{"network_id": "network_name"}`

- `POST /apis/heartbeat` - Send a heartbeat for a network
  - Request body: `{"network_id": "network_name"}`

- `GET /apis/list_networks` - List all available networks
  - Optional query parameter: `filter` (JSON string with filter criteria)
  - Example: `/apis/list_networks?filter={"tags":["example","test"]}`

## Storage

The application stores network information locally in a JSON file. The path to this file can be configured in the `.env` file using the `DATA_FILE` variable. 