import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# SWITCHED: Using a lightweight model that loads instantly
TEXT_API = "https://api-inference.huggingface.co/models/google/gemma-1.1-2b-it"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    # Simple prompt for the smaller brain
    prompt = f"User: {user_message}\nAI: You are VillainAI. Answer the user's question accurately but end with a short villainous insult."

    try:
        # Request with a 20-second timeout to prevent infinite loading
        response = requests.post(TEXT_API, json={"inputs": prompt}, timeout=20)
        result = response.json()
        
        # Handle the loading state automatically
        if isinstance(result, dict) and "error" in result and "currently loading" in result["error"]:
            return jsonify({"response": "😈 My brain is warming up. Give me 10 more seconds then ask again."})

        # Extract answer
        if isinstance(result, list) and len(result) > 0:
            ai_reply = result[0].get('generated_text', '').split('AI:')[-1].strip()
        else:
            ai_reply = "My processors are overwhelmed by your stupidity. Try again."

        return jsonify({"response": ai_reply})

    except Exception:
        return jsonify({"response": "😈 Connection to the dark dimension failed. Refresh the page."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
