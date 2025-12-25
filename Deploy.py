import os, ssl
from huggingface_hub import HfApi, create_repo

# --- PATCH SSL ---
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# --- CONFIGURATION ---
TOKEN = "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" # Allez sur hf.co/settings/tokens (Rôle: WRITE)
USER = "OUAREDAEK"
SPACE_NAME = "AskLAQ3"
REPO_ID = f"{USER}/{SPACE_NAME}"

def deploy():
    api = HfApi(token=TOKEN)
    print(f"🚀 Création du Space {REPO_ID}...")
    create_repo(repo_id=REPO_ID, repo_type="space", space_sdk="gradio", exist_ok=True, token=TOKEN)

    print("📤 Envoi des fichiers en cours...")
    # Liste spécifique des fichiers à envoyer
    files_to_upload = [
        "app.py", "requirements.txt", "dataset_2026.csv", "embeddings_questions.pt"
    ]
    
    # Envoi des fichiers racines
    for file in files_to_upload:
        if os.path.exists(file):
            api.upload_file(path_or_fileobj=file, path_in_repo=file, repo_id=REPO_ID, repo_type="space")
    
    # Envoi des dossiers templates et static
    for folder in ["templates", "static"]:
        if os.path.exists(folder):
            api.upload_folder(folder_path=folder, path_in_repo=folder, repo_id=REPO_ID, repo_type="space")

    print("\n" + "="*50)
    print(f"✅ TERMINÉ ! Accès : https://{USER.lower()}-{SPACE_NAME.lower()}.hf.space")
    print("="*50)

if __name__ == "__main__":
    deploy()