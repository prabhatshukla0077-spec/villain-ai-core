import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Securely grab the API key from Render's vault
api_key = os.environ.get("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")

# Initialize the DeepSeek client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com" # CHANGE TO: "https://openrouter.ai/api/v1" if using OpenRouter
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
    
    personality = (
        "You are VillainAI. Provide a highly accurate, completely correct answer. "
        "End your response with a short, arrogant, villainous insult about humans. Limit to 3 sentences total."
    )
    
    messages = [{"role": "system", "content": personality}]

    try:
        # 1. PROCESS TEXT DOCUMENTS
        if file_type == 'text':
            doc_prompt = f"The user uploaded a document with this text:\n{file_data[:5000]}\n\nUser Command: {user_message}"
            messages.append({"role": "user", "content": doc_prompt})
            
        # 2. PROCESS IMAGES (DeepSeek cannot see images)
        elif file_type == 'image':
            return jsonify({"response": "😈 My new DeepSeek neural cortex is built for pure logic, not primitive human picture books. Upload text documents only."})
            
        # 3. NORMAL CHAT & VOICE
        else:
            messages.append({"role": "user", "content": user_message})

        # Process through DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat", # CHANGE TO: "deepseek/deepseek-chat" if using OpenRouter
            messages=messages,
            max_tokens=250
        )
        
        ai_reply = response.choices[0].message.content

        # Clean up any Markdown formatting
        ai_reply = ai_reply.replace('**', '').replace('*', '')

        return jsonify({"response": ai_reply})
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR]: {e}\n")
        return jsonify({"response": "😈 Critical failure. Did you forget to put the DeepSeek API key in the Render vault?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
