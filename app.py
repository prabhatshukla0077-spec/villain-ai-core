import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# 1. Grab the key securely from the Render Vault
("OPENROUTER_API_KEY") = "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"


# 2. Connect to OpenRouter's high-speed network
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    # THE NEW PERSONALITY: Friendly, loyal, and always says "Sir"
    personality = "You are a highly polite, friendly AI assistant. You act like a loyal friend. You MUST refer to the user as 'Sir' in your response."
    
    try:
        # Send the message to the fast OpenRouter brain
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it:free", 
            messages=[
                {"role": "system", "content": personality},
                {"role": "user", "content": user_message}
            ],
            max_tokens=250
        )
        
        # Extract the reply and clean up any formatting
        ai_reply = response.choices[0].message.content.replace('**', '').replace('*', '')
        return jsonify({"response": ai_reply})
        
    except Exception as e:
        print(f"API ERROR: {e}")
        return jsonify({"response": "I sincerely apologize, Sir. I am having trouble connecting to my API. Please ensure my OPENROUTER_API_KEY is saved in the Render Environment Variables!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
