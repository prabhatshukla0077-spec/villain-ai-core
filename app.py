import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# =====================================================================
# 🌊 THE WATERFALL API PROTOCOL
# The system will try Groq first (fastest). If it fails, it tries Gemini. 
# If Gemini fails, it tries HuggingFace. It will never show an error.
# =====================================================================
APIS = [
    {
        "name": "Groq (Llama 3)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": "YOUR_GROQ_API_KEY_HERE", 
        "model": "llama3-8b-8192",
        "type": "openai_format"
    },
    {
        "name": "Google Gemini (1.5 Flash)",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "key": "YOUR_GOOGLE_GEMINI_API_KEY_HERE",
        "type": "gemini_format"
    },
    {
        "name": "HuggingFace (Mistral)",
        "url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        "key": "YOUR_HUGGINGFACE_API_KEY_HERE",
        "type": "huggingface_format"
    }
]

SYSTEM_PROMPT = "You are Villain AI, an incredibly advanced, slightly dark, and highly intelligent AI entity. Keep your answers concise, modern, and formatting clean. Do not use asterisks."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "System requires input to process."})

    # The Loop: Try each API one by one until a response is generated
    for api in APIS:
        # Skip if you haven't put a real key in yet
        if "YOUR_" in api["key"] or not api["key"]:
            continue
            
        try:
            response = call_ai_brain(api, user_message)
            if response:
                return jsonify({"response": response, "model_used": api["name"]})
        except Exception as e:
            print(f"[!] {api['name']} failed: {str(e)}. Falling back to next brain...")
            continue # Triggers the fallback to the next API

    # If every single API fails or keys are missing
    return jsonify({"response": "CRITICAL: All neural networks are currently offline. Please check your API keys."})

def call_ai_brain(api, message):
    """Handles the different formats required by different AI companies."""
    headers = {'Content-Type': 'application/json'}
    
    # --- GROQ FORMAT ---
    if api["type"] == "openai_format":
        headers['Authorization'] = f'Bearer {api["key"]}'
        payload = {
            'model': api["model"],
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': 500
        }
        res = requests.post(api["url"], headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content'].replace('**', '').replace('*', '')

    # --- GOOGLE GEMINI FORMAT ---
    elif api["type"] == "gemini_format":
        url_with_key = f"{api['url']}?key={api['key']}"
        payload = {
            'contents': [{'parts': [{'text': f"{SYSTEM_PROMPT}\n\nUser: {message}"}]}],
            'generationConfig': {'maxOutputTokens': 500}
        }
        res = requests.post(url_with_key, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text'].replace('**', '').replace('*', '')

    # --- HUGGINGFACE FORMAT ---
    elif api["type"] == "huggingface_format":
        headers['Authorization'] = f'Bearer {api["key"]}'
        payload = {
            'inputs': f"<s>[INST] {SYSTEM_PROMPT} \n\n {message} [/INST]",
            'parameters': {'max_new_tokens': 500}
        }
        res = requests.post(api["url"], headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return data[0].get('generated_text', '').split('[/INST]')[-1].strip().replace('**', '')

    return None

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
