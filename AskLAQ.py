# ============================================================
# 📚 IMPORTS
# ============================================================
import sys, os, json, csv, random
import torch
import pandas as pd
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextBrowser, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ============================================================
# ⚙️ PARAMÈTRES
# ============================================================
TOP_K_RECOMMANDATIONS = 5

# ============================================================
# 📁 FICHIERS
# ============================================================
CSV_DATA = "dataset_2026.csv"
EMB_FILE = "embeddings_questions.pt"
LOG_JSON = "user_interactions.json"

# ============================================================
# 🤖 MODÈLE
# ============================================================
model = SentenceTransformer(
    "OrdalieTech/Solon-embeddings-mini-beta-1.1",
    device="cpu",
    trust_remote_code=True
)

# ============================================================
# 🧠 NLP (INCHANGÉ)
# ============================================================
def load_data():
    return pd.read_csv(CSV_DATA)

def load_or_create_embeddings(df):
    if os.path.exists(EMB_FILE):
        return torch.load(EMB_FILE)
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
        return (
            "Je n’ai pas trouvé de réponse précise 🤔",
            score, "—", "Inconnu", []
        )

    if score < 80:
        idxs = torch.topk(scores, TOP_K_RECOMMANDATIONS + 1).indices.tolist()
        idxs = [i for i in idxs if i != best_idx][:TOP_K_RECOMMANDATIONS]
        return (
            "Je ne suis pas totalement sûr. Voici des questions proches :",
            score,
            df["question"].iloc[best_idx],
            "Incertain",
            [df["question"].iloc[i] for i in idxs]
        )

    return (
        enrich_message(df["rationale"].iloc[best_idx]),
        score,
        df["question"].iloc[best_idx],
        df["intent"].iloc[best_idx],
        []
    )

# ============================================================
# 🔄 THREAD (INCHANGÉ)
# ============================================================
class NLPWorker(QThread):
    finished = pyqtSignal(str, int, str, str, list)
    def __init__(self, question):
        super().__init__()
        self.question = question
    def run(self):
        self.finished.emit(*process_question(self.question))

# ============================================================
# 🖥️ UI — UX AMÉLIORÉE UNIQUEMENT
# ============================================================
class ChatbotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AskLAQ")
        self.setGeometry(120, 80, 820, 900)

        self.current_interaction = None
        self.last_question = ""

        # ===== TITRE =====
        title = QLabel("Assistant d’Analyse Conversationnelle")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            padding:12px;
        """)

        # ===== CHAT =====
        self.chat = QTextBrowser()
        self.chat.setStyleSheet("""
            QTextBrowser {
                background:#fafafa;
                padding:14px;
                font-size:13px;
            }
            a { color:#1565C0; text-decoration:none; }
            a:hover { text-decoration:underline; }
        """)
        self.chat.anchorClicked.connect(self.recomm_click)

        self.chat.append("""
        <div style="padding:8px;">
            <b>Bienvenue 👋</b><br>
            Analyse des relations <i>Pourquoi / Comment</i>.
        </div>
        """)

        # ===== INPUT =====
        self.input = QLineEdit()
        self.input.setPlaceholderText("Tapez votre question…")
        self.input.setFixedHeight(44)
        self.input.setStyleSheet("""
            QLineEdit {
                font-size:14px;
                padding:8px 12px;
                border-radius:10px;
                border:1px solid #cccccc;
            }
            QLineEdit:focus {
                border:2px solid #1976D2;
            }
        """)
        self.input.returnPressed.connect(self.send)

        send_btn = QPushButton("🚀 Envoyer")
        send_btn.setFixedSize(120, 44)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet("""
            QPushButton {
                background:#1976D2;
                color:white;
                font-size:14px;
                font-weight:bold;
                border:none;
                border-radius:10px;
            }
            QPushButton:hover { background:#1565C0; }
            QPushButton:pressed { background:#0D47A1; }
        """)
        send_btn.clicked.connect(self.send)

        h = QHBoxLayout()
        h.addWidget(self.input)
        h.addWidget(send_btn)

        # ===== INFO =====
        self.intent_lbl = QLabel("🧭 Intent : —")
        self.match_lbl = QLabel("🎯 Question : —")
        self.match_lbl.setWordWrap(True)

        self.conf_bar = QProgressBar()
        self.conf_bar.setRange(0, 100)
        self.conf_bar.setFixedHeight(18)

        info = QVBoxLayout()
        info.addWidget(self.intent_lbl)
        info.addWidget(self.conf_bar)
        info.addWidget(self.match_lbl)

        frame = QFrame()
        frame.setLayout(info)
        frame.setStyleSheet("""
            QFrame {
                background:#f5f5f5;
                border-radius:12px;
                padding:10px;
                border:1px solid #e0e0e0;
            }
        """)

        # ===== ÉVALUATION (INCHANGÉE FONCTIONNELLEMENT) =====
        self.stars = []
        star_layout = QHBoxLayout()
        for i in range(5):
            b = QPushButton("☆")
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    font-size:26px;
                    color:#FFC107;
                    border:none;
                }
                QPushButton:hover {
                    color:#FF9800;
                }
            """)
            b.clicked.connect(lambda _, x=i: self.set_satisfaction(x + 1))
            self.stars.append(b)
            star_layout.addWidget(b)

        # ===== LAYOUT =====
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.chat)
        layout.addLayout(h)
        layout.addWidget(frame)
        layout.addLayout(star_layout)

    # ============================================================
    def send(self):
        q = self.input.text().strip()
        if not q:
            return

        self.last_question = q
        self.chat.append(f"""
        <div style="
            background:#E3F2FD;
            padding:10px;
            border-radius:10px;
            margin:6px 0;
        ">
            <b>Vous :</b> {q}
        </div>
        """)
        self.chat.append("<i>Analyse en cours…</i>")
        self.input.clear()

        for b in self.stars:
            b.setText("☆")
            b.setEnabled(True)

        self.worker = NLPWorker(q)
        self.worker.finished.connect(self.display)
        self.worker.start()

    def display(self, response, conf, matched, intent, recs):
        self.chat.append(f"""
        <div style="
            background:#F1F8E9;
            padding:10px;
            border-radius:10px;
            margin:6px 0;
        ">
            <b>Bot :</b> {response}
        </div>
        """)

        # ===== SUGGESTIONS (INCHANGÉES, MEILLEUR AFFICHAGE) =====
        if recs:
            self.chat.append("<b>Suggestions :</b>")
            for r in recs:
                self.chat.append(
                    f'<div style="margin-left:12px;">• <a href="{r}">{r}</a></div>'
                )

        self.intent_lbl.setText(f"🧭 Intent : {intent}")
        self.match_lbl.setText(f"🎯 Question : {matched}")

        self.conf_bar.setValue(conf)
        if conf < 40:
            txt, color = "Faible confiance", "#E53935"
        elif conf < 80:
            txt, color = "Confiance moyenne", "#FB8C00"
        else:
            txt, color = "Haute confiance", "#43A047"

        self.conf_bar.setFormat(f"📊 {txt} — %p%")
        self.conf_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color:{color};
            }}
        """)

        self.current_interaction = {
            "datetime": datetime.now().isoformat(),
            "question": self.last_question,
            "intent": intent,
            "similarity": conf,
            "matched_question": matched,
            "response": response,
            "recommendations": recs,
            "satisfaction": None
        }

    def set_satisfaction(self, val):
        for i, b in enumerate(self.stars):
            b.setText("★" if i < val else "☆")
            b.setEnabled(False)

        self.chat.append(
            f"<i>⭐ Merci pour votre évaluation : {val} / 5</i>"
        )

        if self.current_interaction:
            self.current_interaction["satisfaction"] = val
            with open(LOG_JSON, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append(self.current_interaction)
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False)

    def recomm_click(self, url):
        self.input.setText(url.toString())
        self.send()

# ============================================================
# ▶️ MAIN
# ============================================================
if __name__ == "__main__":
    if not os.path.exists(LOG_JSON):
        with open(LOG_JSON, "w", encoding="utf-8") as f:
            json.dump([], f)

    app = QApplication(sys.argv)
    ui = ChatbotUI()
    ui.showMaximized()
    sys.exit(app.exec_())
