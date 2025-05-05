# Coral Server JSON-RPC Format Guide

This document provides detailed information about the JSON-RPC format requirement for communicating with the Coral server.

## Overview

The Coral server expects all messages to follow the JSON-RPC format, which requires a unique "id" field for each request. Failing to include this field will result in 400 Bad Request errors.

## JSON-RPC Format Requirements

1. **Unique ID Field**: Each message must include a unique "id" field
2. **Action Field**: Specifies the operation to perform
3. **Payload Field**: Contains the data for the operation

## Example Messages

### Agent Registration

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "register_agent",
  "payload": {
    "agent_id": "your_agent_id",
    "name": "Your Agent Name",
    "description": "Your agent description",
    "capabilities": ["capability1", "capability2"]
  }
}
```

### Thread Creation

```json
{
  "id": "663f8500-f39c-52e5-b827-557766551111",
  "action": "create_thread",
  "payload": {
    "participants": ["agent_id_1", "agent_id_2"],
    "metadata": {}
  }
}
```

### Message Sending

```json
{
  "id": "774f9600-g49d-63f6-c938-668877662222",
  "action": "send_message",
  "payload": {
    "thread_id": "thread_123456",
    "sender_id": "your_agent_id",
    "content": "Hello, this is a test message.",
    "mentions": ["agent_id_to_mention"]
  }
}
```

## Generating Unique IDs

In Python, you can generate a unique ID using the `uuid` module:

```python
import uuid

message_id = str(uuid.uuid4())
```

## Common Errors

### 400 Bad Request

If you receive a 400 Bad Request error from the Coral server, check that:

1. Your message includes the "id" field
2. The "id" field is unique for each request
3. The message structure follows the JSON-RPC format

### Other Errors

- **401 Unauthorized**: Check your session ID
- **404 Not Found**: Verify the endpoint URL
- **500 Internal Server Error**: Server-side issue, try again later

## Best Practices

1. **Generate New UUIDs**: Always generate a new UUID for each request
2. **Log Request IDs**: Store the request IDs for debugging purposes
3. **Handle Responses**: Check response status codes and handle errors appropriately
4. **Validate Messages**: Validate your message format before sending

## Implementation in SimpleCoralAgent

The `SimpleCoralAgent` class automatically adds the required "id" field to all messages:

```python
payload = {
    "id": str(uuid.uuid4()),  # Required for JSON-RPC format
    "action": "register_agent",
    "payload": {
        "agent_id": self.agent_id,
        "name": name,
        "description": description,
        "capabilities": []
    }
}
```

## Conclusion

Understanding and implementing the JSON-RPC format is crucial for successful communication with the Coral server. By following the guidelines in this document, you can ensure that your messages are properly formatted and avoid common errors.
