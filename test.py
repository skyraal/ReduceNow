import os
import json
from flask import Flask, render_template
from flask_socketio import SocketIO
from dotenv import load_dotenv
import websockets
import asyncio

# Load environment variables from .env
load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Flask app and WebSocket setup
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

async def send_audio_to_deepgram(ws, audio_data):
    async with websockets.connect(
        'wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1',
        extra_headers={'Authorization': f'token {DEEPGRAM_API_KEY}'}
    ) as deepgram_ws:
        await deepgram_ws.send(audio_data)

        async for message in deepgram_ws:
            data = json.loads(message)
            transcript = data['channel']['alternatives'][0]['transcript']
            if transcript:
                print(f'Transcript: {transcript}')
                # Emit the transcript back to the client
                socketio.emit('transcript', {'transcript': transcript})

@socketio.on('audio_chunk')
def handle_audio_chunk(audio_chunk):
    # Start an asyncio task to send audio to Deepgram
    asyncio.run(send_audio_to_deepgram(None, audio_chunk))

if __name__ == '__main__':
    socketio.run(app, debug=True)
