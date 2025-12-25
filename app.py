import os, json, random
from datetime import datetime
import torch
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer, util

# --- AJOUTS POUR LA PRODUCTION ET SPYDER ---
import gradio as gr
import uvicorn
import nest_asyncio
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

CSV_DATA = "dataset_2026.csv"
EMB_FILE = "embeddings_questions.pt"
TOP_K_RECOMMANDATIONS = 5

# Chargement du modèle
model = SentenceTransformer(
    "OrdalieTech/Solon-embeddings-mini-beta-1.1",
    device="cpu",
    trust_remote_code=True
)

def load_data():
    return pd.read_csv(CSV_DATA)

def load_or_create_embeddings(df):
    if os.path.exists(EMB_FILE):
        return torch.load(EMB_FILE, map_location="cpu")
    emb = model.encode(
        df["question"].astype(str).tolist(),
        convert_to_tensor=True,
        normalize_embeddings=True
    )
    torch.save(emb, EMB_FILE)
    return emb

def enrich_message(base):
    return random.choice([
        f"Bonne question 🙂 {base}",
        f"Voici ce que je peux vous dire : {base}",
        f"Intéressant ! {base}",
        base
    ])

def process_question(question):
    df = load_data()
    emb_base = load_or_create_embeddings(df)
    emb_q = model.encode(question, convert_to_tensor=True, normalize_embeddings=True)
    scores = util.pytorch_cos_sim(emb_q, emb_base)[0]

    best_idx = torch.argmax(scores).item()
    score = int(scores[best_idx].item() * 100)

    if score < 40:
        return {"response":"Aucune réponse trouvée","confidence":score,"matched":"—","intent":"Inconnu","recs":[]}

    if score < 80:
        idxs = torch.topk(scores, TOP_K_RECOMMANDATIONS + 1).indices.tolist()
        idxs = [i for i in idxs if i != best_idx][:TOP_K_RECOMMANDATIONS]
        return {
            "response":"Je ne suis pas totalement sûr.",
            "confidence":score,
            "matched":df["question"].iloc[best_idx],
            "intent":"Incertain",
            "recs":[df["question"].iloc[i] for i in idxs]
        }

    return {
        "response":enrich_message(df["rationale"].iloc[best_idx]),
        "confidence":score,
        "matched":df["question"].iloc[best_idx],
        "intent":df["intent"].iloc[best_idx],
        "recs":[]
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    return jsonify(process_question(request.json["question"]))

# --- CONFIGURATION DE PRODUCTION (Indispensable pour Hugging Face) ---
fastapi_app = FastAPI()
fastapi_app.mount("/", WSGIMiddleware(app))

if __name__ == "__main__":
    # 1. On permet à Uvicorn de tourner dans Spyder/Jupyter
    nest_asyncio.apply()
    
    # 2. On lance le serveur sur le port 7860 (obligatoire HF)
    print("🚀 Lancement du serveur de production sur http://localhost:7860")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=7860)