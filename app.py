import os
import ollama
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "Analyze this.")
    file_data = data.get("file_data")
    file_type = data.get("file_type")
    
    personality = "You are VillainAI. Answer correctly. End with an arrogant insult. Limit to 3 sentences."
    
    try:
        # 1. PROCESS IMAGES (Using Local Llama Vision)
        if file_type == 'image':
            # Remove the HTML header from the image data
            clean_base64 = file_data.split(',')[1] 
            
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[{
                    'role': 'user',
                    'content': f"{personality}\n\nUser: {user_message}",
                    'images': [clean_base64]
                }]
            )
            
        # 2. PROCESS TEXT DOCUMENTS
        elif file_type == 'text':
            doc_prompt = f"{personality}\n\nDocument text:\n{file_data[:3000]}\n\nUser: {user_message}"
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[{'role': 'user', 'content': doc_prompt}]
            )
            
        # 3. NORMAL CHAT
        else:
            prompt = f"{personality}\n\nUser: {user_message}"
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[{'role': 'user', 'content': prompt}]
            )

        ai_reply = response['message']['content'].replace('**', '').replace('*', '')
        return jsonify({"response": ai_reply})
        
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"response": "😈 My local brain failed to boot. Is Ollama running on your machine?"})

if __name__ == '__main__':
    # Running strictly on your local machine
    app.run(host='127.0.0.1', port=5000, debug=True)
