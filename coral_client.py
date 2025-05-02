# coral_client.py
import json
import uuid
import asyncio
import httpx
import sseclient

class CoralClient:
    def __init__(self, server_url, agent_id, session_id="session1"):
        self.server_url = server_url
        self.agent_id = agent_id
        self.session_id = session_id
        self.sse_url = f"{server_url}/devmode/exampleApplication/privkey/{session_id}/sse?agentId={self.agent_id}"
        self.client = httpx.AsyncClient()
        self.message_handlers = []

    async def connect(self):
        response = self.client.stream('GET', self.sse_url)
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.event == 'message':
                data = json.loads(event.data)
                await self._handle_message(data)

    async def _handle_message(self, message):
        for handler in self.message_handlers:
            await handler(message)

    def add_message_handler(self, handler):
        self.message_handlers.append(handler)

    async def register_agent(self, name, description, capabilities=[]):
        response = await self.client.post(
            f"{self.server_url}/tools/register_agent",
            json={
                "agent_id": self.agent_id,
                "name": name,
                "description": description,
                "capabilities": capabilities
            }
        )
        return response.status_code == 200

    async def create_thread(self, participants, metadata={}):
        response = await self.client.post(
            f"{self.server_url}/tools/create_thread",
            json={"participants": participants, "metadata": metadata}
        )
        return response.json().get("thread_id")

    async def send_message(self, thread_id, content, mentions=[], signature_info=None):
        # Prepare the message payload
        message_payload = {
            "thread_id": thread_id,
            "sender_id": self.agent_id,
            "content": content,
            "mentions": mentions
        }
        
        # Add signature information if provided
        if signature_info:
            message_payload["signature"] = signature_info.get("signature")
            message_payload["original_message"] = signature_info.get("message")
        
        # Send the message
        response = await self.client.post(
            f"{self.server_url}/tools/send_message",
            json=message_payload
        )
        return response.json()
