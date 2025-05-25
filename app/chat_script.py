import requests
import json
import numpy as np
import os

from sklearn.metrics.pairwise import cosine_similarity
from embedding_utils import get_sentence_embedding, cos_sim
import gensim.downloader as api

def format_messages(messages):
    """Formats the message history into a structured conversation string."""
    return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in messages)

def stream_response(prompt):
    with requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
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
    word_vectors = api.load("glove-wiki-gigaword-100")
    with open('question_template.json', 'r') as file:
        pairs = json.load(file)

    while True:
        user_input = input(">>> ")
        if user_input.lower() == "end":
            break
        

        embedded_input = get_sentence_embedding(user_input, word_vectors)
        best_sim = np.argmax([cos_sim(embedded_input, emb) for emb in list(pairs.values())])
        best_template = os.path.join("templates", f"{list(pairs.keys())[best_sim]}.rq.j2")

        messages.append({"role": "user", "content": user_input})

        chat_context = format_messages(messages)
        response_chunks = []
        finished_thinking = False
        prev_chunk = None
        for chunk in stream_response(chat_context):
            if finished_thinking:
                print(chunk, end="", flush=True)
            if prev_chunk == "</think>":
                finished_thinking = True
            response_chunks.append(chunk)
            prev_chunk = chunk
        print("\n")

        messages.append({"role": "assistant", "content": "".join(response_chunks)})

        