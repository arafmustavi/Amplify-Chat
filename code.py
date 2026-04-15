from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "Rta-AILabs/Nandi-Mini-150M-Instruct"

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    dtype=torch.bfloat16
).to(device).eval()

i=0

while(i!=5):
    prompt = input("Ask me anything : ")

    messages = [
        {"role": "user", "content": prompt}
    ]

    prompt = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **inputs,
        max_new_tokens=500,
        do_sample=True,
        temperature=0.3,
        top_p=0.90,
        top_k=20,
        repetition_penalty=1.1,
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print(response)
    i-=1
