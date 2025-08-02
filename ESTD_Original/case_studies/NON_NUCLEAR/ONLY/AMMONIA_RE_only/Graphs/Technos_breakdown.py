#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# === 📥 PARAMÈTRES UTILISATEUR ===
scenario_prefix = "AMMONIA_RE_gwp_"
root_prefix     = "AMMONIA_RE_only"
# liste des scénarios de 0.000 à 0.045 par pas de 0.005
scenarios = [f"{scenario_prefix}{i/100:.3f}" for i in range(0, 50, 5)]
root = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/ONLY") / root_prefix

use_plotly = True   # True = Plotly interactif, False = Matplotlib statique
threshold_pct = 1    # % de variation en-dessous duquel on regroupe
min_abs      = 0.1   # valeur max en-dessous de laquelle on regroupe


# === 🔍 FONCTIONS ===

def load_all_capacities(scenarios, base_dir):
    """
    Lit chaque assets.txt et renvoie un DataFrame
    index=scénarios, colonnes=technos, valeurs=f.
    """
    data = {}
    for scen in scenarios:
        fn = base_dir / scen / "output" / "assets.txt"
        if not fn.exists():
            print(f"[⚠] Pas d'assets.txt pour {scen} ({fn})")
            continue

        df = pd.read_csv(fn, sep="\t", engine="python", comment="#")
        df.columns = df.columns.str.strip()
        # convertit 'Infinity' en np.inf puis numeric
        df['f'] = df['f'].replace('Infinity', np.inf)
        df['f'] = pd.to_numeric(df['f'], errors='coerce')

        # récupère la série f par techno
        ser = df.set_index('TECHNOLOGIES')['f']
        data[scen] = ser

    # pivot en DataFrame, remplace NaN par 0
    df_caps = pd.DataFrame(data).T.fillna(0)
    return df_caps

def find_stable_tech(df, threshold_pct, min_abs, exclude=None):
    """
    Identifie technos à faible variation ou très petites
    pour les regrouper sous 'Autres (stables)'.
    """
    mx = df.max()
    mn = df.min()
    var_pct = ((mx - mn) / mx.replace(0,1e-9)) * 100

    low_var = var_pct[var_pct < threshold_pct].index
    low_val = mx[mx < min_abs].index
    stable = low_var.union(low_val)
    if exclude in stable:
        stable = stable.drop(exclude)
    return stable

def prepare_df(df, stable_list):
    """
    Regroupe les stable en 'Autres (stables)' en tête de colonnes.
    """
    autres = df[stable_list].sum(axis=1).rename("Autres (stables)")
    df_var = df.drop(columns=stable_list)
    return pd.concat([autres, df_var], axis=1)[["Autres (stables)"] + df_var.columns.tolist()]

def plot_matplotlib(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    cols   = df.columns.tolist()
    #colors = [color_palette.get(c, "#CCCCCC") for c in cols]
    df.plot(kind="bar", stacked=True, ax=ax,  width=0.8) #color=colors,

    ax.set_title("Capacités f des technologies par scénario", fontsize=14)
    ax.set_xlabel("Scénarios", fontsize=12)
    ax.set_ylabel("Capacité f [GW or GWh]", fontsize=12)
    plt.xticks(rotation=45)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

def plot_plotly(df):
    import plotly.graph_objects as go
    fig = go.Figure()
    for techno in df.columns:
        fig.add_trace(go.Bar(
            x=df.index, y=df[techno], name=techno,
            #marker=dict(color=color_palette.get(techno, "#CCCCCC")),
            hovertemplate=f"{techno}: %{{y:.2f}}<br>Scénario: %{{x}}"
        ))
    fig.update_layout(
        title="Capacités f des technologies par scénario",
        xaxis_title="Scénarios", yaxis_title="Capacité f",
        barmode="stack", legend=dict(x=1.02,y=1),
        margin=dict(l=80,r=200,t=80,b=120), hovermode="x unified"
    )
    fig.show()

# === 🧪 MAIN ===

if __name__ == "__main__":
    # 1) Chargement des capacités
    df_caps = load_all_capacities(scenarios, root)
    if df_caps.empty:
        print("[Erreur] aucun scénario chargé, vérifiez les chemins.")
        sys.exit(1)

    # 2) Identification des technos stables
    stable = find_stable_tech(df_caps, threshold_pct, min_abs)

    # 3) Préparation de la table finale
    df_final = prepare_df(df_caps, stable)

    # 4) Trace
    if use_plotly:
        plot_plotly(df_final)
    else:
        plot_matplotlib(df_final)
