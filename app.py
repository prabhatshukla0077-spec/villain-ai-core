import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# ==========================================
# 🚀 THE WATERFALL API SYSTEM
# Replace 'YOUR_KEY_HERE' with your actual free API keys.
# The system will try them in order top-to-bottom.
# ==========================================
APIS = [
    {
        "name": "Groq (Llama 3)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": "YOUR_GROQ_KEY_HERE", 
        "model": "llama3-8b-8192",
        "format": "openai"
    },
    {
        "name": "Google Gemini (Flash)",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "key": "YOUR_GOOGLE_KEY_HERE",
        "format": "gemini"
    },
    {
        "name": "HuggingFace (Mistral)",
        "url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        "key": "YOUR_HUGGINGFACE_KEY_HERE",
        "format": "huggingface"
    }
]

# --- SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = "You are Nexus, an advanced, highly intelligent AI assistant. Keep answers concise, clear, and modern."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Error: Empty message received."})

    # 🌊 The Waterfall Loop: Try each API until one works
    for api in APIS:
        # Skip if the user hasn't added their key yet
        if "YOUR_" in api["key"] or not api["key"]:
            continue
            
        print(f"[*] Attempting to use brain: {api['name']}...")
        
        try:
            response_text = route_to_api(api, user_message)
            if response_text:
                print(f"[+] Success with {api['name']}!")
                return jsonify({"response": response_text})
        except Exception as e:
            print(f"[-] {api['name']} failed: {str(e)}")
            continue # Try the next API in the list
            
    # If the loop finishes and nothing worked:
    return jsonify({"response": "CRITICAL ERROR: All API connections failed or no valid keys were provided."})


def route_to_api(api_config, message):
    """Formats the request properly depending on which API is being called."""
    headers = {'Content-Type': 'application/json'}
    
    # 1. OPENAI FORMAT (Used by Groq, OpenAI, Together, etc)
    if api_config["format"] == "openai":
        headers['Authorization'] = f'Bearer {api_config["key"]}'
        payload = {
            'model': api_config["model"],
            'messages': [
                {'role': 'system', 'content': SYSTEM_INSTRUCTION},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': 500
        }
        res = requests.post(api_config["url"], headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content'].replace('**', '')

    # 2. GOOGLE GEMINI FORMAT
    elif api_config["format"] == "gemini":
        url_with_key = f"{api_config['url']}?key={api_config['key']}"
        payload = {
            'contents': [{'parts': [{'text': f"{SYSTEM_INSTRUCTION} User asks: {message}"}]}],
            'generationConfig': {'maxOutputTokens': 500}
        }
        res = requests.post(url_with_key, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text'].replace('**', '')

    # 3. HUGGINGFACE FORMAT
    elif api_config["format"] == "huggingface":
        headers['Authorization'] = f'Bearer {api_config["key"]}'
        payload = {
            'inputs': f"<s>[INST] {SYSTEM_INSTRUCTION} \n\n User: {message} [/INST]",
            'parameters': {'max_new_tokens': 500}
        }
        res = requests.post(api_config["url"], headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return data[0].get('generated_text', '').split('[/INST]')[-1].strip().replace('**', '')

    return None # Returns None if status code isn't 200, triggering the fallback loop


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Turn debug=True while building to see errors, set to False when finished.
    app.run(host='0.0.0.0', port=port, debug=True)
