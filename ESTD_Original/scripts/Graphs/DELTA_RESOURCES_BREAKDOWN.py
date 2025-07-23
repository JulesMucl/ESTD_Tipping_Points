#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Nom du scénario à comparer (dossier sous case_studies)
SCENARIO = "Methanol_RE_0.3"  # remplacez par le nom exact du dossier de votre scénario


def load_breakdown(scenario: str, used_col: str) -> pd.DataFrame:
    """
    Charge le fichier resources_breakdown.txt pour un scénario donné et renvoie
    un DataFrame avec les colonnes ['Name', used_col, 'Potential'].
    """
    root = Path(__file__).resolve().parent.parent.parent
    fn = root / "case_studies" / scenario / "output" / "resources_breakdown.txt"
    if not fn.exists():
        print(f"[Erreur] fichier introuvable pour scénario '{scenario}': {fn}")
        sys.exit(1)

    df = pd.read_csv(fn, sep="\t", engine="python", comment="#")
    df.columns = df.columns.str.strip()
    if 'Name' not in df.columns or 'Used' not in df.columns or 'Potential' not in df.columns:
        print(f"Colonnes disponibles dans {fn} :", df.columns.tolist())
        raise KeyError("Colonnes 'Name', 'Used' et/ou 'Potential' introuvables.")

    df = df[['Name', 'Used', 'Potential']].copy()
    df.rename(columns={'Used': used_col}, inplace=True)
    return df


def main():
    # Chemin racine du projet
    root = Path(__file__).resolve().parent.parent.parent

    # Charger les données des deux scénarios
    df_ref = load_breakdown("Belgium_2050_base", 'Used_ref')
    df_scn = load_breakdown(SCENARIO, 'Used_scenario')

    # Fusionner toutes les ressources
    df_cmp = pd.merge(
        df_ref,
        df_scn,
        on='Name',
        how='outer'
    )

    # Remplacer NaN par 0 pour Used
    df_cmp['Used_ref'] = df_cmp['Used_ref'].fillna(0)
    df_cmp['Used_scenario'] = df_cmp['Used_scenario'].fillna(0)

    # Combiner Potential
    df_cmp['Potential'] = df_cmp['Potential_x'].fillna(df_cmp['Potential_y'])
    df_cmp.drop(columns=[col for col in df_cmp.columns if col.startswith('Potential_')], inplace=True)

    # Calcul de la différence absolue
    df_cmp['diff'] = df_cmp['Used_scenario'] - df_cmp['Used_ref']

    # Calcul du delta en pourcentage
    def compute_delta(ref, scn):
        if ref == 0:
            return np.nan
        return (scn - ref) / ref * 100

    df_cmp['delta_pct'] = df_cmp.apply(
        lambda row: compute_delta(row['Used_ref'], row['Used_scenario']), axis=1
    )

    # Formatage des colonnes
    df_cmp['Différence [GW]'] = df_cmp['diff'].map(lambda x: f"{x:+.2f}")
    df_cmp['Δ [%]'] = df_cmp['delta_pct'].map(lambda x: f"{x:+.1f}%" if pd.notnull(x) else 'NA')

    # Préparer le tableau final
    df_out = df_cmp[
        ['Name', 'Used_ref', 'Used_scenario', 'Différence [GW]', 'Δ [%]', 'Potential']
    ].rename(columns={
        'Name': 'Ressource',
        'Used_ref': 'Utilisée Réf [GW]',
        'Used_scenario': f'Utilisée {SCENARIO} [GW]'
    })

    # Afficher le résultat
    print(df_out.to_string(index=False))

    # Calcul des totaux sur les colonnes Used
    total_ref = df_out['Utilisée Réf [GW]'].sum()
    total_scn = df_out[f'Utilisée {SCENARIO} [GW]'].sum()
    print(f"Somme Utilisée Réf [GW] : {total_ref:.2f}")
    print(f"Somme Utilisée {SCENARIO} [GW] : {total_scn:.2f}")

    # Enregistrer le tableau en CSV dans le dossier du scénario
    out_csv = root / "case_studies" / SCENARIO / "output" / f"{SCENARIO}_resources_comparative_tab.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"[OK] Tableau enregistré sous {out_csv}")


if __name__ == "__main__":
    main()
