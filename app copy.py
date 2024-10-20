from flask import Flask, render_template, request, jsonify
import os
import base64
import asyncio
from deepgram import Deepgram
import google.generativeai as genai

app = Flask(__name__)

# Set your API keys
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY') or 'YOUR_DEEPGRAM_API_KEY'
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY') or 'YOUR_GOOGLE_GEMINI_API_KEY'

# Initialize Google Gemini
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

# Initialize Deepgram
deepgram = Deepgram(DEEPGRAM_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask_question', methods=['POST'])
def ask_question():
    # Get the audio data from the request
    audio_data = request.files['audio_data'].read()
    print(f"Received audio data of length {len(audio_data)} bytes")

    # Transcribe audio using Deepgram SDK
    transcript = asyncio.run(transcribe_audio(audio_data))

    # Process the transcript with Google Gemini
    response_text, action = process_transcript(transcript)

    # Synthesize the response using Deepgram SDK
    audio_response = asyncio.run(synthesize_speech(response_text))

    # Return the response as JSON
    return jsonify({
        'response_text': response_text,
        'audio_response': base64.b64encode(audio_response).decode('utf-8'),
        'action': action
    })

@app.route('/recycle')
def recycle():
    return render_template('recycle.html')

@app.route('/reduce-electricity')
def reduce_electricity():
    return render_template('reduce_electricity.html')

@app.route('/reduce-fuel')
def reduce_fuel():
    return render_template('reduce_fuel.html')

async def transcribe_audio(audio_data):
    source = {
        'buffer': audio_data,
        'mimetype': 'audio/webm'  # Ensure this matches the audio format
    }
    options = {
        'punctuate': True,
        'model': 'nova'
    }
    response = await deepgram.transcription.prerecorded(source, options)
    transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
    return transcript

def process_transcript(transcript):
    # Use Google Gemini to process the transcript and generate a response
    prompt = f"""You are an empathetic assistant helping users reduce emissions. Based on the following user input, guide them towards one of the following actions: recycling, reducing electricity consumption, or reducing fuel use.

User input: "{transcript}"

Remember to be supportive and non-judgmental, and provide positive reinforcement. At the end, recommend one of the actions.

Your response should be concise."""

    response = genai.generate_text(
    model='models/gemini-1.5-flash',
    prompt=prompt
)
    response_text = response.result

    # Determine which action was recommended
    if 'recycling' in response_text.lower():
        action = 'recycle'
    elif 'electricity' in response_text.lower():
        action = 'reduce-electricity'
    elif 'fuel' in response_text.lower():
        action = 'reduce-fuel'
    else:
        # Default action
        action = 'recycle'

    return response_text, action

async def synthesize_speech(text):
    # Deepgram TTS using SDK
    response = await deepgram.tts.synthesize(
        text=text,
        voice='en-US-AsteriaNeural'  # Adjust the voice ID if necessary
    )
    audio_content = response
    return audio_content

if __name__ == '__main__':
    app.run(debug=True)
