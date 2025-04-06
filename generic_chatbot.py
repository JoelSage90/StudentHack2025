import os
import asyncio
from pyneuphonic import Neuphonic, Agent, AgentConfig
import threading
from dotenv import load_dotenv
load_dotenv()
apiKey = os.getenv("NEUPHONIC_API_KEY")

#threading used to run tasks concurrently (bg tasks)
chatbot_thread = None
chatbot_agent = None
chatbot_loop = None

class genericAssistant:
    def __init__(self,context):
        self.context = context
        self.client = Neuphonic(api_key = apiKey)

    async def run(self):

        global chatbot_agent
        agent_id = self.client.agents.create(
        name='Agent 1',
        prompt=f"You are talking to a person with Alzheimer's. Help them recall their memories. Here is there stored memories {self.context}",
        greeting='Hi, how can I help you today?').data['agent_id']

        chatbot_agent = Agent(self.client, agent_id = agent_id, tts_model = 'neu_hq')
        await chatbot_agent.start()

    def start_background(self):
        global chatbot_loop, chatbot_thread
        chatbot_loop = asyncio.new_event_loop()
        def run_loop():
            asyncio.set_event_loop(chatbot_loop)
            chatbot_loop.run_until_complete(self.run())

        chatbot_thread = threading.Thread(target=run_loop)
        chatbot_thread.start()

def stop_chatbot():
    global chatbot_agent, chatbot_loop
    if chatbot_agent and chatbot_loop:
        chatbot_loop.call_soon_threadsafe(asyncio.create_task, chatbot_agent.stop())