#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def main():
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

    # 3b) Conversion de 'f' en float (Infinity → np.inf)
    df['f'] = df['f'].replace('Infinity', np.inf)
    df['f'] = pd.to_numeric(df['f'], errors='coerce')

    # 4) Vérification
    if "f" not in df.columns:
        print("Colonnes disponibles :", df.columns.tolist())
        raise KeyError("La colonne 'f' est introuvable après conversion.")

    # 5) Technologies ciblées
    techs = [
      "NUCLEAR","CCGT","CCGT_AMMONIA","COAL_US","COAL_IGCC","PV",
      "WIND_ONSHORE","WIND_OFFSHORE","HYDRO_RIVER","GEOTHERMAL",
      "IND_COGEN_GAS","IND_COGEN_WOOD","IND_COGEN_WASTE",
      "DHN_COGEN_GAS","DHN_COGEN_WOOD","DHN_COGEN_WASTE",
      "DHN_COGEN_WET_BIOMASS","DHN_COGEN_BIO_HYDROLYSIS",
      "DEC_COGEN_GAS","DEC_COGEN_OIL","DEC_ADVCOGEN_GAS","DEC_ADVCOGEN_H2",
      "BIO_HYDROLYSIS","PYROLYSIS_TO_LFO","PYROLYSIS_TO_FUELS","BIOMASS_TO_METHANOL"
    ]

    # 6) Filtrer et trier numériquement
    sub = df[df["TECHNOLOGIES"].isin(techs)].copy()

    # 6b) Exclure les techno dont f est strictement égal à 0
    sub = sub[sub["f"] != 0]
    sub = sub[sub["f"] >= 0.001]


    # Vérifier les techno manquantes dans le fichier source
    present = set(df[df["TECHNOLOGIES"].isin(techs)]["TECHNOLOGIES"])
    missing = set(techs) - present
    if missing:
        print("⚠️ Technologies manquantes dans le fichier :", missing)

    # 6c) Trier par f croissant
    sub = sub.sort_values(by="f", ascending=True)

    # 7) Tracer
    plt.figure(figsize=(12,6))
    plt.bar(sub["TECHNOLOGIES"], sub["f"], color="teal")
    plt.xticks(rotation=90)
    plt.xlabel("Technologie")
    plt.ylabel("Capacité installée F [GW ou GWh]")
    plt.title("Capacités installées (F) par technologie — tri numérique croissant")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    # 8) Sauvegarder et afficher
    out = Path("capacites_installees_sorted.png")
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"[OK] Graphique sauvegardé sous {out}")

if __name__ == "__main__":
    main()
