import os
import g4f
from flask import Flask, render_template, request, jsonify

# Setup Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    
    try:
        # 1. Strict Rules for a CORRECT Answer
        personality = (
            "You are VillainAI. Provide a highly accurate, completely correct, "
            "and helpful answer. End with a short, arrogant villain insult. "
            "Limit: 3 sentences total."
        )
        
        # 2. Use G4F to automatically find a working, free AI provider
        response = g4f.ChatCompletion.create(
            model=g4f.models.default, # Auto-routes to a working model to prevent "Not Found" errors
            messages=[
                {"role": "system", "content": personality},
                {"role": "user", "content": user_message}
            ],
            timeout=15
        )
        
        return jsonify({"response": response})
        
    except Exception as e:
        # If it STILL fails, it will print the EXACT reason in your VS Code terminal
        print(f"\n[CRITICAL ERROR]: {e}\n")
        return jsonify({"response": "😈 My neural pathways are overloaded. Speak again."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)