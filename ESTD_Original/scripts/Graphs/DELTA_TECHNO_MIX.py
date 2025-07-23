#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Nom du scénario à comparer (dossier sous case_studies)
SCENARIO = "Methanol_RE_0.3"  # remplacez par le nom exact du dossier de votre scénario


def load_assets(scenario: str) -> pd.DataFrame:
    """
    Charge le fichier assets.txt pour un scénario donné et renvoie
    un DataFrame avec les colonnes ['TECHNOLOGIES', 'f'] (float).
    """
    root = Path(__file__).resolve().parent.parent.parent
    fn = root / "case_studies" / scenario / "output" / "assets.txt"
    if not fn.exists():
        print(f"[Erreur] fichier introuvable pour scénario '{scenario}': {fn}")
        sys.exit(1)

    df = pd.read_csv(fn, sep="\t", engine="python", comment="#")
    df.columns = df.columns.str.strip()
    # Conversion de 'f' en float
    df['f'] = df['f'].replace('Infinity', np.inf)
    df['f'] = pd.to_numeric(df['f'], errors='coerce')

    if 'TECHNOLOGIES' not in df.columns or 'f' not in df.columns:
        print(f"Colonnes disponibles dans {fn} :", df.columns.tolist())
        raise KeyError("Colonnes 'TECHNOLOGIES' et/ou 'f' introuvables.")

    return df[['TECHNOLOGIES', 'f']].dropna()


def main():
    # Chemin racine du projet
    root = Path(__file__).resolve().parent.parent.parent

    # Charger les données des deux scénarios
    df_ref = load_assets("Belgium_2050_base").rename(columns={'f': 'f_ref'})
    df_scn = load_assets(SCENARIO).rename(columns={'f': 'f_scenario'})

    # Fusionner tous les techs des deux scénarios
    df_cmp = pd.merge(
        df_ref,
        df_scn,
        on='TECHNOLOGIES',
        how='outer'
    ).fillna(0)

    # Calcul de la différence absolue (GW)
    df_cmp['diff_gw'] = df_cmp['f_scenario'] - df_cmp['f_ref']

    # Calcul du delta en pourcentage
    def compute_delta(ref, scn):
        if ref == 0:
            return np.nan
        return (scn - ref) / ref * 100

    df_cmp['delta_pct'] = df_cmp.apply(
        lambda row: compute_delta(row['f_ref'], row['f_scenario']), axis=1
    )

    # Formatage pour affichage
    df_cmp['delta_str'] = df_cmp['delta_pct'].apply(
        lambda x: f"{x:+.1f}%" if pd.notnull(x) else 'NA'
    )
    df_cmp['diff_str'] = df_cmp['diff_gw'].apply(
        lambda x: f"{x:+.2f}"  # format en GW, signe inclus
    )

    # Préparer le tableau final
    df_out = df_cmp[
        ['TECHNOLOGIES', 'f_ref', 'f_scenario', 'diff_str', 'delta_str']
    ].rename(columns={
        'TECHNOLOGIES': 'Techno',
        'f_ref': "Réf [GW]",
        'f_scenario': f"{SCENARIO} [GW]",
        'diff_str': 'Différence [GW]',
        'delta_str': 'Δ [%]'
    })

    # Afficher le résultat
    print(df_out.to_string(index=False))

    # Enregistrer le tableau en CSV dans le dossier du scénario
    out_csv = root / "case_studies" / SCENARIO / "output" / f"{SCENARIO}_comparative_tab.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"[OK] Tableau enregistré sous {out_csv}")


if __name__ == "__main__":
    main()
