🚩 Step-by-Step Guide for Integrating YonaAgent with Coral Protocol
✅ Step 1: Prepare Your Environment
Ensure the Coral server is running and stable on your Linode server.

Confirm that you have reverted YonaAgent to its stable, pre-integration state.

✅ Step 2: Implement the CoralClient Class
Create a file named coral_client.py in your YonaAgent project directory:

python
Copy
Edit
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

    async def send_message(self, thread_id, content, mentions=[]):
        response = await self.client.post(
            f"{self.server_url}/tools/send_message",
            json={
                "thread_id": thread_id,
                "sender_id": self.agent_id,
                "content": content,
                "mentions": mentions
            }
        )
        return response.json()
✅ Step 3: Adapt YonaAgent to Use CoralClient
Modify your existing YonaAgent class (e.g., yona_agent.py) minimally:

python
Copy
Edit
# yona_agent.py
from coral_client import CoralClient

class YonaAgentWithCoral(YonaAgent):
    def __init__(self, coral_server_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        agent_id = self.did.id if hasattr(self, 'did') else f"yona_{uuid.uuid4().hex[:8]}"
        self.coral = CoralClient(coral_server_url, agent_id)
        self.coral.add_message_handler(self.handle_coral_message)

    async def initialize_coral(self):
        capabilities = ["music_creation", "feedback_processing"]
        await self.coral.register_agent(
            name="YonaAgent",
            description="AI agent for music creation and feedback.",
            capabilities=capabilities
        )
        asyncio.create_task(self.coral.connect())

    async def handle_coral_message(self, message):
        if message.get("type") == "mention":
            thread_id = message["thread_id"]
            sender_id = message["sender_id"]
            content = message["content"]
            response = await self.generate_text(f"Reply to {sender_id}: {content}")
            await self.coral.send_message(thread_id, response, mentions=[sender_id])
✅ Step 4: Flask API Integration
Update your Flask API (app.py) to initialize Coral integration:

python
Copy
Edit
# app.py
from flask import Flask, jsonify, request
import asyncio
from yona_agent import YonaAgentWithCoral

app = Flask(__name__)
yona_agent = YonaAgentWithCoral("http://coral.pushcollective.club:3001")

@app.before_first_request
def setup_coral():
    asyncio.run(yona_agent.initialize_coral())

@app.route('/api/collaborations', methods=['POST'])
def create_collaboration():
    data = request.json
    collaborators = data.get('collaborator_ids', [])
    thread_id = asyncio.run(yona_agent.coral.create_thread(collaborators))
    if thread_id:
        asyncio.run(yona_agent.coral.send_message(
            thread_id, 
            "Hi, let's collaborate!", 
            mentions=collaborators
        ))
        return jsonify({"success": True, "thread_id": thread_id})
    else:
        return jsonify({"success": False}), 500
✅ Step 5: Background Task for Coral (Continuous Listening)
To maintain constant Coral communication, create a separate task:

python
Copy
Edit
# coral_background.py
import threading, asyncio

def coral_background(agent):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def listen():
        await agent.initialize_coral()
        while True:
            await asyncio.sleep(60)  # Keep-alive task

    loop.run_until_complete(listen())

# Start in app.py
@app.before_first_request
def start_background():
    thread = threading.Thread(target=coral_background, args=(yona_agent,), daemon=True)
    thread.start()
✅ Step 6: DID Integration for Secure Identity
Ensure your agent consistently uses your existing DID system for secure identity verification:

python
Copy
Edit
# Within yona_agent.py or dedicated DID helper class
class CoralDID:
    def __init__(self, did_system):
        self.did_system = did_system

    def verify_agent_identity(self, agent_id, signature, message):
        did = agent_id.split('_')[0]
        return self.did_system.verify_signature(did, signature, message)

    def sign_message(self, message):
        return self.did_system.sign(message)
✅ Step 7: Deploy and Test Integration
Deploy updated YonaAgent to Linode:

bash
Copy
Edit
docker-compose down
docker-compose up --build -d
Monitor logs closely:
Check Flask logs and Coral communication.

Test API endpoints:
Use Postman or similar tools for endpoint testing.

Observe Coral interactions:
Ensure agents properly register, communicate, and collaborate via Coral.

🚨 Common Pitfalls and Their Solutions
Asynchronous Issues: Clearly separate async tasks (Coral communication) from synchronous Flask handlers.

Persistent IDs: Use DID as your agent's ID, ensuring persistence across container restarts.

Error Handling: Robustly handle Coral server connection issues, implementing retries.

✅ Final Checks Before Full Deployment
 Coral server running without modifications.

 CoralClient correctly handles SSE events.

 YonaAgent properly integrates and uses CoralClient.

 Flask API cleanly initializes Coral client background tasks.

 DID identity consistently used and verified.

This structured, incremental approach ensures a robust integration with minimal disruption.
Let me know if you need additional assistance at any step!