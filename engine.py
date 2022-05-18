import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('distilbert-base-nli-mean-tokens')

def get_recommendations(base, candidates):
  print("started")
  base_text = base[1]
  candidates_ids = candidates[:,0]
  candidates_text = candidates[:,1]
  base_emb = np.array(model.encode(base_text, show_progress_bar=True))
  candidates_emb = np.array(model.encode(candidates_text, show_progress_bar=True))
  cs = cosine_similarity(base_emb.reshape(1, -1), candidates_emb)
  recommendations = sorted(zip(cs[0], candidates_ids), reverse=True)
  return np.array(recommendations)
