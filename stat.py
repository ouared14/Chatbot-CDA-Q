# ============================================================
# 📊 ANALYSE AVANCÉE DES INTERACTIONS UTILISATEUR
# ============================================================

import json
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# ⚙️ PARAMÈTRES
# ============================================================
FICHIER_JSON = "user_interactions.json"

# ============================================================
# 📥 CHARGEMENT
# ============================================================
with open(FICHIER_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

print("\n📦 Nombre total d'interactions :", len(df))
print("📋 Colonnes détectées :", df.columns.tolist())

# ============================================================
# 🔁 NORMALISATION DES COLONNES
# ============================================================

# Similarité
if "similarity" not in df.columns and "confidence" in df.columns:
    df["similarity"] = df["confidence"]

# Question affichable
if "question" in df.columns:
    df["question_used"] = df["question"]
elif "matched_question" in df.columns:
    df["question_used"] = df["matched_question"]
else:
    df["question_used"] = "N/A"

# Satisfaction
if "satisfaction" not in df.columns:
    df["satisfaction"] = None

# Date
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

# ============================================================
# 🧭 1. RÉPARTITION PAR INTENT
# ============================================================
intent_counts = df["intent"].value_counts()

print("\n🧭 Répartition par intent :\n", intent_counts)

plt.figure()
intent_counts.plot(kind="bar", title="Répartition des intents")
plt.tight_layout()
plt.show()

# 🔵 PIE – INTENTS
plt.figure()
intent_counts.plot(
    kind="pie",
    autopct="%1.1f%%",
    title="Répartition des intents",
    ylabel=""
)
plt.tight_layout()
plt.show()

# ============================================================
# ⭐ 2. SATISFACTION
# ============================================================
sat_df = df.dropna(subset=["satisfaction"])

print("\n⭐ Nombre d'évaluations :", len(sat_df))

if not sat_df.empty:
    print("⭐ Satisfaction moyenne :", round(sat_df["satisfaction"].mean(), 2))
    print("\n⭐ Distribution :\n", sat_df["satisfaction"].value_counts().sort_index())

    sat_df["satisfaction"].value_counts().sort_index().plot(
        kind="bar",
        title="Distribution de la satisfaction"
    )
    plt.tight_layout()
    plt.show()

# ============================================================
# 🔴🟡🟢 3. ZONES DE SIMILARITÉ
# ============================================================
def zone(sim):
    if sim < 40:
        return "<40 (Faible)"
    elif sim < 80:
        return "40–80 (Moyenne)"
    else:
        return ">80 (Forte)"

df["similarity_zone"] = df["similarity"].apply(zone)

zone_counts = df["similarity_zone"].value_counts()

print("\n📊 Répartition par zone de similarité :\n", zone_counts)

# BAR
plt.figure()
zone_counts.plot(kind="bar", title="Zones de similarité")
plt.tight_layout()
plt.show()

# PIE
plt.figure()
zone_counts.plot(
    kind="pie",
    autopct="%1.1f%%",
    title="Répartition des zones de similarité",
    ylabel=""
)
plt.tight_layout()
plt.show()

# ============================================================
# 🔴 4. FAIBLE SIMILARITÉ (<40)
# ============================================================
low_conf = df[df["similarity"] < 40]

print("\n❌ Questions à faible similarité (<40%) :", len(low_conf))
print(low_conf[["question_used", "similarity"]].head(10))

# ============================================================
# 🟡 5. SIMILARITÉ MOYENNE (40–80)
# ============================================================
mid_conf = df[(df["similarity"] >= 40) & (df["similarity"] < 80)]

print("\n🟡 Cas moyens (40–80) :", len(mid_conf))
print("⭐ Satisfaction moyenne (40–80) :", round(mid_conf["satisfaction"].mean(), 2))

# ============================================================
# 🟢 6. HAUTE SIMILARITÉ (>80)
# ============================================================
high_conf = df[df["similarity"] >= 80]

print("\n🟢 Cas forts (>80) :", len(high_conf))
print("⭐ Satisfaction moyenne (>80) :", round(high_conf["satisfaction"].mean(), 2))

# ============================================================
# 💡 7. ANALYSE DES QUESTIONS RECOMMANDÉES
# ============================================================
reco_df = df[df["recommendations"].apply(lambda x: isinstance(x, list) and len(x) > 0)]

print("\n💡 Interactions avec recommandations :", len(reco_df))

# Explosion des recommandations
exploded_reco = reco_df.explode("recommendations")

top_reco = exploded_reco["recommendations"].value_counts().head(10)

print("\n🔝 Top 10 questions recommandées :\n", top_reco)

# BAR – questions recommandées
plt.figure(figsize=(8, 4))
top_reco.plot(kind="bar", title="Top questions recommandées")
plt.tight_layout()
plt.show()

# PIE – réponses directes vs recommandations
answer_types = pd.Series({
    "Réponse directe (>80)": len(high_conf),
    "Avec recommandations (<80)": len(df) - len(high_conf)
})

plt.figure()
answer_types.plot(
    kind="pie",
    autopct="%1.1f%%",
    title="Réponses directes vs recommandations",
    ylabel=""
)
plt.tight_layout()
plt.show()

# ============================================================
# 📈 8. ÉVOLUTION TEMPORELLE
# ============================================================
daily = df.groupby(df["datetime"].dt.date).agg({
    "similarity": "mean",
    "satisfaction": "mean"
})

print("\n📈 Évolution journalière :\n", daily)

daily.plot(marker="o", title="Évolution Similarité / Satisfaction")
plt.tight_layout()
plt.show()

# ============================================================
# 🧠 9. SATISFACTION PAR INTENT
# ============================================================
intent_sat = df.groupby("intent")["satisfaction"].mean().sort_values()

print("\n🧠 Satisfaction moyenne par intent :\n", intent_sat)

intent_sat.plot(kind="barh", title="Satisfaction moyenne par intent")
plt.tight_layout()
plt.show()

# ============================================================
# 📤 10. EXPORT FINAL
# ============================================================
df.to_csv("user_interactions_analysis.csv", index=False, encoding="utf-8")
print("\n📁 Export créé : user_interactions_analysis.csv")

print("\n✅ Analyse complète terminée avec succès.")
