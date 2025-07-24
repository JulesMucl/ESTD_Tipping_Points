import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 📁 Dossier de scénarios
root = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/case_studies/Methanol_H2")

# 📂 Scénarios
methanol_gwps = [0.22, 0.23, 0.24, 0.25]
h2_gwps = [round(i * 0.05, 3) for i in range(0, 8)]
scenarios = [f"meth{g_meth:.3f}_h2{g_h2:.3f}" for g_meth in methanol_gwps for g_h2 in h2_gwps]

# 📊 Données
data = {}
costs = {}

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

    if fn_log.exists():
        with open(fn_log, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("TotalCost"):
                    try:
                        costs[scenario] = float(line.strip().split()[1])
                    except:
                        pass
                    break

combined_df = pd.DataFrame(data).fillna(0).T

if not combined_df.empty:
    max_usage = combined_df.max()
    min_usage = combined_df.min()
    variation_pct = ((max_usage - min_usage) / max_usage.replace(0, 1e-9)) * 100
    low_var_or_low_usage = variation_pct[variation_pct < 3].index.union(max_usage[max_usage < 0.1].index)

    if "METHANOL_RE" in low_var_or_low_usage:
        low_var_or_low_usage = low_var_or_low_usage.drop("METHANOL_RE")

    stable_df = combined_df[low_var_or_low_usage].sum(axis=1).rename("Autres (stables)").to_frame()
    variable_df = combined_df.drop(columns=low_var_or_low_usage)
    final_df = pd.concat([stable_df, variable_df], axis=1)
    final_df = final_df[["Autres (stables)"] + variable_df.columns.tolist()]

    # 📈 Graphe empilé
    fig, ax1 = plt.subplots(figsize=(14, 8))
    final_df.plot(kind="bar", stacked=True, width=0.8, ax=ax1)
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[1:], labels[1:], title="Ressources", bbox_to_anchor=(1.02, 1), loc="upper left")

    ax3 = ax1.twinx()
    scenarios_list = final_df.index.tolist()
    cost_values = [costs.get(s, None) for s in scenarios_list]
    ax3.plot(range(len(scenarios_list)), cost_values, color="black", marker="o", label="TotalCost (€)")
    ax3.set_ylabel("Coût total [€]", fontsize=12, color="black")
    ax1.set_title("Utilisation des ressources par scénario (gwp_op) avec coût total", fontsize=14)
    ax1.set_xlabel("Scénarios")
    ax1.set_ylabel("Utilisation des ressources [GWh/an]")
    ax3.tick_params(axis="y", labelcolor="black")
    plt.xticks(ticks=range(len(scenarios_list)), labels=scenarios_list, rotation=45)
    plt.tight_layout()
    ax3.legend(loc="upper right")
    plt.show()
else:
    print("[❌] Aucune donnée de ressources disponible.")



    # === FLUX ENTRANTS/SORTANTS DE SYN_METHANOLATION ===
flux_in, flux_out = {}, {}

for scenario in scenarios:
    fn_year = root / scenario / "output" / "year_balance.txt"
    if fn_year.exists():
        try:
            df = pd.read_csv(fn_year, sep="\t", engine="python", index_col=0)
            df.columns = df.columns.str.strip()
            df.index = df.index.str.strip()
            if 'SYN_METHANOLATION' in df.index:
                row = df.loc['SYN_METHANOLATION']
                flux_in[scenario] = row[row > 0]
                flux_out[scenario] = -row[row < 0]
        except Exception as e:
            print(f"[⚠] Erreur de parsing pour {scenario} : {e}")

# 📊 DataFrames
df_in = pd.DataFrame(flux_in).fillna(0).T
df_out = pd.DataFrame(flux_out).fillna(0).T

# 📈 Graphe des flux entrants
if not df_in.empty:
    df_in.plot(kind="bar", stacked=True, figsize=(14, 6))
    plt.title("Flux entrants de SYN_METHANOLATION par scénario")
    plt.xlabel("Scénarios")
    plt.ylabel("Entrée [GWh/an]")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
else:
    print("[⚠] Aucun flux entrant détecté.")

# 📈 Graphe des flux sortants
if not df_out.empty:
    df_out.plot(kind="bar", stacked=True, figsize=(14, 6))
    plt.title("Flux sortants de SYN_METHANOLATION par scénario")
    plt.xlabel("Scénarios")
    plt.ylabel("Sortie [GWh/an]")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
else:
    print("[⚠] Aucun flux sortant détecté.")

