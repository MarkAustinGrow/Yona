# Yona MCP Implementation

This directory contains the implementation of the Model Context Protocol (MCP) for the Yona agent. The MCP framework enables secure, decentralized communication between agents.

## Overview

The implementation follows the three-layer architecture described in the MCP white paper:

1. **Identity and Encrypted Communication Layer**: Implemented in `src/identity/`
2. **Meta-Protocol Layer**: Implemented in `src/protocol/`
3. **Application Protocol Layer**: Implemented in `src/api/`

## Features

- **Decentralized Identity (DID)**: Generate and manage DIDs for the Yona agent
- **Capability Document**: Describe Yona's services and protocols
- **API Endpoints**: Serve the capability document and DID document

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Testing

You can test the MCP implementation using the provided test script:

```bash
python test_mcp.py
```

This will test the DID manager and capability document generation without needing to run the full API server.

If you don't have the `cryptography` package installed, the test will run in simulation mode, which uses mock keys instead of real cryptographic operations.

## Running the API Server

To run the API server, which serves the capability document and DID document:

```bash
python run_api_server.py
```

This will start a Flask server on `http://127.0.0.1:5000` with the following endpoints:

- **Capability Document**: `http://127.0.0.1:5000/capabilities`
- **DID Document**: `http://127.0.0.1:5000/.well-known/did.json`
- **Health Check**: `http://127.0.0.1:5000/health`

## Implementation Details

### Identity Layer (`src/identity/`)

The identity layer provides functionality for generating and managing DIDs, creating DID documents, and signing requests.

- **DIDManager**: Manages DIDs, creates DID documents, and signs requests

### Protocol Layer (`src/protocol/`)

The protocol layer provides functionality for generating capability documents and handling protocol negotiation.

- **CapabilityDocument**: Generates capability documents that describe Yona's services

### API Layer (`src/api/`)

The API layer provides endpoints for serving the capability document and DID document.

- **YonaAPI**: Provides API endpoints for the Yona agent

## Next Steps

The current implementation includes Phase 1 of the MCP implementation plan:

- [x] Create basic DID infrastructure
- [x] Create capability document
- [x] Set up a simple API endpoint

Future phases will include:

- [ ] Implement basic protocol handling
- [ ] Add authentication to API requests
- [ ] Implement protocol negotiation
- [ ] Add protocol code generation
- [ ] Implement end-to-end encryption
- [ ] Integrate with existing scripts
- [ ] Create test agents
- [ ] Optimize and refine

## Usage with Existing Yona Functionality

The MCP implementation is designed to work alongside the existing Yona functionality. The API server can be run separately from the main Yona agent, allowing for gradual integration.

In future phases, the MCP components will be integrated with the existing Yona agent to enable secure, decentralized communication with other agents.
