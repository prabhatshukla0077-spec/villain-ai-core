import os
from flask import Flask, render_template, request, jsonify
from gpt4all import GPT4All

app = Flask(__name__, template_folder='templates')

print("=========================================")
print("🧠 INITIATING LOCAL OFFLINE NEURAL NET...")
print("=========================================")
# This loads a highly compressed, fast AI model directly into your computer's RAM.
# The first boot will download a ~3GB file. Afterwards, it runs entirely offline.
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
print("✅ LOCAL AI LOADED AND READY.")

@app.route('/')
def home():
    # This connects to the exact same Gen-Z futuristic index.html we built earlier
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "System requires input to process."})

    try:
        # The AI generates the response using your actual computer processor
        system_prompt = "You are Villain AI, an advanced local intelligence. Answer concisely.\n\nUser: "
        full_prompt = system_prompt + user_message
        
        # max_tokens limits how long the answer is so it doesn't freeze your computer
        response = model.generate(full_prompt, max_tokens=200)
        
        return jsonify({"response": response.replace('**', '').replace('*', '')})
    
    except Exception as e:
        print(f"Core System Error: {str(e)}")
        return jsonify({"response": "CRITICAL: Local neural net failed to process."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
