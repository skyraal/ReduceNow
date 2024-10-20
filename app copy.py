from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import google.generativeai as genai
from deepgram.utils import verboselogs
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    SpeakWebSocketEvents,
    SpeakWSOptions,
)
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# Configure the API keys for Gemini and Deepgram
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Gemini chat session
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

# Flask app initialization
app = Flask(__name__)

# Function to connect to Deepgram WebSocket TTS and play audio
def text_to_speech_via_websocket(text):
    TTS_TEXT = text
    global warning_notice
    warning_notice = True

    try:
        # Create a Deepgram client
        config = DeepgramClientOptions(
            options={"speaker_playback": "true"},
        )
        deepgram = DeepgramClient("", config)

        # Create a WebSocket connection to Deepgram
        dg_connection = deepgram.speak.websocket.v("1")

        # WebSocket event handlers
        def on_open(self, open, **kwargs):
            print(f"WebSocket opened: {open}")

        def on_binary_data(self, data, **kwargs):
            global warning_notice
            if warning_notice:
                print("Received binary data")
                warning_notice = False
            # Here you can handle the binary data for audio (stream to a player or save to a file)

        def on_metadata(self, metadata, **kwargs):
            print(f"Metadata received: {metadata}")

        def on_close(self, close, **kwargs):
            print(f"Connection closed: {close}")

        def on_error(self, error, **kwargs):
            print(f"Error occurred: {error}")

        # Register WebSocket event handlers
        dg_connection.on(SpeakWebSocketEvents.Open, on_open)
        dg_connection.on(SpeakWebSocketEvents.AudioData, on_binary_data)
        dg_connection.on(SpeakWebSocketEvents.Metadata, on_metadata)
        dg_connection.on(SpeakWebSocketEvents.Close, on_close)
        dg_connection.on(SpeakWebSocketEvents.Error, on_error)

        # Start WebSocket connection with specified options
        options = SpeakWSOptions(
            model="aura-asteria-en",  # Select the voice model
            encoding="linear16",  # Audio encoding
            sample_rate=16000,  # Sample rate for audio
        )

        if dg_connection.start(options) is False:
            print("Failed to start WebSocket connection")
            return

        # Send text to Deepgram for TTS conversion
        dg_connection.send_text(TTS_TEXT)

        # Flush the WebSocket connection (mandatory)
        dg_connection.flush()

        # Wait for WebSocket to complete
        dg_connection.wait_for_complete()

        # Close the connection
        dg_connection.finish()

        return "Audio played successfully"

    except Exception as e:
        print(f"An error occurred during WebSocket TTS: {e}")
        return None


# Function to forward user based on the result
def forward_user_based_on_choice(result):
    if "recycling" in result.lower():
        return redirect(url_for('recycle'))
    elif "electricity" in result.lower():
        return redirect(url_for('electricity'))
    elif "fuel" in result.lower():
        return redirect(url_for('fuel'))
    else:
        return jsonify({"error": "Sorry, I couldn't understand the recommendation."})


# Main chatbot route (frontend)
@app.route('/')
def index():
    return render_template('index.html')


# Chatbot response route (backend logic)
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']

    # Start a chat session with Gemini
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    """
                    You are a sustainability expert tasked with helping individuals reduce their carbon footprint.
                    Your goal is to ask the user five or less behavioral questions to determine which method of reducing emissions is most suitable for them: 
                    1. Recycling waste
                    2. Reducing electricity consumption
                    3. Reducing fuel use.

                    Ask each question one at a time, evaluating the user's preferences, habits, and comfort with each method.
                    After the fifth question, make a recommendation based on the user's responses, answer with one of the following options: 
                    Recycling, electricity, or fuel. Do not use the word recycle, electricity, or fuel in the five questions.
                    """
                ],
            },
        ]
    )

    # Send user's input to Gemini and get the response
    response = chat_session.send_message(user_input)
    result = response.text

    # Convert the chatbot's text to speech using Deepgram WebSocket TTS
    tts_result = text_to_speech_via_websocket(result)

    # Return the chatbot result and TTS result to the frontend
    return jsonify({"response": result, "tts_result": tts_result})


# Redirect routes after final decision
@app.route('/recycle')
def recycle():
    return render_template('recycle.html')

@app.route('/submit-image', methods=['POST'])
def submit_image():
    image_data = request.json['image']
    image_data = image_data.split(",")[1]  # Remove the base64 header
    image = Image.open(BytesIO(base64.b64decode(image_data)))

    # Encode image for API
    base64_img = encode_image(image)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {llm_api_key}",
    }

    # Payload for the LLM API
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"},
                    },
                    {
                        "type": "text",
                        "text": "Based on the product, provide the best recycling recommendation and calculate the amount of CO2 emissions that can be reduced if this product is properly recycled."
                    }
                ],
            }
        ],
        "model": "meta-llama/Llama-3.2-90B-Vision-Instruct",
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    # Call the LLM API
    response = requests.post("https://api.hyperbolic.xyz/v1/chat/completions", headers=headers, json=payload)
    result = response.json()

    # Extract the recommendation and emission reduction from the API response
    try:
        recycling_suggestion = result['choices'][0]['message']['content']
        emissions_reduction = "Unknown"  # Adjust this depending on how the LLM returns it
        for line in recycling_suggestion.split("\n"):
            if "CO2" in line:
                emissions_reduction = line
    except KeyError:
        recycling_suggestion = "Sorry, something went wrong with the LLM response."
        emissions_reduction = "Unknown"

    return jsonify({
        "recycling_suggestion": recycling_suggestion,
        "emissions_reduction": emissions_reduction
    })


@app.route('/electricity')
def electricity():
    return render_template('electricity.html')

@app.route('/fuel')
def fuel():
    return render_template('fuel.html')



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)