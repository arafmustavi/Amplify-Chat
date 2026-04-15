from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)

# --- Model setup ---
model_name = "Rta-AILabs/Nandi-Mini-150M-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

print("--- Loading AMPLIFY Model ---")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16
).to(device).eval()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_prompt = data.get("prompt", "")

    messages = [{"role": "user", "content": user_prompt}]
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=500,
            do_sample=True,
            temperature=0.3,
            top_p=0.9
        )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
    ]
    response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return jsonify({"response": response_text.strip()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)