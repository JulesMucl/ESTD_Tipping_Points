#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# === 📥 PARAMÈTRES À MODIFIER ===
root_prefix = "AMMONIA_RE_ONLY_NUCLEAR"               # nom du dossier racine



scenario_name = "AMMONIA_RE_ONLY_NUCLEAR_0.400"         # nom du scénario

base_path = Path(f"C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/NUCLEAR/ONLY/{root_prefix}/{scenario_name}/output/sankey")  # NORMAL

sources_initiales = ["Imp. Gas", "Imp. Gas RE", "Imp. Ammonia RE","Imp. H2 RE"]  # "Wet biomass", , "Waste" , "Wood"
nodes_terminaux = {"Elec", "Heat HT"}


outputfile = base_path / f"{root_prefix}_{scenario_name}_sankey.html"

def drawSankey(path, outputfile='TO_REPLACE', auto_open=True):
    flows = pd.read_csv(path / "input2sankey.csv")

    # === 🔍 Filtrer récursivement depuis certaines sources, avec coupure sur certains nœuds ===


    selected_flows = pd.DataFrame()
    current_sources = set(sources_initiales)
    all_used_sources = set()

    while current_sources:
        # Garder les lignes dont la source est dans les sources actuelles
        next_flows = flows[flows['source'].isin(current_sources)]

        if next_flows.empty:
            break

        selected_flows = pd.concat([selected_flows, next_flows])
        all_used_sources.update(current_sources)

        # Déterminer les nouvelles sources : cibles des flux, sauf si ce sont des nœuds terminaux
        next_targets = set(next_flows['target'].unique())
        current_sources = next_targets - nodes_terminaux - all_used_sources

        # Supprimer les lignes déjà traitées pour éviter les boucles
        flows = flows[~flows.index.isin(next_flows.index)]

    selected_flows.reset_index(drop=True, inplace=True)

    # === 🔁 Génération du diagramme ===
    fig = genSankey(selected_flows, cat_cols=['source', 'target'], value_cols='realValue', title='Energy Flow (Filtered)', color_col='layerColor')
    fig.write_html(str(outputfile), auto_open=auto_open)
    print(f"[✔] Sankey diagram saved to: {outputfile}")




def genSankey(df, cat_cols=[], value_cols='', title='Sankey Diagram', color_col=[]):
    labelList = []
    colorNumList = []

    for catCol in cat_cols:
        labelListTemp = list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList += labelListTemp

    labelList = list(dict.fromkeys(labelList))

    # Couleurs simples, facilement distinguables
    colorPalette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList += [colorPalette[idx % len(colorPalette)]] * colorNum

    for i in range(len(cat_cols) - 1):
        if i == 0:
            sourceTargetDf = df[[cat_cols[i], cat_cols[i + 1], value_cols, color_col]]
            sourceTargetDf.columns = ['source', 'target', 'count', 'color']
        else:
            tempDf = df[[cat_cols[i], cat_cols[i + 1], value_cols, color_col]]
            tempDf.columns = ['source', 'target', 'count', 'color']
            sourceTargetDf = pd.concat([sourceTargetDf, tempDf])

        sourceTargetDf = sourceTargetDf.groupby(['source', 'target']).agg({'count': 'sum', 'color': 'first'}).reset_index()

    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))

    data = go.Sankey(
        valueformat=".1f",
        valuesuffix=" TWh",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labelList,
            color=colorList
        ),
        link=dict(
            source=sourceTargetDf['sourceID'],
            target=sourceTargetDf['targetID'],
            value=sourceTargetDf['count'],
            color=sourceTargetDf['color'].apply(lambda h: hexToRGBA(h, 0.5))
        )
    )

    fig = go.Figure(data=[data], layout=dict(title=title, font=dict(size=10)))
    return fig

def hexToRGBA(hex, alpha):
    hex = hex.lstrip('#')
    r = int(hex[0:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"

# === ✅ EXECUTION ===
if not base_path.exists():
    print(f"[❌] Path not found: {base_path}")
else:
    drawSankey(path=base_path, outputfile=outputfile, auto_open=True)
