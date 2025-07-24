import csv

# Dictionnaire des ressources et leurs couleurs
color_palette = {
    "ELECTRICITY": "#00BFFF",
    "GASOLINE": "#A0522D",
    "DIESEL": "#D3D3D3",
    "BIOETHANOL": "#8FBC8F",
    "BIODIESEL": "#D3D3D3",
    "LFO": "#BC8F8F",
    "GAS": "#FFD700",
    "GAS_RE": "#FFD700",
    "WOOD": "#CD853F",
    "WET_BIOMASS": "#CD853F",
    "COAL": "#2F4F4F",
    "URANIUM": "#708090",
    "WASTE": "#808000",
    "H2": "#FF00FF",
    "H2_RE": "#FF00FF",
    "AMMONIA": "#000ECD",
    "METHANOL": "#CC0066",
    "AMMONIA_RE": "#000ECD",
    "METHANOL_RE": "#CC0066",
    "ELEC_EXPORT": "#00BFFF",
    "CO2_EMISSIONS": "#696969",
    "RES_WIND": "#27AE34",
    "RES_SOLAR": "#FFFF00",
    "RES_HYDRO": "#0000FF",
    "RES_GEO": "#FF8C00",
    "CO2_ATM": "#708090",
    "CO2_INDUSTRY": "#A9A9A9",
    "CO2_CAPTURED": "#32CD32"
}

# Écriture dans un fichier CSV
with open("resource_color_palette.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Resource", "Color"])
    for resource, color in color_palette.items():
        writer.writerow([resource, color])

print("✅ Fichier 'resource_color_palette.csv' généré avec succès.")
