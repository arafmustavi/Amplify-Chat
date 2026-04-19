import os
import csv
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from llama_cpp import Llama  # <--- No Torch here!

app = Flask(__name__)

# --- Configuration ---
# Download the .gguf file to your folder and put the filename here
MODEL_PATH = "llama-3.2-1b-instruct-q4_k_m.gguf" 
LOG_FILE = "amplify_chat_history.csv"

# --- 1. Model Initialization ---
print("--- [AMPLIFY] Initializing Llama-CPP on CPU... ---")

# n_ctx is the memory for conversation history
# n_threads should be about half of your phone's CPU cores
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4,
    verbose=False
)

print("--- [AMPLIFY] System Ready! ---")

# --- 2. CSV Logging Helper ---
def log_interaction(prompt, response, latency):
    file_exists = os.path.isfile(LOG_FILE)
    fieldnames = ["timestamp", "prompt", "response", "latency_sec", "device"]
    
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt.replace('\n', ' '), 
            "response": response.replace('\n', ' '),
            "latency_sec": round(latency, 3),
            "device": "CPU (llama-cpp)"
        })

# --- 3. Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_prompt = data.get("prompt", "")

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    start_time = time.time()

    try:
        # Generate response
        output = llm(
            f"Q: {user_prompt} A: ", 
            max_tokens=500,
            stop=["Q:", "\n"],
            echo=False
        )
        
        response_text = output['choices'][0]['text'].strip()
        latency = time.time() - start_time
        
        log_interaction(user_prompt, response_text, latency)

        return jsonify({
            "status": "success",
            "response": response_text,
            "latency": round(latency, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
