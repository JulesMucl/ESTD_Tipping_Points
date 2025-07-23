

"""
Ce que fait ce script :
1. Trouve le fichier `resources_breakdown.txt` dans le répertoire de sortie du cas d'étude.
2. Charge les données du fichier.
3. Filtre les ressources pour ne garder que celles avec une consommation positive et exclut les émissions de CO2.
4. Calcule le pourcentage de consommation pour chaque ressource.
5. Trie les ressources par ordre décroissant de consommation.
6. Trace un graphique à barres verticales montrant la répartition de l'énergie consommée par ressource, avec des annotations pour chaque barre indiquant le pourcentage de consommation.

"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# 1) Trouver la racine du projet
root = Path(__file__).resolve().parent.parent.parent

# 2) Construire le chemin vers resources_breakdown.txt
fn = root / "case_studies" / "Belgium_2050_base" / "output" / "resources_breakdown.txt"

# 3) Vérifier l’existence du fichier
if not fn.exists():
    print(f"[ERROR] Fichier introuvable : {fn}", file=sys.stderr)
    sys.exit(1)

# 4) Charger le fichier
df = pd.read_csv(fn, sep='\t')

# 5) Filtrer : garder uniquement Used > 0 et fini, exclure CO2_EMISSIONS
df = df[np.isfinite(df['Used']) & (df['Used'] > 0.01)]
df = df[df['Name'] != 'CO2_EMISSIONS']

# 6) Calculer pourcentages
total = df['Used'].sum()
df['Pct'] = df['Used'] / total * 100

# 7) (Optionnel) Trier par ordre décroissant de consommation
df = df.sort_values(by='Used', ascending=False)

# 8) Préparer labels, tailles et pourcentages
labels      = df['Name'].tolist()
sizes       = df['Used'].tolist()
percentages = df['Pct'].tolist()

# 9) Tracer le graphe à barres verticales
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(labels, sizes)

# 10) Annoter chaque barre avec son pourcentage
for bar, pct in zip(bars, percentages):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + total * 0.005,
        f"{pct:.1f}%",
        ha='center',
        va='bottom'
    )

# 11) Mise en forme
ax.set_title("Répartition de l'énergie consommée par ressource (sans émissions)")
ax.set_ylabel("Énergie utilisée [mêmes unités que dans le fichier]")
ax.set_xticklabels(labels, rotation=45, ha='right')
plt.tight_layout()
plt.show()
