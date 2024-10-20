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
def forward_user_based_on_choice(choice):
    if choice.lower() == "recycling":
        return redirect(url_for('recycle'))
    elif choice.lower() == "electricity":
        return redirect(url_for('electricity'))
    elif choice.lower() == "fuel":
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
                    "In three questions or less, you are trying to see which method of reducing emissions is most suitable for the users: Recycling, Reducing electricity consumption, or Reducing fuel use. After three questions return the recommendation in one word recycle, fuel, or electricity."
                ],
            },
        ]
    )

    # Send user's input to Gemini and get the response
    response = chat_session.send_message(user_input)
    result = response.text
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
