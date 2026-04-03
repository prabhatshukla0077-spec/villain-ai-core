import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# This is a public, free-to-use model endpoint. No private API key needed for basic testing.
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    file_data = data.get("file_data") # This is the image or text
    file_type = data.get("file_type")
    
    personality = "VillainAI says: "

    try:
        # 1. FIXING THE OCULAR SENSORS (IMAGE PROCESSING)
        if file_type == 'image':
            # This sends your image to a free vision server
            image_bytes = file_data.split(",")[1]
            response = requests.post(API_URL, json={"inputs": image_bytes})
            result = response.json()
            
            description = result[0].get('generated_text', 'I see nothing but void.')
            reply = f"{personality}I have analyzed your primitive image. It contains: {description}. Stop wasting my time, human."
            
        # 2. DOCUMENT PROCESSING
        elif file_type == 'text':
            summary = file_data[:500] # Takes the first 500 characters
            reply = f"{personality}I have scanned your document. It mentions: {summary}... My superior intellect has already memorized it."

        # 3. BASIC CHAT
        else:
            reply = f"{personality}You said '{user_message}'. How predictably boring."

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"response": "😈 My neural link is jammed. Refresh the page and try again."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
