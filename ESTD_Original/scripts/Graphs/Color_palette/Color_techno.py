import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# 1) Liste complète de vos codes “Technologies param”
technos = [
    'NUCLEAR', 'CCGT', 'CCGT_AMMONIA', 'COAL_US', 'COAL_IGCC', 'PV',
    'WIND_ONSHORE', 'WIND_OFFSHORE', 'HYDRO_RIVER', 'GEOTHERMAL',
    'IND_COGEN_GAS', 'IND_COGEN_WOOD', 'IND_COGEN_WASTE',
    'IND_BOILER_GAS', 'IND_BOILER_WOOD', 'IND_BOILER_OIL',
    'IND_BOILER_COAL', 'IND_BOILER_WASTE', 'IND_DIRECT_ELEC',
    'DHN_HP_ELEC', 'DHN_COGEN_GAS', 'DHN_COGEN_WOOD',
    'DHN_COGEN_WASTE', 'DHN_COGEN_WET_BIOMASS',
    'DHN_COGEN_BIO_HYDROLYSIS', 'DHN_BOILER_GAS', 'DHN_BOILER_WOOD',
    'DHN_BOILER_OIL', 'DHN_DEEP_GEO', 'DHN_SOLAR',
    'DEC_HP_ELEC', 'DEC_THHP_GAS', 'DEC_COGEN_GAS', 'DEC_COGEN_OIL',
    'DEC_ADVCOGEN_GAS', 'DEC_ADVCOGEN_H2', 'DEC_BOILER_GAS',
    'DEC_BOILER_WOOD', 'DEC_BOILER_OIL', 'DEC_SOLAR',
    'DEC_DIRECT_ELEC', 'TRAMWAY_TROLLEY', 'BUS_COACH_DIESEL',
    'BUS_COACH_HYDIESEL', 'BUS_COACH_CNG_STOICH',
    'BUS_COACH_FC_HYBRIDH2', 'TRAIN_PUB', 'CAR_GASOLINE',
    'CAR_DIESEL', 'CAR_NG', 'CAR_METHANOL', 'CAR_HEV',
    'CAR_PHEV', 'CAR_BEV', 'CAR_FUEL_CELL', 'TRAIN_FREIGHT',
    'BOAT_FREIGHT_DIESEL', 'BOAT_FREIGHT_NG',
    'BOAT_FREIGHT_METHANOL', 'TRUCK_DIESEL', 'TRUCK_METHANOL',
    'TRUCK_FUEL_CELL', 'TRUCK_ELEC', 'TRUCK_NG', 'EFFICIENCY',
    'DHN', 'GRID', 'H2_ELECTROLYSIS', 'SMR', 'H2_BIOMASS',
    'GASIFICATION_SNG', 'SYN_METHANATION', 'BIOMETHANATION',
    'BIO_HYDROLYSIS', 'PYROLYSIS_TO_LFO', 'PYROLYSIS_TO_FUELS',
    'ATM_CCS', 'INDUSTRY_CCS', 'SYN_METHANOLATION',
    'METHANE_TO_METHANOL', 'BIOMASS_TO_METHANOL', 'HABER_BOSCH',
    'AMMONIA_TO_H2', 'OIL_TO_HVC', 'GAS_TO_HVC', 'BIOMASS_TO_HVC',
    'METHANOL_TO_HVC', 'BATT_LI', 'BEV_BATT', 'PHEV_BATT', 'PHS',
    'TS_DEC_DIRECT_ELEC', 'TS_DEC_HP_ELEC', 'TS_DEC_THHP_GAS',
    'TS_DEC_COGEN_GAS', 'TS_DEC_COGEN_OIL', 'TS_DEC_ADVCOGEN_GAS',
    'TS_DEC_ADVCOGEN_H2', 'TS_DEC_BOILER_GAS',
    'TS_DEC_BOILER_WOOD', 'TS_DEC_BOILER_OIL',
    'TS_DHN_DAILY', 'TS_DHN_SEASONAL', 'TS_HIGH_TEMP',
    'GAS_STORAGE', 'H2_STORAGE', 'DIESEL_STORAGE',
    'GASOLINE_STORAGE', 'LFO_STORAGE', 'AMMONIA_STORAGE',
    'METHANOL_STORAGE', 'CO2_STORAGE'
]

# 2) Rassemble plusieurs colormaps qualitatives
cmaps = [plt.cm.tab20, plt.cm.tab20b, plt.cm.tab20c]

# 3) Génère une couleur par techno en enchaînant les cmaps
colors = []
for cmap in cmaps:
    n = cmap.N  # nombre de couleurs disponibles dans cette colormap
    for i in range(n):
        colors.append(mcolors.to_hex(cmap(i)))
# on tronque à la longueur de la liste de technos
colors = colors[:len(technos)]

# 4) On assemble le dictionnaire
color_palette = {tech: col for tech, col in zip(technos, colors)}

# Affichage rapide
import pprint; pprint.pprint(color_palette)
