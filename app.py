import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, template_folder='templates')

# Securely grab the API key from Render
api_key = os.environ.get("OPENROUTER_API_KEY")

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
    
    if not client or not api_key:
        return jsonify({"response": "Sir, my systems are disconnected. Please ensure my OPENROUTER_API_KEY is securely stored in the Render Environment Variables."})

    # THE J.A.R.V.I.S. DIRECTIVE
    system_prompt = "You are J.A.R.V.I.S., a highly advanced AI system created to assist Mr. Prabhat. You are polite, highly efficient, and always address him as 'Sir' or 'Mr. Prabhat'. Keep your answers clear, professional, and conversational. Do not use markdown formatting like asterisks or bold text, as your responses will be read out loud by a voice synthesizer."

    try:
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it:free", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200
        )
        
        ai_reply = response.choices[0].message.content.replace('**', '').replace('*', '')
        return jsonify({"response": ai_reply})

    except Exception as e:
        return jsonify({"response": "I apologize, Sir. My neural network experienced a brief interruption. Please ask again."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
