import torch
import pandas as pd
from sentence_transformers import SentenceTransformer

CSV_DATA = "dataset_2026.csv"
EMB_FILE = "embeddings_questions.pt"

model = SentenceTransformer(
    "OrdalieTech/Solon-embeddings-mini-beta-1.1",
    device="cpu",
    trust_remote_code=True
)

print("📥 Chargement du dataset...")
df = pd.read_csv(CSV_DATA)

questions = df["question"].astype(str).tolist()

print("🧠 Calcul des embeddings...")
embeddings = model.encode(
    questions,
    convert_to_tensor=True,
    normalize_embeddings=True
)

print("💾 Sauvegarde dans embeddings_questions.pt")
torch.save(embeddings, EMB_FILE)

print("✅ Terminé :", embeddings.shape)
