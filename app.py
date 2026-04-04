import os
from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__, template_folder='templates')

# ===== MULTIPLE API KEYS (4-5 FALLBACK SYSTEM) =====
# Get these from: 
# Groq: https://console.groq.com/keys
# Anthropic: https://console.anthropic.com/account/keys
# HuggingFace: https://huggingface.co/settings/tokens
# Google Gemini: https://makersuite.google.com/app/apikeys

APIS = {
    'groq': {
        'key': 'gsk_YOUR_GROQ_KEY_HERE',  # Replace with your key
        'url': 'https://api.groq.com/openai/v1/chat/completions',
        'model': 'mixtral-8x7b-32768',  # Updated working model
        'priority': 1
    },
    'anthropic': {
        'key': 'sk-ant-YOUR_ANTHROPIC_KEY_HERE',  # Replace with your key
        'url': 'https://api.anthropic.com/v1/messages',
        'model': 'claude-3-haiku-20240307',
        'priority': 2
    },
    'huggingface': {
        'key': 'hf_YOUR_HUGGINGFACE_KEY_HERE',  # Replace with your key
        'url': 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1',
        'priority': 3
    },
    'google': {
        'key': 'YOUR_GOOGLE_GEMINI_KEY_HERE',  # Replace with your key
        'url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
        'priority': 4
    }
}

@app.route('/')
def home():
    return render_template('index.html')

# ===== MAIN CHAT ENDPOINT =====
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "Analyze this.")
    file_data = data.get("file_data")
    file_type = data.get("file_type")

    # Try each API in priority order
    response_text = None
    
    # Try Groq First
    if not response_text:
        response_text = try_groq(user_message, file_data, file_type)
    
    # Try Anthropic if Groq fails
    if not response_text:
        response_text = try_anthropic(user_message, file_data, file_type)
    
    # Try HuggingFace if Anthropic fails
    if not response_text:
        response_text = try_huggingface(user_message, file_data, file_type)
    
    # Try Google Gemini if HuggingFace fails
    if not response_text:
        response_text = try_google(user_message, file_data, file_type)
    
    # If all fail, return default response
    if not response_text:
        response_text = "CRITICAL SYSTEM FAILURE: All API connections down. Check your API keys and internet connection."

    return jsonify({"response": response_text})

# ===== API 1: GROQ (FASTEST) =====
def try_groq(message, file_data, file_type):
    try:
        api_key = APIS['groq']['key']
        if 'YOUR_' in api_key:
            return None  # Key not set
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        system_prompt = "You are VillainAI, a highly advanced, futuristic AI system. Answer accurately with a dark commanding tone. Keep responses under 300 words."
        
        payload = {
            'model': APIS['groq']['model'],
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': 300,
            'temperature': 0.7
        }
        
        response = requests.post(APIS['groq']['url'], headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'].replace('**', '').replace('*', '')
        return None
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return None

# ===== API 2: ANTHROPIC CLAUDE =====
def try_anthropic(message, file_data, file_type):
    try:
        api_key = APIS['anthropic']['key']
        if 'YOUR_' in api_key:
            return None  # Key not set
        
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        
        payload = {
            'model': APIS['anthropic']['model'],
            'max_tokens': 300,
            'system': 'You are VillainAI, a highly advanced AI. Answer with dark commanding tone. Keep it under 300 words.',
            'messages': [
                {'role': 'user', 'content': message}
            ]
        }
        
        response = requests.post(APIS['anthropic']['url'], headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text'].replace('**', '').replace('*', '')
        return None
    except Exception as e:
        print(f"Anthropic API Error: {str(e)}")
        return None

# ===== API 3: HUGGINGFACE =====
def try_huggingface(message, file_data, file_type):
    try:
        api_key = APIS['huggingface']['key']
        if 'YOUR_' in api_key:
            return None  # Key not set
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'inputs': message,
            'parameters': {
                'max_length': 300,
                'temperature': 0.7
            }
        }
        
        response = requests.post(APIS['huggingface']['url'], headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get('generated_text', '').replace('**', '').replace('*', '')
        return None
    except Exception as e:
        print(f"HuggingFace API Error: {str(e)}")
        return None

# ===== API 4: GOOGLE GEMINI =====
def try_google(message, file_data, file_type):
    try:
        api_key = APIS['google']['key']
        if 'YOUR_' in api_key:
            return None  # Key not set
        
        url = f"{APIS['google']['url']}?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'contents': [
                {
                    'parts': [
                        {'text': f"You are VillainAI. {message}"}
                    ]
                }
            ],
            'generationConfig': {
                'maxOutputTokens': 300,
                'temperature': 0.7
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text'].replace('**', '').replace('*', '')
        return None
    except Exception as e:
        print(f"Google API Error: {str(e)}")
        return None

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
