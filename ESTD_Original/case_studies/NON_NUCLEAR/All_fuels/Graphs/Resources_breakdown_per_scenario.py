
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 📁 Chemin vers ton dossier de scénarios
root = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/All_fuels")

# 📂 Liste des scénarios à traiter
scenarios = [f"all_fuels_RE_gwp_{i/1000:.3f}" for i in range(0, 63, 1)]

# 📊 Stockage des données
data = {}
costs = {}  # 💰 Pour stocker les coûts totaux depuis log.txt

for scenario in scenarios:
    # 🔎 Lecture des ressources
    fn_res = root / scenario / "output" / "resources_breakdown.txt"
    fn_log = root / scenario / "output" / "log.txt"

    if fn_res.exists():
        df = pd.read_csv(fn_res, sep="\t", engine="python", comment="#")
        df.columns = df.columns.str.strip()
        df["Name"] = df["Name"].str.strip()
        df = df[["Name", "Used"]]
        df = df[df["Used"] > 0]
        df = df.set_index("Name")
        data[scenario] = df["Used"]
    else:
        print(f"[⚠] Fichier ressources introuvable pour : {scenario}")

    # 💰 Lecture du coût total depuis log.txt
    if fn_log.exists():
        with open(fn_log, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("TotalCost"):
                    try:
                        costs[scenario] = float(line.strip().split()[1])
                    except (IndexError, ValueError):
                        print(f"[⚠] Problème de lecture du coût dans : {scenario}")
                    break
    else:
        print(f"[⚠] Fichier log.txt introuvable pour : {scenario}")

# 📐 Fusion des données
combined_df = pd.DataFrame(data).fillna(0).T

# 🔍 Détection des ressources à faible variation (< 3 %) ou très faible utilisation (< 0.1 GWh)
max_usage = combined_df.max()
min_usage = combined_df.min()
variation_pct = ((max_usage - min_usage) / max_usage.replace(0, 1e-9)) * 100
low_var_or_low_usage = variation_pct[variation_pct < 3].index.union(max_usage[max_usage < 0.1].index)

# ✅ Forcer l'affichage de METHANOL_RE
if "METHANOL_RE" in low_var_or_low_usage:
    low_var_or_low_usage = low_var_or_low_usage.drop("METHANOL_RE")

# 🔀 Séparation des données
stable_df = combined_df[low_var_or_low_usage].sum(axis=1).rename("Autres (stables)")
variable_df = combined_df.drop(columns=low_var_or_low_usage)

# 🧩 Assemblage final
final_df = pd.concat([stable_df, variable_df], axis=1)
final_df = final_df[["Autres (stables)"] + variable_df.columns.tolist()]

# 📈 Graphique empilé
fig, ax1 = plt.subplots(figsize=(14, 8))
final_df.plot(kind="bar", stacked=True, width=0.8, ax=ax1)

# 🧼 Légende principale (pour les ressources)
handles, labels = ax1.get_legend_handles_labels()
handles_cleaned = handles[1:]  # Retirer "Autres (stables)"
labels_cleaned = labels[1:]
ax1.legend(handles_cleaned, labels_cleaned, title="Ressources", bbox_to_anchor=(1.02, 1), loc="upper left")

# 🎯 Ajouter 3e axe pour le coût total
ax3 = ax1.twinx()
scenarios_list = final_df.index.tolist()
cost_values = [costs.get(scenario, None) for scenario in scenarios_list]
ax3.plot(range(len(scenarios_list)), cost_values, color="black", marker="o", label="TotalCost (€)")

# 📌 Mise en forme
ax1.set_title("Utilisation des ressources par scénario (gwp_op) avec coût total", fontsize=14)
ax1.set_xlabel("Scénarios", fontsize=12)
ax1.set_ylabel("Utilisation des ressources [GWh/an]", fontsize=12)
ax3.set_ylabel("Coût total [€]", fontsize=12, color="black")
ax3.tick_params(axis="y", labelcolor="black")
plt.xticks(ticks=range(len(scenarios_list)), labels=scenarios_list, rotation=45)
plt.tight_layout()

# 🧾 Légende pour le coût
lines, labels = ax3.get_legend_handles_labels()
ax3.legend(lines, labels, loc="upper right")

# 💾 Sauvegarde possible
# plt.savefig(root / "stacked_resources_plus_costs.png", dpi=300)

plt.show()
