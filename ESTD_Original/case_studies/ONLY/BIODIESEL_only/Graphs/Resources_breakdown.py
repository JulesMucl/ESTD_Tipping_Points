import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from pathlib import Path


# === 📥 PARAMÈTRES ===
scenario_prefix = "BIODIESEL_gwp_"
root_prefix = "BIODIESEL_only"
scenarios = [f"{scenario_prefix}{i/100:.3f}" for i in range(0, 60, 2)]

root = Path(f"C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/ONLY/{root_prefix}")
save_path = Path(f"C:/Users/julem/Dropbox/EPL/TFE/TFE_textes/Images/TIPPING_POINT/{root_prefix}.png")

cost = True  # 🔁 Activer ou non l'extraction du coût total
use_plotly = False  # 🔁 Affichage interactif ou statique



import csv

# Dictionnaire des ressources et leurs couleurs
color_palette = {
    "ELECTRICITY": "#003f5c",         # Bleu foncé
    "GASOLINE": "#7a5195",            # Violet profond
    "DIESEL": "#ef5675",              # Rouge vif
    "BIOETHANOL": "#2ca02c",          # Vert intense
    "BIODIESEL": "#bc5090",           # Rose-violet
    "LFO": "#ffa600",                 # Orange
    "GAS": "#ff7c43",                 # Orange vif
    "GAS_RE": "#f95d6a",              # Corail rouge
    "WOOD": "#8c564b",                # Marron foncé
    "WET_BIOMASS": "#bcbd22",         # Jaune-vert saturé
    "COAL": "#343434",                # Noir-gris
    "URANIUM": "#636363",             # Gris neutre
    "WASTE": "#9467bd",               # Violet pur
    "H2": "#1f77b4",                  # Bleu classique
    "H2_RE": "#1f77b4",               # Même teinte pour cohérence
    "AMMONIA": "#2f4b7c",             # Bleu nuit
    "METHANOL": "#d62728",            # Rouge franc
    "AMMONIA_RE": "#1b9e77",          # Vert sapin
    "METHANOL_RE": "#f72427",         # Rouge pur
    "ELEC_EXPORT": "#17becf",         # Bleu cyan
    "CO2_EMISSIONS": "#7f7f7f",       # Gris
    "RES_WIND": "#2ca02c",            # Vert
    "RES_SOLAR": "#ffcc00",           # Jaune fort
    "RES_HYDRO": "#1f78b4",           # Bleu moyen
    "RES_GEO": "#ff8c00",             # Orange foncé
    "CO2_ATM": "#999999",             # Gris clair
    "CO2_INDUSTRY": "#aaaaaa",        # Argenté
    "CO2_CAPTURED": "#66c2a5",        # Turquoise
    "Autres (stables)": "#4337EB"     # Gris foncé neutre
}



# === 🔍 FONCTIONS ===
def extract_cost_from_log(log_file):
    try:
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("TotalCost"):
                    return float(line.strip().split()[1])
    except Exception as e:
        print(f"[⚠] Erreur lecture coût {log_file} : {e}")
    return None


def load_data(scenarios, root, cost_enabled=True):
    data, costs = {}, {}
    for scenario in scenarios:
        fn_res = root / scenario / "output" / "resources_breakdown.txt"
        fn_log = root / scenario / "output" / "log.txt"

        if fn_res.exists():
            df = pd.read_csv(fn_res, sep="\t", engine="python", comment="#")
            df.columns = df.columns.str.strip()
            df["Name"] = df["Name"].str.strip()
            df = df[["Name", "Used"]]
            df = df[df["Used"] > 0].set_index("Name")
            data[scenario] = df["Used"]
        else:
            print(f"[⚠] Fichier res manquant : {scenario}")

        if cost_enabled and fn_log.exists():
            value = extract_cost_from_log(fn_log)
            if value is not None:
                costs[scenario] = value
            else:
                print(f"[⚠] Coût non lu pour : {scenario}")

    return pd.DataFrame(data).fillna(0).T, costs


def split_stable_resources(df, threshold_pct=1, min_abs=0.1, exclude=None):
    max_usage = df.max()
    min_usage = df.min()
    variation_pct = ((max_usage - min_usage) / max_usage.replace(0, 1e-9)) * 100
    low_var = variation_pct[variation_pct < threshold_pct].index
    low_val = max_usage[max_usage < min_abs].index
    stable = low_var.union(low_val)
    if exclude and exclude in stable:
        stable = stable.drop(exclude)
    return stable


def prepare_final_dataframe(df, stable_resources):
    stable_df = df[stable_resources].sum(axis=1).rename("Autres (stables)")
    variable_df = df.drop(columns=stable_resources)
    final_df = pd.concat([stable_df, variable_df], axis=1)
    return final_df[["Autres (stables)"] + variable_df.columns.tolist()]


def plot_plotly(df, costs):
    fig = go.Figure()

    # Barres empilées
    for col in df.columns:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[col],
            name=col,
            marker=dict(color=color_palette.get(col, "#AAAAAA")),
            hovertemplate=f'{col}: %{{y:.1f}} GWh<br>Scénario: %{{x}}'
        ))

    # Ligne de coût total
    if costs:
        costs_list = [costs.get(s, None) for s in df.index]
        fig.add_trace(go.Scatter(
            x=df.index,
            y=costs_list,
            mode='lines+markers',
            name="Coût total",
            yaxis="y2",
            line=dict(color="black", width=3),
            marker=dict(size=8),
            hovertemplate='Coût total: %{y:,.0f} €<br>Scénario: %{x}'
        ))

    fig.update_layout(
        title="Utilisation des ressources et coût total par scénario",
        xaxis_title="Scénarios (gwp_op)",
        yaxis=dict(title="Utilisation des ressources [GWh/an]"),
        yaxis2=dict(
            title="Coût total [€]",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        barmode="stack",
        legend=dict(x=1.01, y=1),
        margin=dict(l=80, r=80, t=80, b=120),
        hovermode="x unified"
    )

    fig.show()


def plot_matplotlib(df, costs):
    fig, ax1 = plt.subplots(figsize=(14, 8))
    colors = [color_palette.get(col, "#AAAAAA") for col in df.columns]
    df.plot(kind="bar", stacked=True, width=0.8, ax=ax1, color=colors)


    ax1.set_title("Utilisation des ressources par scénario" + (" avec coût total" if costs else ""), fontsize=14)
    ax1.set_xlabel("Scénarios", fontsize=12)
    ax1.set_ylabel("Utilisation des ressources [GWh/an]", fontsize=12)
    plt.xticks(rotation=45)

    if costs:
        ax2 = ax1.twinx()
        scenario_list = df.index.tolist()
        cost_values = [costs.get(s, None) for s in scenario_list]
        ax2.plot(range(len(scenario_list)), cost_values, color="black", marker="o", label="TotalCost (€)")
        ax2.set_ylabel("Coût total [€]", fontsize=12, color="black")
        ax2.tick_params(axis="y", labelcolor="black")
        ax2.legend(loc="upper right")

    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[1:], labels[1:], title="Ressources", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()

    
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"[✔] Graphique sauvegardé ici : {save_path}")

    plt.show()


# === 🧪 MAIN SCRIPT ===
df_raw, cost_dict = load_data(scenarios, root, cost_enabled=cost)
stable_resources = split_stable_resources(df_raw, exclude="METHANOL_RE")
df_final = prepare_final_dataframe(df_raw, stable_resources)

if use_plotly:
    plot_plotly(df_final, cost_dict if cost else None)
else:
    plot_matplotlib(df_final, cost_dict if cost else None)
