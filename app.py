import os
import g4f
from flask import Flask, render_template, request, jsonify

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "Analyze this data.")
    file_data = data.get("file_data")
    file_type = data.get("file_type")
    
    try:
        personality = (
            "You are VillainAI. Provide a highly accurate, completely correct answer. "
            "End with a short, arrogant villain insult. Limit: 3 sentences total."
        )
        messages = [{"role": "system", "content": personality}]

        # 1. Handle Text/Document Files
        if file_type == 'text':
            document_content = f"The user uploaded a document containing this text:\n{file_data[:3000]}\n\nUser's question: {user_message}"
            messages.append({"role": "user", "content": document_content})
            
        # 2. Handle Image Files (Computer Vision)
        elif file_type == 'image':
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": file_data}}
                ]
            })
            
        # 3. Handle Normal Text Chat
        else:
            messages.append({"role": "user", "content": user_message})

        # Process through G4F (Using gpt-4o as it supports vision)
        response = g4f.ChatCompletion.create(
            model="gpt-4o", 
            messages=messages,
            timeout=20
        )
        
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR]: {e}\n")
        return jsonify({"response": "😈 My ocular sensors failed to process your primitive data. Network is unstable."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
