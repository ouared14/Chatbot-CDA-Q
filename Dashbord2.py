# ============================================================
# 📚 IMPORTS
# ============================================================
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ============================================================
# ⚙️ CONFIGURATION
# ============================================================
LOG_CSV = "user_interactions.csv"

# ============================================================
# 📂 DATA LOADING
# ============================================================
def load_data():
    if not os.path.exists(LOG_CSV):
        return pd.DataFrame()
    return pd.read_csv(LOG_CSV, encoding="utf-8")

# ============================================================
# 📊 CANVAS GRAPHIQUE
# ============================================================
class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 3))
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

# ============================================================
# 🖥️ UI ANALYTICS
# ============================================================
class AnalyticsUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AskLAQ – Tableau de Bord Analytique")
        self.setGeometry(120, 80, 1200, 820)

        self.df = load_data()

        main_layout = QVBoxLayout(self)

        # ---------------- Titre ----------------
        title = QLabel("📊 Tableau de Bord – Analyse des Interactions")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        main_layout.addWidget(title)

        # ---------------- KPIs ----------------
        self.init_kpis(main_layout)

        # ---------------- Graphiques ----------------
        graphs_box = QGroupBox("Analyses Visuelles")
        graphs_layout = QHBoxLayout()

        self.canvas_conf = MplCanvas()
        self.canvas_intent = MplCanvas()

        graphs_layout.addWidget(self.canvas_conf)
        graphs_layout.addWidget(self.canvas_intent)

        graphs_box.setLayout(graphs_layout)
        main_layout.addWidget(graphs_box)

        # ---------------- Graphiques bas ----------------
        graphs_box2 = QGroupBox("Analyses Avancées")
        graphs_layout2 = QHBoxLayout()

        self.canvas_time = MplCanvas()
        self.canvas_sat = MplCanvas()

        graphs_layout2.addWidget(self.canvas_time)
        graphs_layout2.addWidget(self.canvas_sat)

        graphs_box2.setLayout(graphs_layout2)
        main_layout.addWidget(graphs_box2)

        # ---------------- Table ----------------
        self.init_table(main_layout)

        self.refresh()

    # ========================================================
    # KPIs
    # ========================================================
    def init_kpis(self, layout):
        box = QGroupBox("Indicateurs Clés")
        lay = QHBoxLayout()

        self.kpi_total = QLabel()
        self.kpi_conf = QLabel()
        self.kpi_sat = QLabel()
        self.kpi_intents = QLabel()

        for lbl in [self.kpi_total, self.kpi_conf, self.kpi_sat, self.kpi_intents]:
            lbl.setStyleSheet("font-size:14px;")
            lay.addWidget(lbl)

        box.setLayout(lay)
        layout.addWidget(box)

    # ========================================================
    # Table
    # ========================================================
    def init_table(self, layout):
        box = QGroupBox("Historique des Interactions")
        lay = QVBoxLayout()

        self.table = QTableWidget()
        lay.addWidget(self.table)

        box.setLayout(lay)
        layout.addWidget(box)

    # ========================================================
    # Refresh
    # ========================================================
    def refresh(self):
        if self.df.empty:
            return

        # ---- Nettoyage ----
        for col in ["similarity", "satisfaction"]:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        if "datetime" in self.df.columns:
            self.df["datetime"] = pd.to_datetime(
                self.df["datetime"], errors="coerce"
            )

        # ---- KPIs ----
        self.kpi_total.setText(f"🗨️ Interactions : {len(self.df)}")

        conf = self.df["similarity"].dropna().mean()
        sat = self.df["satisfaction"].dropna().mean()

        self.kpi_conf.setText(
            f"📊 Confiance moy. : {conf:.1f}%" if not pd.isna(conf) else "📊 Confiance moy. : —"
        )
        self.kpi_sat.setText(
            f"⭐ Satisfaction moy. : {sat:.1f}/5" if not pd.isna(sat) else "⭐ Satisfaction moy. : —"
        )

        if "intent" in self.df.columns:
            self.kpi_intents.setText(
                f"🧭 Intents distincts : {self.df['intent'].nunique()}"
            )

        # ---- Table ----
        cols = ["datetime", "question", "intent", "similarity", "satisfaction"]
        self.table.setRowCount(len(self.df))
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)

        for r, (_, row) in enumerate(self.df.iterrows()):
            for c, col in enumerate(cols):
                self.table.setItem(r, c, QTableWidgetItem(str(row.get(col, ""))))

        self.table.resizeColumnsToContents()

        # ---- Graphiques ----
        self.plot_confidence()
        self.plot_intents()
        self.plot_timeline()
        self.plot_satisfaction_by_intent()

    # ========================================================
    # Graph 1 : Histogramme confiance
    # ========================================================
    def plot_confidence(self):
        self.canvas_conf.fig.clear()
        ax = self.canvas_conf.fig.add_subplot(111)

        data = self.df["similarity"].dropna()
        if not data.empty:
            ax.hist(data, bins=10)
            ax.set_title("Distribution de la Confiance (%)")
            ax.set_xlabel("Similarity")
            ax.set_ylabel("Fréquence")

        self.canvas_conf.draw()

    # ========================================================
    # Graph 2 : Intents
    # ========================================================
    def plot_intents(self):
        self.canvas_intent.fig.clear()
        ax = self.canvas_intent.fig.add_subplot(111)

        if "intent" in self.df.columns:
            top = self.df["intent"].value_counts().head(10)
            top.plot(kind="bar", ax=ax)
            ax.set_title("Top 10 des Intents")
            ax.set_ylabel("Occurrences")

        self.canvas_intent.draw()

    # ========================================================
    # Graph 3 : Timeline
    # ========================================================
    def plot_timeline(self):
        self.canvas_time.fig.clear()
        ax = self.canvas_time.fig.add_subplot(111)

        if "datetime" in self.df.columns:
            temp = self.df.dropna(subset=["datetime"])
            if not temp.empty:
                temp.set_index("datetime").resample("D").size().plot(ax=ax)
                ax.set_title("Évolution Temporelle des Interactions")
                ax.set_ylabel("Nombre")

        self.canvas_time.draw()

    # ========================================================
    # Graph 4 : Satisfaction par intent
    # ========================================================
    def plot_satisfaction_by_intent(self):
        self.canvas_sat.fig.clear()
        ax = self.canvas_sat.fig.add_subplot(111)

        if {"intent", "satisfaction"}.issubset(self.df.columns):
            data = self.df.dropna(subset=["satisfaction"])
            if not data.empty:
                data.groupby("intent")["satisfaction"].mean().sort_values(
                    ascending=False
                ).head(10).plot(kind="bar", ax=ax)
                ax.set_title("Satisfaction Moyenne par Intent")
                ax.set_ylabel("Note /5")

        self.canvas_sat.draw()

# ============================================================
# ▶️ MAIN
# ============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = AnalyticsUI()
    ui.show()
    sys.exit(app.exec_())
