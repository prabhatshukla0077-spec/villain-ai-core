import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# This is a much smarter Conversational Brain (Mistral)
TEXT_API = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-v0.1"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    # The instructions for the AI's personality
    prompt = f"<s>[INST] You are VillainAI. Answer this question correctly but with a short villainous insult at the end: {user_message} [/INST]"

    try:
        # Send your question to the free smart brain
        response = requests.post(TEXT_API, json={"inputs": prompt})
        result = response.json()
        
        # Get the text answer
        if isinstance(result, list) and len(result) > 0:
            ai_reply = result[0].get('generated_text', '').split('[/INST]')[-1].strip()
        else:
            ai_reply = "My neural processors are rebooting. Try again, worm."

        # Clean up any messy stars/markdown
        ai_reply = ai_reply.replace('**', '').replace('*', '')

        return jsonify({"response": ai_reply})

    except Exception as e:
        return jsonify({"response": "😈 Connection lost to the dark dimension. Refresh the page."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
