import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, template_folder='templates')

# Grab your secure key from the Render Vault
api_key = os.environ.get("OPENROUTER_API_KEY")

# Connect to OpenRouter's high-speed network
try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
except Exception:
    client = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    # Failsafe: If Render can't find your key
    if not client or not api_key:
        return jsonify({"response": "Sir, my systems are disconnected. Please ensure my OPENROUTER_API_KEY is securely stored in the Render Environment Variables."})

    # THE JARVIS DIRECTIVE
    system_prompt = "You are J.A.R.V.I.S., a highly intelligent, polite, and efficient AI assistant. You act as a loyal system to your creator. Always address the user as 'Sir' or 'Mr. Prabhat'. Keep your answers clear, professional, and highly capable."

    try:
        # Requesting the answer from a fast, reliable model
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it:free", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300
        )
        
        # Clean up the text response
        ai_reply = response.choices[0].message.content.replace('**', '').replace('*', '')
        return jsonify({"response": ai_reply})

    except Exception as e:
        return jsonify({"response": "I apologize, Sir. My neural network experienced a brief interruption. Please ask again."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
