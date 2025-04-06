import os
import asyncio
from pyneuphonic import Neuphonic, WebsocketEvents
from pyneuphonic.player import AsyncAudioPlayer, AsyncAudioRecorder
from pyneuphonic.models import APIResponse, AgentResponse, AgentConfig

class SpeechToSpeechChatbot:
    def __init__(self, api_key):
        self.client = Neuphonic(api_key=api_key)
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