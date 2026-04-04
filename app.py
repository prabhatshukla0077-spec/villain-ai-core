import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, template_folder='templates')

# Your exact key is perfectly placed here
api_key = "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"

try:
    client = OpenAI(
        api_key=api_key, 
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://villain-ai-prabhat.onrender.com",
            "X-Title": "VillainAI"
        }
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

    model_to_use = "meta-llama/llama-3-8b-instruct:free"
    messages = [{"role": "system", "content": system_prompt}]

    try:
        if file_type == 'image' and file_data:
            model_to_use = "meta-llama/llama-3.2-11b-vision-instruct:free" 
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
        # This will print the EXACT reason it is failing to your screen
        return jsonify({"response": f"SYSTEM ERROR DETECTED: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
