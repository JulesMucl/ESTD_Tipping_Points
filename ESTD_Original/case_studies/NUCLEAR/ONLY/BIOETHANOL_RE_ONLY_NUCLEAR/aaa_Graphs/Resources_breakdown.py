import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import csv


#------------------------------------------------------- BIOETHANOL_RE_ONLY_NUCLEAR ---------------------------------------------------


# Configuration centralisée
config = {

    # Ressources à exclure des graphiques
    "excluded_resources": [
        "CO2_EMISSIONS",
        "CO2_ATM",
        "CO2_INDUSTRY",
        "CO2_CAPTURED"
    ],
    
    "selection_resources": ["AMMONIA_RE", "H2_RE", "GAS_RE","GAS","METHANOL_RE","BIODIESEL","BIOETHANOL"],  # Ressources à sélectionner pour les graphiques

    "selection_technos": ["CCGT_AMMONIA", "IND_COGEN_GAS","SYN_METHANOLATION","INDUSTRY_CCS","IND_BOILER_WOOD","BIOMASS_TO_METHANOL"], # Technologies à sélectionner pour les graphiques
    
    # Paramètres de base pour les chemins et préférences
    "root_prefix": "BIOETHANOL_RE_ONLY_NUCLEAR",  # Préfixe du dossier racine
    "save_path": Path("C:/Users/julem/Dropbox/EPL/TFE/TFE_textes/Images/TIPPING_POINT/NUCLEAR/BIOETHANOL_ONLY_NUCLEAR/"),  # Chemin de sauvegarde des graphiques
    "cost_enabled": True,
    "use_plotly": False,
    
    # Palette de couleurs pour les ressources
    "color_palette": {
        # Couleurs pour les différentes ressources
        "ELECTRICITY": "#003f5c",
        "GASOLINE": "#7a5195",
        "DIESEL": "#ef5675",
        "BIOETHANOL": "#2ca02c",
        "BIODIESEL": "#bc5090",
        "LFO": "#ffa600",
        "GAS": "#ff7c43",
        "GAS_RE": "#f95d6a",
        "WOOD": "#8c564b",
        "WET_BIOMASS": "#bcbd22",
        "COAL": "#343434",
        "URANIUM": "#636363",
        "WASTE": "#9467bd",
        "H2": "#1f77b4",
        "H2_RE": "#1f77b4",
        "AMMONIA": "#2f4b7c",
        "METHANOL": "#d62728",
        "AMMONIA_RE": "#1b9e77",
        "METHANOL_RE": "#f72427",
        "ELEC_EXPORT": "#17becf",
        "CO2_EMISSIONS": "#7f7f7f",
        "RES_WIND": "#2ca02c",
        "RES_SOLAR": "#ffcc00",
        "RES_HYDRO": "#1f78b4",
        "RES_GEO": "#ff8c00",
        "CO2_ATM": "#999999",
        "CO2_INDUSTRY": "#aaaaaa",
        "CO2_CAPTURED": "#66c2a5",
        "Autres (stables)": "#4337EB"
    }
}

markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd']



def extract_cost_from_log(log_file):
    """Extract the cost from a log file."""
    try:
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("TotalCost"):
                    return float(line.strip().split()[1])
    except Exception as e:
        print(f"[⚠] Error reading cost from {log_file}: {e}")
    return None

def load_data(scenarios, root, cost_enabled=True):
    """Load data from scenario files."""
    data, costs = {}, {}
    for scenario in scenarios:
        fn_res = root / scenario / "output" / "resources_breakdown.txt"
        fn_log = root /"log"/ scenario / "output" / "log.txt"
        if fn_res.exists():
            df = pd.read_csv(fn_res, sep="\t", engine="python", comment="#")
            df.columns = df.columns.str.strip()
            df["Name"] = df["Name"].str.strip()
            df = df[["Name", "Used"]]
            df = df[df["Used"] > 0].set_index("Name")
            df = df[~df.index.isin(config["excluded_resources"])]
            data[scenario] = df["Used"]
        else:
            print(f"[⚠] Missing resource file: {scenario}")
        if cost_enabled and fn_log.exists():
            value = extract_cost_from_log(fn_log)
            if value is not None:
                costs[scenario] = value
            else:
                print(f"[⚠] Cost not read for: {scenario}")
    return pd.DataFrame(data).fillna(0).T, costs

def split_stable_resources(df, threshold_pct=1, min_abs=0.1, exclude=None):
    """Split resources into stable and variable based on usage variation."""
    if exclude is None:
        exclude = []
    elif isinstance(exclude, str):
        exclude = [exclude]
    max_usage = df.max()
    min_usage = df.min()
    variation_pct = ((max_usage - min_usage) / max_usage.replace(0, 1e-9)) * 100
    low_var = variation_pct[variation_pct < threshold_pct].index
    low_val = max_usage[max_usage < min_abs].index
    stable = low_var.union(low_val)
    stable = stable.drop(labels=exclude, errors="ignore")
    return stable

def prepare_final_dataframe(df, stable_resources):
    """Prepare the final dataframe by combining stable and variable resources."""
    stable_df = df[stable_resources].sum(axis=1).rename("Autres (stables)")
    variable_df = df.drop(columns=stable_resources)
    final_df = pd.concat([stable_df, variable_df], axis=1)
    return final_df[["Autres (stables)"] + variable_df.columns.tolist()]

def plot_plotly(df, costs):
    """Plot the data using Plotly."""
    fig = go.Figure()
    for col in df.columns:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[col],
            name=col,
            marker=dict(color=config["color_palette"].get(col, "#AAAAAA")),
            hovertemplate=f'{col}: %{{y:.1f}} GWh<extra>Scénario: %{{x}}</extra>'
        ))

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
            hovertemplate='Coût total: %{y:,.0f} €<extra>Scénario: %{x}</extra>'
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
        margin=dict(l=80, r=80, t=80, b=150),  # Augmenter la marge inférieure pour les étiquettes
        hovermode="x unified",
        xaxis_tickangle=-45  # Rotation des étiquettes de l'axe des x
    )
    fig.show()

def plot_matplotlib(df, costs):
    """Plot the data using Matplotlib."""
    fig, ax1 = plt.subplots(figsize=(14, 8))
    colors = [config["color_palette"].get(col, "#AAAAAA") for col in df.columns]
    df.plot(kind="bar", stacked=True, width=0.8, ax=ax1, color=colors)

    ax1.set_title("Utilisation des ressources par scénario" + (" avec coût total" if costs else ""), fontsize=14)
    ax1.set_xlabel("Scénarios", fontsize=12)
    ax1.set_ylabel("Utilisation des ressources [GWh/an]", fontsize=12)

    # Rotation et alignement des étiquettes des abscisses
    plt.xticks(rotation=45, ha='right')

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
    plt.savefig(config["save_path"] / f"{config['root_prefix']}.png", dpi=300, bbox_inches="tight")
    print(f"[✔] Graphique sauvegardé ici : {config['save_path']}")
    plt.show()

def select_most_variable(df, top_n=10, exclude=None):
    """Select the top_n most variable columns in a DataFrame."""
    max_val = df.max()
    min_val = df.min()
    amplitude_abs = max_val - min_val
    if exclude:
        amplitude_abs = amplitude_abs.drop(labels=exclude, errors="ignore")
    return amplitude_abs.sort_values(ascending=False).head(top_n).index.tolist()

def load_installed_capacity(scenarios, root):
    """Load installed capacity data from scenario files."""
    data = {}
    for scenario in scenarios:
        fn = root / scenario / "output" / "assets.txt"
        if not fn.exists():
            print(f"[⚠] Missing assets file: {scenario}")
            continue
        df = pd.read_csv(fn, sep="\t", engine="python", comment="#")
        df.columns = df.columns.str.strip()
        df = df[["TECHNOLOGIES", "f"]].copy()
        df['f'] = df['f'].replace('Infinity', np.inf)
        df['f'] = pd.to_numeric(df['f'], errors='coerce')
        df.set_index("TECHNOLOGIES", inplace=True)
        data[scenario] = df["f"]
    return pd.DataFrame(data).T.fillna(0)

def plot_selected_resources(df_resources, selected_resources, save_as=None):
    """Plot selected resources."""
    plt.figure(figsize=(14, 6))  # Augmenter la taille de la figure
    for i, res in enumerate(selected_resources):
        if res in df_resources.columns:
            plt.plot(df_resources.index, df_resources[res], label=res, linestyle='-', linewidth=2,
                     marker=markers[i % len(markers)],
                     color=config["color_palette"].get(res, "#AAAAAA"), alpha=0.7)
        else:
            print(f"[⚠] Ressource '{res}' non trouvée dans les données.")

    plt.xlabel("Scénarios", fontsize=12)
    plt.ylabel("Utilisation [GWh/an]", fontsize=12)
    plt.title("Utilisation des ressources sélectionnées", fontsize=14)
    plt.xticks(rotation=45, ha='right')  # Rotation et alignement des étiquettes
    plt.legend(title="Ressources", bbox_to_anchor=(1.05, 1), loc='upper left')  # Légende à l'extérieur
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Ajustement de la mise en page
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches="tight")
        print(f"[✔] Courbe enregistrée ici : {save_as}")
    plt.show()

def plot_installed_technos(df_assets, techs_to_plot, save_as=None):
    """Plot installed technologies."""
    plt.figure(figsize=(14, 6))  # Augmenter la taille de la figure
    for i, tech in enumerate(techs_to_plot):
        if tech in df_assets.columns:
            plt.plot(df_assets.index, df_assets[tech], label=tech, linestyle='-', linewidth=2,
                     marker=markers[i % len(markers)],
                     alpha=0.7)
        else:
            print(f"[⚠] Technology '{tech}' not found in data.")

    plt.xlabel("Scénarios", fontsize=12)
    plt.ylabel("Capacité installée [GW]", fontsize=12)
    plt.title("Évolution des capacités installées", fontsize=14)
    plt.xticks(rotation=45, ha='right')  # Rotation et alignement des étiquettes
    plt.legend(title="Technologies", bbox_to_anchor=(1.05, 1), loc='upper left')  # Légende à l'extérieur
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Ajustement de la mise en page
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches="tight")
        print(f"[✔] Courbe enregistrée ici : {save_as}")
    plt.show()

def plot_combined_figure(df_assets, df_resources, cost_dict, selection_technos, selection_resources, save_as=None):
    """Plot a combined figure with selected technologies, resources, and costs, sharing a single x-axis."""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 15), sharex=True)

    # Plot for selected technologies
    for i, tech in enumerate(selection_technos):
        if tech in df_assets.columns:
            ax1.plot(df_assets.index, df_assets[tech], label=tech, linestyle='-', linewidth=2,
                     marker=markers[i % len(markers)], alpha=0.7)
        else:
            print(f"[⚠] Technology '{tech}' not found in data.")
    ax1.set_ylabel("Capacité installée [GW]", fontsize=12)
    ax1.set_title("Évolution des capacités installées pour les technologies sélectionnées", fontsize=14)
    ax1.legend(title="Technologies")
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    # Plot for selected resources
    for res in selection_resources:
        if res in df_resources.columns:
            ax2.plot(df_resources.index, df_resources[res], label=res, marker='o', linestyle='-', linewidth=2,
                     color=config["color_palette"].get(res, "#AAAAAA"), alpha=0.7)
        else:
            print(f"[⚠] Ressource '{res}' non trouvée dans les données.")
    ax2.set_ylabel("Utilisation [GWh/an]", fontsize=12)
    ax2.set_title("Utilisation des ressources sélectionnées", fontsize=14)
    ax2.legend(title="Ressources")
    ax2.grid(axis="y", linestyle="--", alpha=0.3)

    # Plot for costs
    scenario_list = df_resources.index.tolist()
    cost_values = [cost_dict.get(s, None) for s in scenario_list]
    ax3.plot(scenario_list, cost_values, color="black", marker="o", label="Coût total (€)")
    ax3.set_xlabel("Scénarios", fontsize=12)
    ax3.set_ylabel("Coût total [€]", fontsize=12)
    ax3.set_title("Coût total par scénario", fontsize=14)
    ax3.legend(loc="upper right")
    ax3.grid(axis="y", linestyle="--", alpha=0.3)

    # Rotation et alignement des étiquettes des abscisses
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Ajustement de la mise en page
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches="tight")
        print(f"[✔] Figure combinée enregistrée ici : {save_as}")
    plt.show()

def main():
    root_prefix = config["root_prefix"]
    root = Path(f"C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/NUCLEAR/ONLY/{root_prefix}")

    # Récupération automatique de tous les sous-dossiers de scénarios
    scenarios = sorted([
        d.name for d in root.iterdir()
        if d.is_dir() and (d / "output" / "resources_breakdown.txt").exists()
    ])
    print(f"[✅] {len(scenarios)} scénarios détectés dans {root_prefix}")

    df_raw, cost_dict = load_data(scenarios, root, cost_enabled=config["cost_enabled"])
    stable_resources = split_stable_resources(df_raw, exclude="METHANOL_RE")
    df_final = prepare_final_dataframe(df_raw, stable_resources)

    if config["use_plotly"]:
        plot_plotly(df_final, cost_dict if config["cost_enabled"] else None)
    else:
        plot_matplotlib(df_final, cost_dict if config["cost_enabled"] else None)

    selected_resources = select_most_variable(df_raw, top_n=10, exclude=["Autres (stables)"])
    print("[🔍] Selected resources:", selected_resources)
    plot_selected_resources(df_raw, selected_resources, save_as=config["save_path"] / f"{config['root_prefix']}_resources.png")

    df_assets = load_installed_capacity(scenarios, root)
    selected_techs = select_most_variable(df_assets, top_n=20)
    print("[🔍] Selected technologies:", selected_techs)
    plot_installed_technos(df_assets, selected_techs, save_as=config["save_path"] / f"{config['root_prefix']}_techs.png")

    selection_technos = config["selection_technos"]
    selection_resources = config["selection_resources"]
    plot_installed_technos(df_assets, selection_technos, save_as=config["save_path"] / f"{config['root_prefix']}_techs_case.png")
    plot_selected_resources(df_raw, selection_resources, save_as=config["save_path"] / f"{config['root_prefix']}_resources_case.png")

    # Create and save the combined figure
    plot_combined_figure(df_assets, df_raw, cost_dict, selection_technos, selection_resources,
                         save_as=config["save_path"] / f"{config['root_prefix']}_combined_figure.png")

if __name__ == "__main__":
    main()


#------------------------------------------------------- BIOETHANOL_RE_ONLY_NUCLEAR ---------------------------------------------------
