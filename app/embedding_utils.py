import numpy as np
from numpy.linalg import norm

def get_sentence_embedding(sentence, model):
    words = sentence.split()
    embeddings = [model[word] for word in words if word in model]
    return np.mean(embeddings, axis=0) if embeddings else np.zeros(100)

def cos_sim(A, B):
    return np.dot(A,B)/(norm(A)*norm(B))