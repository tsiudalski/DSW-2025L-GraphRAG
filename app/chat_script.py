import requests
import json
import numpy as np
import os
from dotenv import load_dotenv
from embedding_utils import cos_sim

load_dotenv()

def format_messages(messages):
    """Formats the message history into a structured conversation string."""
    return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in messages)

def stream_response(prompt):
    with requests.post(
        f"http://{os.getenv('OLLAMA_HOST')}:{os.getenv('OLLAMA_PORT')}/api/generate",
        json={
            "model": f"{os.getenv('OLLAMA_MODEL')}",
            "prompt": prompt,
            "stream": True
        },
        stream=True
    ) as r:
        for line in r.iter_lines():
            if line:
                yield json.loads(line.decode())["response"]

if __name__ == "__main__":
    messages = []
    
    with open('question_template.json', 'r') as file:
        pairs = json.load(file)

    while True:
        user_input = input(">>> ")
        if user_input.lower() == "end":
            break

        embedding = requests.post(
            f"http://{os.getenv('OLLAMA_HOST')}:{os.getenv('OLLAMA_PORT')}/api/embed",
            json={
                "model": "all-minilm",
                "input": user_input
            }
        ).json()

        embedding = np.array(embedding['embeddings'][0])
        embedding = embedding / np.linalg.norm(embedding)
        print("Searching for best template... ", end="", flush=True)

        ## Pad the paiirs from 100 to 384 dimensions
        # Assuming pairs are already in the correct format, we pad them to 384 dimensions
        pairs = {k: np.pad(np.array(v), (0, 384 - len(v)), 'constant') for k, v in pairs.items()}
        best_sim = np.argmax([cos_sim(embedding, emb) for emb in list(pairs.values())])
        print(f"Best match: {list(pairs.keys())[best_sim]}")
        print(f"Similarity score: {cos_sim(embedding, list(pairs.values())[best_sim])}")

        best_template = os.path.join("templates", f"{list(pairs.keys())[best_sim]}.rq.j2")

        with open(best_template, 'r') as template_file:
            template = template_file.read()

        safe_template = template.replace('{', '{{').replace('}', '}}').replace('{{user_input}}', '{user_input}')
        user_input = safe_template.format(user_input=user_input)
        print("Using template:", user_input)

        messages.append({"role": "user", "content": user_input})
