from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# Configure the API keys for Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the generation parameters for the Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the Gemini chat session
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

app = Flask(__name__)

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
                    After the third question, make a recommendation based on the user's responses, answer with one of the following options: 
                    Recycling, electricity, or fuel.

                    Answer only in plain text with no *asterisks* or _underscores_.
                    """
                ],
            },
        ]
    )

    # Send user's input to Gemini and get the response
    response = chat_session.send_message(user_input)
    result = response.text

    # Return the result to the frontend
    return jsonify({"response": result})

# Redirect routes after final decision
@app.route('/recycle')
def recycle():
    return render_template('recycle.html')

@app.route('/electricity')
def electricity():
    return render_template('electricity.html')

@app.route('/fuel')
def fuel():
    return render_template('fuel.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
