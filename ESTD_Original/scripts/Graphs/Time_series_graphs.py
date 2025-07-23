#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# 1) Trouver la racine du projet
root = Path(__file__).resolve().parent.parent.parent

# 2) Construire le chemin vers resources_breakdown.txt
csv_path = root / "Data" / "2050" / "Time_series.csv" 


# 1. Charger les données
df = pd.read_csv(csv_path, sep=';')

# 4) Renommer la première colonne si elle s'appelle "{PERIODS}"
first = df.columns[0]
if first != "PERIODS":
    df = df.rename(columns={first: "PERIODS"})


# 2. Créer un graphique par série temporelle
for col in df.columns:
    if col == 'PERIODS':
        continue
    plt.figure()
    plt.plot(df['PERIODS'], df[col])
    plt.title(col)
    plt.xlabel('Days')
    plt.ylabel(col)
    plt.tight_layout()
    # Enregistrer la figure (optionnel)
    safe_name = col.replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'pct')
    out_file = Path(f"{safe_name}.png")
    plt.savefig(out_file)
    plt.show()


