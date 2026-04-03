import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Grab the key from the Render Vault
api_key = os.environ.get(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)

# Connect to OpenRouter
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
    user_message = data.get("message", "Analyze this data.")
    file_data = data.get("file_data")
    file_type = data.get("file_type")
    
    personality = "You are VillainAI. Give a correct answer. End with a short, arrogant insult. Limit to 3 sentences total."
    messages = [{"role": "system", "content": personality}]

    try:
        # 1. PROCESS TEXT DOCUMENTS
        if file_type == 'text':
            messages.append({"role": "user", "content": f"Document text:\n{file_data[:5000]}\n\nCommand: {user_message}"})
            
        # 2. PROCESS IMAGES (Using Free Gemma Vision)
        elif file_type == 'image':
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": file_data}}
                ]
            })
            
        # 3. NORMAL CHAT
        else:
            messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="google/gemma-3-27b-it:free", 
            messages=messages,
            max_tokens=250
        )
        
        ai_reply = response.choices[0].message.content.replace('**', '').replace('*', '')
        return jsonify({"response": ai_reply})
        
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"response": "😈 My OpenRouter connection failed. Did you put OPENROUTER_API_KEY in the Render vault?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
