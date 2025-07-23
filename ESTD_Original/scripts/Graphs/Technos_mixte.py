#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Importer la liste des technologies depuis le fichier externe
from Liste_techno_conversion import technos

def main():
    threshold = 0.001  # seuil pour le paramètre f

    # 1) Racine du projet
    root = Path(__file__).resolve().parent.parent.parent

    # 2) Chemin vers assets.txt
    fn = root / "case_studies" / "Belgium_2050_base" / "output" / "assets.txt"
    if not fn.exists():
        print(f"[Erreur] fichier introuvable : {fn}")
        sys.exit(1)

    # 3) Lecture et nettoyage
    df = pd.read_csv(fn, sep="\t", engine="python", comment="#")
    df.columns = df.columns.str.strip()

    # 4) Conversion de 'f' en float (Infinity → np.inf)
    df['f'] = df['f'].replace('Infinity', np.inf)
    df['f'] = pd.to_numeric(df['f'], errors='coerce')

    # 5) Vérification de la présence de la colonne 'f'
    if 'f' not in df.columns:
        print("Colonnes disponibles :", df.columns.tolist())
        raise KeyError("La colonne 'f' est introuvable après conversion.")

    # 6) Ne conserver que les technologies listées
    df = df[df['TECHNOLOGIES'].isin(technos)].copy()

    # 7) Filtrer les technos dont f > threshold
    df_pos = df[df['f'] > threshold].copy()

    # 8) Liste des technos retenues
    techs_over_threshold = df_pos['TECHNOLOGIES'].dropna().unique().tolist()
    print(f"Technologies avec f > {threshold} :")
    for tech in sorted(techs_over_threshold):
        print(f" - {tech}")

    # 9) Trier par f croissant pour le graphe
    df_plot = df_pos.sort_values(by='f', ascending=True)

    # 10) Tracer
    plt.figure(figsize=(12,6))
    plt.bar(df_plot['TECHNOLOGIES'], df_plot['f'], color='teal')
    plt.xticks(rotation=90)
    plt.xlabel('Technologie')
    plt.ylabel('Paramètre f')
    plt.title(f'Paramètre f par technologie (f > {threshold}), tri croissant')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 11) Sauvegarder et afficher
    out = Path("capacites_f_threshold_plot.png")
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"[OK] Graphique sauvegardé sous {out}")

if __name__ == "__main__":
    main()