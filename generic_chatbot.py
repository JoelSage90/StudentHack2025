import os
import asyncio
from pyneuphonic import Neuphonic, WebsocketEvents
from pyneuphonic.player import AsyncAudioPlayer, AsyncAudioRecorder
from pyneuphonic.models import APIResponse, AgentResponse, AgentConfig
import threading

class ChatbotRunner:
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_chat(self):
        asyncio.run_coroutine_threadsafe(self.chatbot.start_chat(), self.loop)

    def stop_chat(self):
        asyncio.run_coroutine_threadsafe(self.chatbot.stop_chat(), self.loop)

class SpeechToSpeechChatbot:
    def __init__(self, apiKey):
        self.client = Neuphonic(api_key=apiKey)
        self.ws = self.client.agents.AsyncWebsocketClient()
        self.player = AsyncAudioPlayer()
        self.recorder = AsyncAudioRecorder(sampling_rate=16000, websocket=self.ws, player=self.player)

    async def start_chat(self):
        async def on_message(message: APIResponse[AgentResponse]):
            if message.data.type == 'audio_response':
                await self.player.play(message.data.audio)  # Play the response audio
            elif message.data.type == 'user_transcript':
                print(f'User: {message.data.text}')
            elif message.data.type == 'llm_response':
                print(f'Agent: {message.data.text}')
            elif message.data.type == 'stop_audio_response':
                await self.player.stop_playback()  # Stop audio on user interruption

        async def on_close():
            await self.player.close()
            await self.recorder.close()

        self.ws.on(WebsocketEvents.MESSAGE, on_message)
        self.ws.on(WebsocketEvents.CLOSE, on_close)

        await self.player.open()
        await self.ws.open(agent_config=AgentConfig(sampling_rate=16000))

        # Start recording user speech
        await self.recorder.record()

    async def stop_chat(self):
        await self.ws.close()