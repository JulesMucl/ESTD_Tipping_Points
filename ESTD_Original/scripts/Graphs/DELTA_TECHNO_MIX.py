#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# === PARAMÈTRES À MODIFIER ===

REFERENCE = "NUCLEAR/ONLY/BIODIESEL_RE_ONLY_NUCLEAR/BIODIESEL_RE_ONLY_NUCLEAR_0.000"

SCENARIO  = "NUCLEAR/ONLY/BIODIESEL_RE_ONLY_NUCLEAR/BIODIESEL_RE_ONLY_NUCLEAR_0.100"


THRESHOLD_GW = 1.0         # Seuil pour technologies
THRESHOLD_RESOURCE = 0.5   # Seuil pour ressources


def load_ressources(scenario: str) -> pd.DataFrame:
    root = Path(__file__).resolve().parent.parent.parent
    fn = root / "case_studies" / scenario / "output" / "resources_breakdown.txt"

    if not fn.exists():
        print(f"[Erreur] fichier introuvable pour le scénario '{scenario}': {fn}")
        sys.exit(1)

    df = pd.read_csv(fn, sep="\t", engine="python", comment="#")
    df.columns = df.columns.str.strip()

    if 'Name' not in df.columns or 'Used' not in df.columns:
        print(f"Colonnes disponibles dans {fn} :", df.columns.tolist())
        raise KeyError("Colonnes 'Name' et/ou 'Used' introuvables.")

    df['Used'] = pd.to_numeric(df['Used'], errors='coerce')
    return df[['Name', 'Used']].dropna()


def load_assets(scenario: str) -> pd.DataFrame:
    root = Path(__file__).resolve().parent.parent.parent
    fn = root / "case_studies" / scenario / "output" / "assets.txt"
    if not fn.exists():
        print(f"[Erreur] fichier introuvable pour scénario '{scenario}': {fn}")
        sys.exit(1)

    df = pd.read_csv(fn, sep="\t", engine="python", comment="#")
    df.columns = df.columns.str.strip()
    df['f'] = df['f'].replace('Infinity', np.inf)
    df['f'] = pd.to_numeric(df['f'], errors='coerce')

    if 'TECHNOLOGIES' not in df.columns or 'f' not in df.columns:
        print(f"Colonnes disponibles dans {fn} :", df.columns.tolist())
        raise KeyError("Colonnes 'TECHNOLOGIES' et/ou 'f' introuvables.")

    return df[['TECHNOLOGIES', 'f']].dropna()


def compute_delta(ref, scn):
    if ref == 0:
        return np.nan
    return (scn - ref) / ref * 100


def main():
    root = Path(__file__).resolve().parent.parent.parent

    # === TECHNO MIX ===
    df_ref = load_assets(REFERENCE).rename(columns={'f': 'f_ref'})
    df_scn = load_assets(SCENARIO).rename(columns={'f': 'f_scenario'})

    df_cmp = pd.merge(df_ref, df_scn, on='TECHNOLOGIES', how='outer').fillna(0)
    df_cmp['diff_gw'] = df_cmp['f_scenario'] - df_cmp['f_ref']
    df_cmp['delta_pct'] = df_cmp.apply(lambda row: compute_delta(row['f_ref'], row['f_scenario']), axis=1)
    df_cmp['delta_str'] = df_cmp['delta_pct'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else 'NA')
    df_cmp['diff_str'] = df_cmp['diff_gw'].apply(lambda x: f"{x:+.2f}")
    df_cmp = df_cmp[df_cmp['diff_gw'].abs() > THRESHOLD_GW]

    df_out = df_cmp[
        ['TECHNOLOGIES', 'f_ref', 'f_scenario', 'diff_str', 'delta_str']
    ].rename(columns={
        'TECHNOLOGIES': 'Techno',
        'f_ref': "Réf [GW]",
        'f_scenario': f"{SCENARIO} [GW]",
        'diff_str': 'Différence [GW]',
        'delta_str': 'Δ [%]'
    })

    df_out["Réf [GW]"] = df_out["Réf [GW]"].round(2)
    df_out[f"{SCENARIO} [GW]"] = df_out[f"{SCENARIO} [GW]"].round(2)

    print("\n🧱 COMPARAISON DES TECHNOLOGIES INSTALLÉES")
    print(df_out.to_string(index=False))


    # === RESOURCE MIX ===
    df_ref_r = load_ressources(REFERENCE).rename(columns={'Used': 'used_ref'})
    df_scn_r = load_ressources(SCENARIO).rename(columns={'Used': 'used_scenario'})

    df_cmp_r = pd.merge(df_ref_r, df_scn_r, on='Name', how='outer').fillna(0)
    df_cmp_r['diff_gw'] = df_cmp_r['used_scenario'] - df_cmp_r['used_ref']
    df_cmp_r['delta_pct'] = df_cmp_r.apply(lambda row: compute_delta(row['used_ref'], row['used_scenario']), axis=1)
    df_cmp_r['delta_str'] = df_cmp_r['delta_pct'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else 'NA')
    df_cmp_r['diff_str'] = df_cmp_r['diff_gw'].apply(lambda x: f"{x:+.2f}")
    df_cmp_r = df_cmp_r[df_cmp_r['diff_gw'].abs() > THRESHOLD_RESOURCE]

    df_out_r = df_cmp_r[
        ['Name', 'used_ref', 'used_scenario', 'diff_str', 'delta_str']
    ].rename(columns={
        'Name': 'Ressource',
        'used_ref': "Réf [GW]",
        'used_scenario': f"{SCENARIO} [GW]",
        'diff_str': 'Différence [GW]',
        'delta_str': 'Δ [%]'
    })

    df_out_r["Réf [GW]"] = df_out_r["Réf [GW]"].round(2)
    df_out_r[f"{SCENARIO} [GW]"] = df_out_r[f"{SCENARIO} [GW]"].round(2)

    print("\n🌿 COMPARAISON DES RESSOURCES UTILISÉES")
    print(df_out_r.to_string(index=False))


if __name__ == "__main__":
    main()
