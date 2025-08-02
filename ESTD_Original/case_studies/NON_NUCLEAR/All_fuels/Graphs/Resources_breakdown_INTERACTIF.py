import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 📁 Chemin vers les scénarios
root = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/All_fuels")
scenarios = [f"all_fuels_RE_gwp_{i/1000:.3f}" for i in range(0, 63)]

# 📊 Stockage
resource_data = {}
total_costs = {}

# 📥 Extraction
for scenario in scenarios:
    fn_res = root / scenario / "output" / "resources_breakdown.txt"
    fn_log = root / scenario / "output" / "log.txt"

    # Lecture des ressources
    if fn_res.exists():
        df = pd.read_csv(fn_res, sep="\t", engine="python", comment="#")
        df.columns = df.columns.str.strip()
        df["Name"] = df["Name"].str.strip()
        df = df[["Name", "Used"]]
        df = df[df["Used"] > 0].set_index("Name")
        resource_data[scenario] = df["Used"]

    # Lecture du coût total
    if fn_log.exists():
        with open(fn_log, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("TotalCost"):
                    try:
                        total_costs[scenario] = float(line.strip().split()[1])
                    except:
                        pass
                    break

# 📐 Structuration
df_resources = pd.DataFrame(resource_data).fillna(0).T

# Filtrage des ressources peu variables
max_usage = df_resources.max()
min_usage = df_resources.min()
variation_pct = ((max_usage - min_usage) / max_usage.replace(0, 1e-9)) * 100
low_var_or_low_usage = variation_pct[variation_pct < 3].index.union(max_usage[max_usage < 0.1].index)
low_var_or_low_usage = low_var_or_low_usage.drop("METHANOL_RE", errors="ignore")

# Séparation des colonnes
stable_df = df_resources[low_var_or_low_usage].sum(axis=1).rename("Autres (stables)")
variable_df = df_resources.drop(columns=low_var_or_low_usage)
final_df = pd.concat([stable_df, variable_df], axis=1)
final_df = final_df[["Autres (stables)"] + variable_df.columns.tolist()]

# === 📈 Créer le graphe interactif ===
fig = go.Figure()

# Barres empilées
for col in final_df.columns:
    fig.add_trace(go.Bar(
        x=final_df.index,
        y=final_df[col],
        name=col,
        hovertemplate=f'{col}: %{{y:.1f}} GWh<br>Scénario: %{{x}}'
    ))

# Ligne de coût total (axe secondaire)
costs_list = [total_costs.get(s, None) for s in final_df.index]
fig.add_trace(go.Scatter(
    x=final_df.index,
    y=costs_list,
    mode='lines+markers',
    name="Coût total",
    yaxis="y2",
    line=dict(color="black", width=3),
    marker=dict(size=8),
    hovertemplate='Coût total: %{y:,.0f} €<br>Scénario: %{x}'
))

# 🧭 Mise en page
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

# ✨ Affichage interactif
fig.show()
