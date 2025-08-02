#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# === 📥 PARAMÈTRES SCÉNARIOS ===
root_prefix = "GAS_RE_only"
ZOOM = False  # True pour zoom, False pour normal

if ZOOM:
    SCENARIO = "GAS_RE_gwp_0.030"
    root = Path(f"C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/ONLY/{root_prefix}/ZOOM")


else:
    SCENARIO = "H2_RE_gwp_0.020"
    root = Path(f"C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/ONLY/{root_prefix}")

# === 📂 CHARGEMENT DES DONNÉES ===
def load_breakdown(scenario_dir: Path, scenario_name: str, used_col: str) -> pd.DataFrame:
    """
    Charge le fichier resources_breakdown.txt et renvoie un DataFrame avec ['Name', used_col, 'Potential'].
    """
    fn = scenario_dir / scenario_name / "output" / "resources_breakdown.txt"
    if not fn.exists():
        print(f"[Erreur] fichier introuvable pour scénario '{scenario_name}': {fn}")
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
    # Charger les données des deux scénarios
    base_case = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/Belgium_2050_base")
    df_ref = load_breakdown(base_case, "", 'Used_ref')
    df_scn = load_breakdown(root, SCENARIO, 'Used_scenario')

    # Fusionner et traiter
    df_cmp = pd.merge(df_ref, df_scn, on='Name', how='outer')
    df_cmp['Used_ref'] = df_cmp['Used_ref'].fillna(0)
    df_cmp['Used_scenario'] = df_cmp['Used_scenario'].fillna(0)
    df_cmp['Potential'] = df_cmp['Potential_x'].fillna(df_cmp['Potential_y'])
    df_cmp.drop(columns=[c for c in df_cmp.columns if c.startswith('Potential_')], inplace=True)

    # Différence absolue et en %
    df_cmp['diff'] = df_cmp['Used_scenario'] - df_cmp['Used_ref']
    df_cmp['delta_pct'] = df_cmp.apply(
        lambda row: np.nan if row['Used_ref'] == 0 else (row['diff'] / row['Used_ref'] * 100), axis=1
    )

    # Formatage
    df_cmp['Différence [GW]'] = df_cmp['diff'].map(lambda x: f"{x:+.2f}")
    df_cmp['Δ [%]'] = df_cmp['delta_pct'].map(lambda x: f"{x:+.1f}%" if pd.notnull(x) else 'NA')

    # Tableau final
    df_out = df_cmp[['Name', 'Used_ref', 'Used_scenario', 'Différence [GW]', 'Δ [%]', 'Potential']].rename(columns={
        'Name': 'Ressource',
        'Used_ref': 'Utilisée Réf [GW]',
        'Used_scenario': f'Utilisée {SCENARIO} [GW]'
    })

    print(df_out.to_string(index=False))

    # Totaux
    total_ref = df_out['Utilisée Réf [GW]'].sum()
    total_scn = df_out[f'Utilisée {SCENARIO} [GW]'].sum()
    print(f"\nSomme Utilisée Réf [GW] : {total_ref:.2f}")
    print(f"Somme Utilisée {SCENARIO} [GW] : {total_scn:.2f}")

    # Sauvegarde CSV
    out_csv = root / SCENARIO / "output" / f"{SCENARIO}_resources_comparative_tab.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_csv, index=False)
    print(f"[✔] Tableau enregistré sous {out_csv}")

    


if __name__ == "__main__":
    main()
