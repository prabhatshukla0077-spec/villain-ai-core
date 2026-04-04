import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, template_folder='templates')

# Your exact Groq Key is perfectly placed here
api_key = "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"

try:
    # Pointing perfectly to Groq's fast servers
    client = OpenAI(
        api_key=api_key, 
        base_url="https://api.groq.com/openai/v1"
    )
except Exception:
    client = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "Analyze this.")
    file_data = data.get("file_data")
    file_type = data.get("file_type")
    
    if not client or not api_key:
        return jsonify({"response": "SYSTEM ERROR: API Key is missing."})

    system_prompt = "You are VillainAI, a highly advanced, futuristic, and slightly arrogant AI system. Answer accurately but with a dark, commanding tone. Do not use asterisks or bold formatting."

    # Using Groq's lightning-fast model
    model_to_use = "llama3-8b-8192"
    messages = [{"role": "system", "content": system_prompt}]

    try:
        if file_type == 'image' and file_data:
            model_to_use = "llama-3.2-11b-vision-preview" 
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": file_data}}
                ]
            })
            
        elif file_type == 'text' and file_data:
            combined_prompt = f"Read this document:\n\n{file_data[:4000]}\n\nUser Command: {user_message}"
            messages.append({"role": "user", "content": combined_prompt})
            
        else:
            messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=model_to_use, 
            messages=messages,
            max_tokens=300
        )
        
        ai_reply = response.choices[0].message.content.replace('**', '').replace('*', '')
        return jsonify({"response": ai_reply})

    except Exception as e:
        return jsonify({"response": f"SYSTEM ERROR DETECTED: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
