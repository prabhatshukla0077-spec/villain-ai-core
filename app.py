import os
import requests
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# This is the Smart Instruct Brain (Better at comparing things)
TEXT_API = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    # We give the AI a clear instruction to be a Villain
    prompt = f"<s>[INST] You are VillainAI. Answer the following question accurately but end with a short villainous insult: {user_message} [/INST]"

    try:
        # Requesting the answer from the free brain
        response = requests.post(TEXT_API, json={"inputs": prompt, "parameters": {"max_new_tokens": 250}})
        result = response.json()
        
        # Extracting only the AI's new answer
        if isinstance(result, list) and len(result) > 0:
            full_text = result[0].get('generated_text', '')
            # This splits the text to only show the answer, not the prompt
            ai_reply = full_text.split('[/INST]')[-1].strip()
        else:
            ai_reply = "My neural processors are loading. Ask again in a moment, human."

        # Clean up formatting
        ai_reply = ai_reply.replace('**', '').replace('*', '')

        return jsonify({"response": ai_reply})

    except Exception as e:
        return jsonify({"response": "😈 My dark energy is fluctuating. Refresh and try again."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
