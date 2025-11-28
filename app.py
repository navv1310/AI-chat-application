from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import requests
import re

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in the .env file")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Function to clean and simplify Gemini's Markdown output
def clean_response(text):
    text = re.sub(r'\*{1,2}', '', text)           # Remove * and ** used for emphasis
    text = re.sub(r'\n{2,}', '\n', text)          # Reduce multiple newlines to one
    return text.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    payload = {
        "contents": [{
            "parts": [{"text": user_input}]
        }]
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(GEMINI_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        try:
            reply = data['candidates'][0]['content']['parts'][0]['text']
            reply = clean_response(reply)  # Clean the raw text
            return jsonify({"response": reply})
        except (KeyError, IndexError):
            return jsonify({"response": "Error: Unexpected response structure."}), 500
    else:
        return jsonify({"response": f"Error: {response.status_code}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
