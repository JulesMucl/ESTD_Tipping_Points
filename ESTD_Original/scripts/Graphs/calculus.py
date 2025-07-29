from pathlib import Path
import pandas as pd

# === Chemins des fichiers ===
Technologies_root = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/Data/2050/Technologies_jules.csv")
Resources_root = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/Data/2050/Resources_jules.csv")
Layers_root = Path("C:/Users/julem/EnergyScope_Original/ESTD_Original/Data/2050/Layers_in_out.csv")

# === Lecture du fichier Technologies ===
df_tech = pd.read_csv(Technologies_root, sep=";", skiprows=0)
df_tech.columns = df_tech.columns.str.strip()

# Nettoyage des données : conversion des nombres (virgule → point)
for col in ["c_p", "c_inv", "c_maint", "lifetime"]:
    df_tech[col] = (
        df_tech[col]
        .astype(str)
        .str.strip()
        .str.replace(",", ".")
        .replace("[]", pd.NA)
        .astype("float64")
    )


# === Lecture du fichier Resources ===
df_resources = pd.read_csv(Resources_root, sep=";")
df_resources.columns = df_resources.columns.str.strip()
df_resources["parameter name"] = df_resources["parameter name"].astype(str).str.strip()
df_resources["c_op"] = df_resources["c_op"].astype(str).str.replace(",", ".").astype(float)

# === Lecture du fichier Layers_in_out ===
layers_df = pd.read_csv(Layers_root, sep=";", index_col=0)
layers_df.columns = layers_df.columns.str.strip()
layers_df.index = layers_df.index.str.strip()

# === Fonction pour extraire le ratio input/output ===
def get_ratio(techno_name: str, input_layer: str, output_layer: str) -> float:
    if techno_name not in layers_df.index:
        raise ValueError(f"Technologie '{techno_name}' introuvable dans Layers_in_out.csv")

    row = layers_df.loc[techno_name]

    val_input = row.get(input_layer)
    val_output = row.get(output_layer)

    if pd.isna(val_input) or pd.isna(val_output):
        raise ValueError(f"Flux '{input_layer}' ou '{output_layer}' manquant pour {techno_name}")

    if float(val_output) != 1:
        raise ValueError(f"Le flux de sortie '{output_layer}' ne vaut pas 1 pour {techno_name} (valeur = {val_output})")

    if float(val_input) >= 0:
        raise ValueError(f"Le flux d'entrée '{input_layer}' n'est pas valide (valeur = {val_input})")

    return abs(float(val_input))

# === Formule de coût techno ===
def cost_techno(cp, tau, c_inv, c_maint, ratio, c_op):
    return (1 / cp) * (1 / 8760) * (tau * c_inv + c_maint) + (ratio * c_op)

# === Fonction principale : techno → coût [M€/GWh] ===
def techno(name, input, output,ressource):
    
    row = df_tech[df_tech["Technologies param"].str.strip() == name]
    if row.empty:
        raise ValueError(f"Technologie '{name}' introuvable dans Technologies.csv.")

    cp = row["c_p"].values[0]
    c_inv = row["c_inv"].values[0]
    c_maint = row["c_maint"].values[0]
    lifetime = row["lifetime"].values[0]

    i_rate = 0.015
    tau = (i_rate * (1 + i_rate) ** lifetime) / ((1 + i_rate) ** lifetime - 1)

    ratio = get_ratio(name, input_layer=input, output_layer=output)

    res_row = df_resources[df_resources["parameter name"] == ressource]
    if res_row.empty:
        raise ValueError(f"Ressource '{input}' introuvable dans Resources.csv")

    c_op = res_row["c_op"].values[0]

    return cost_techno(cp, tau, c_inv, c_maint, ratio, c_op) #, ratio, lifetime, c_inv, c_maint, c_op, i_rate, tau, cp

if __name__ == "__main__":
    cost = techno("CCGT_AMMONIA", input="AMMONIA", output="ELECTRICITY", ressource="AMMONIA_RE")

    print(cost)
    print(f"Coût spécifique de CCGT_AMMONIA : {cost:.4f} M€/GWh")

















# def cost_IND_COGEN_GAS_ELEC():
#     cp = 0.85
#     tau = 0.048263
#     c_inv = 1309.8
#     c_maint = 84.1924
#     ratio_heat = 2.17
#     ratio_elec = 2.26041
#     c_op = 0.10430636


#     return cost_techno(cp, tau, c_inv, c_maint, ratio_elec, c_op)

# def cost_IND_COGEN_GAS_HEAT():
#     cp = 0.85
#     tau = 0.048263
#     c_inv = 1309.8
#     c_maint = 84.1924
#     ratio_heat = 2.17
#     ratio_elec = 2.26041
#     c_op = 0.10430636


#     return cost_techno(cp, tau, c_inv, c_maint, ratio_heat, c_op)

# def cost_CCGT_AMMONIA():
#     cp = 0.63
#     tau = 0.048263
#     c_inv = 750.87
#     c_maint = 19.0172
#     ratio_heat = 0
#     ratio_elec = 1.952
#     c_op = 0.07089528

#     return cost_techno(cp, tau, c_inv, c_maint,ratio_elec, c_op)

# def cost_BOILER_WOOD():
#     cp = 0.95
#     tau = 0.048263
#     c_inv = 1000
#     c_maint = 50
#     ratio_heat = 1
#     c_op = 0.03550648

#     return cost_techno(cp, tau, c_inv, c_maint, ratio_heat, c_op)



# print('---------------------------------------')
# print("ELEC PRODUCTION")
# print("Prix d'1 GWh elec via cogen gas    - GAS RE Imp.     ===",cost_IND_COGEN_GAS_ELEC())
# print("Prix d'1 GWh elec via CCGT ammonia - AMMONIA RE Imp. ===",cost_CCGT_AMMONIA())
# print('---------------------------------------')
# print("HEAT PRODUCTION")
# print("Prix d'1 GWh HEAT via cogen gas    - GAS RE Imp.     ===",cost_IND_COGEN_GAS_HEAT())