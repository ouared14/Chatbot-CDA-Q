# ============================================================
# 📚 IMPORTS
# ============================================================
import sys
import os
import pandas as pd

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QGroupBox
)
from PyQt5.QtCore import Qt

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
# 🖥️ UI ANALYTICS
# ============================================================
class AnalyticsUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AskLAQ – Tableau de Bord Analytique")
        self.setGeometry(150, 100, 950, 720)

        self.df = load_data()

        main_layout = QVBoxLayout(self)

        # ---------------- Titre ----------------
        title = QLabel("📊 Tableau de Bord – Analyse des Interactions")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        main_layout.addWidget(title)

        # ---------------- KPIs ----------------
        kpi_box = QGroupBox("Indicateurs Clés")
        kpi_layout = QHBoxLayout()

        self.kpi_total = QLabel()
        self.kpi_conf = QLabel()
        self.kpi_sat = QLabel()
        self.kpi_intents = QLabel()

        for lbl in [self.kpi_total, self.kpi_conf, self.kpi_sat, self.kpi_intents]:
            lbl.setStyleSheet("font-size:14px;")
            kpi_layout.addWidget(lbl)

        kpi_box.setLayout(kpi_layout)
        main_layout.addWidget(kpi_box)

        # ---------------- Table ----------------
        table_box = QGroupBox("Historique des Interactions")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        table_layout.addWidget(self.table)

        table_box.setLayout(table_layout)
        main_layout.addWidget(table_box)

        # ---------------- Init ----------------
        self.refresh()

    def refresh(self):
        if self.df.empty:
            self.kpi_total.setText("❌ Aucune donnée disponible")
            return

        # -------- Sécurisation colonnes numériques --------
        if "similarity" in self.df.columns:
            self.df["similarity"] = pd.to_numeric(
                self.df["similarity"], errors="coerce"
            )

        if "satisfaction" in self.df.columns:
            self.df["satisfaction"] = pd.to_numeric(
                self.df["satisfaction"], errors="coerce"
            )

        # -------- KPIs --------
        self.kpi_total.setText(f"🗨️ Interactions : {len(self.df)}")

        conf_mean = self.df["similarity"].dropna().mean()
        sat_mean = self.df["satisfaction"].dropna().mean()

        self.kpi_conf.setText(
            f"📊 Confiance moy. : {conf_mean:.1f}%"
            if not pd.isna(conf_mean) else "📊 Confiance moy. : —"
        )

        self.kpi_sat.setText(
            f"⭐ Satisfaction moy. : {sat_mean:.1f}/5"
            if not pd.isna(sat_mean) else "⭐ Satisfaction moy. : —"
        )

        if "intent" in self.df.columns:
            self.kpi_intents.setText(
                f"🧭 Intents distincts : {self.df['intent'].nunique()}"
            )
        else:
            self.kpi_intents.setText("🧭 Intents distincts : —")

        # -------- Table --------
        columns = ["datetime", "question", "intent", "similarity", "satisfaction"]

        self.table.setRowCount(len(self.df))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        for row_idx, (_, row) in enumerate(self.df.iterrows()):
            for col_idx, col_name in enumerate(columns):
                value = row.get(col_name, "")
                self.table.setItem(
                    row_idx, col_idx, QTableWidgetItem(str(value))
                )

        self.table.resizeColumnsToContents()

# ============================================================
# ▶️ MAIN
# ============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = AnalyticsUI()
    ui.show()
    sys.exit(app.exec_())
