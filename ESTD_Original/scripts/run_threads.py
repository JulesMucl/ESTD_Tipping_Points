
# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import shutil
import energyscope as es

# === PARAMÈTRES GWP ===
gwp_range_main = [round(i * 0.015, 3) for i in range(0, 20)]  # GAS_RE & AMMONIA_RE: 0 → 0.4
gwp_range_h2 = [round(i * 0.015, 3) for i in range(0, 20)]     # H2_RE: 0 → 0.4

# === CHEMINS ===
root = Path(__file__).resolve().parent.parent
base_data_dir = root / "Data" / "2050"
td_base_case = root / "case_studies" / "base_TD"
config_path = root / "scripts" / "config_ref.yaml"

# === FONCTION POUR UN SCÉNARIO AVEC NOUVEAU GWP_OP ===
def run_scenario(gwp_main, gwp_h2):
    scenario_name = f"GAS&AMMONIA_vs_H2_gas&ammo_{gwp_main:.3f}_h2_{gwp_h2:.3f}"
    print(f"[▶] {scenario_name}...")





    scenario_data_dir = root / "Data" / scenario_name
    scenario_case_dir = root / "case_studies" / "RATIO" / "Gas&Ammonia_vs_H2" /scenario_name
    scenario_data_dir.mkdir(parents=True, exist_ok=True)
    scenario_case_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Copier les données de base
        shutil.copytree(base_data_dir, scenario_data_dir, dirs_exist_ok=True)

        # 2. Modifier les valeurs de gwp_op dans Resources.csv
        scenario_resources_fn = scenario_data_dir / "Resources.csv"
        df = pd.read_csv(scenario_resources_fn, sep=';', skiprows=2)
        df.columns = df.columns.str.strip()

        df.loc[df['parameter name'] == 'GAS_RE', 'gwp_op'] = gwp_main
        df.loc[df['parameter name'] == 'AMMONIA_RE', 'gwp_op'] = gwp_main
        df.loc[df['parameter name'] == 'H2_RE', 'gwp_op'] = gwp_h2

        with open(scenario_resources_fn, 'w', encoding='utf-8') as f:
            f.write(";;;Availability;Direct and indirect emissions;Price;\n")
            f.write(";;units;[GWh/y];[ktCO2-eq./GWh];[Meuro/GWh];\n")
            df.to_csv(f, sep=';', index=False)

        # 3. Copier les TD
        shutil.copy(td_base_case / "ESTD_12TD.dat", scenario_case_dir / "ESTD_12TD.dat")

        # 4. Charger config
        config = es.load_config(config_fn=str(config_path))
        config["case_study"] = scenario_name
        config["Working_directory"] = str(scenario_case_dir)
        config["data_dir"] = Path(scenario_data_dir)
        config["print_data"] = True

        config.setdefault("ampl_options", {})
        config["ampl_options"]["log_file"] = str((scenario_case_dir / "output" / "log.txt").as_posix())

        # 5. Nettoyage output
        output_dir = scenario_case_dir / "output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()

        for file in scenario_case_dir.glob("*.run"):
            file.unlink()
        dat_file = scenario_case_dir / "ESTD_data.dat"
        if dat_file.exists():
            dat_file.unlink()

        # 6. Importation + génération .dat/.run
        es.import_data(config)
        es.print_data(config)

        # 7. Run EnergyScope
        es.run_es(config)

        # 8. Copie des résultats
        output_dst = root / f"RESULTS_gas_{gwp_main:.3f}_h2_{gwp_h2:.3f}"
        output_dst.mkdir(exist_ok=True)
        for file in output_dir.glob("*.txt"):
            shutil.copy(file, output_dst / file.name)

        print(f"[✔] Terminé pour {scenario_name}")

    except Exception as e:
        print(f"[❌] Échec pour {scenario_name} → {e}")

# === SCRIPT PRINCIPAL ===
if __name__ == '__main__':
    # generate_typical_days()  # Décommenter si nécessaire

    for gwp_main in gwp_range_main:
        for gwp_h2 in gwp_range_h2:
            run_scenario(gwp_main, gwp_h2)

    print("[🎯] Tous les scénarios sont terminés.")
































# # -*- coding: utf-8 -*-
# from pathlib import Path
# import pandas as pd
# import shutil
# import energyscope as es

# # === PARAMÈTRES ===
# gwp_up = 1
# gwp_down = 0
# N_RUNS = 15
# STEP = 0.002

# # === CHEMINS ===
# root = Path(__file__).resolve().parent.parent
# base_data_dir = root / "Data" / "2050"
# td_base_case = root / "case_studies" / "base_TD"
# config_path = root / "scripts" / "config_ref.yaml"

# # === FONCTION POUR CONSTRUIRE LES TD UNE FOIS ===
# def generate_typical_days():
#     print("[⏳] Construction des TD...")
#     config = es.load_config(config_fn=str(config_path))
#     config["Working_directory"] = str(td_base_case)
#     config["case_study"] = "base_TD"
#     config["print_data"] = True
#     config["analysis_only"] = False
#     es.import_data(config)
#     es.build_td_of_days(config)
#     es.print_data(config)
#     print("[✅] TD générés.")

# # === FONCTION POUR UN SCÉNARIO AVEC NOUVEAU gwp_op ===
# def run_scenario(run_idx):
#     new_gwp = round(run_idx * STEP, 3)
#     new_gwp += gwp_down
#     name_value = new_gwp
#     scenario_name = f"GAS_vs_Ammonia_3_gwp_{name_value:.3f}"
#     print(f"[▶] {scenario_name}...")

#     scenario_data_dir = root / "Data" / scenario_name
#     scenario_case_dir = root / "case_studies" / scenario_name
#     scenario_data_dir.mkdir(parents=True, exist_ok=True)
#     scenario_case_dir.mkdir(parents=True, exist_ok=True)

#     try:
#         # 1. Copier les données de base
#         shutil.copytree(base_data_dir, scenario_data_dir, dirs_exist_ok=True)

#         # 2. Modifier les valeurs de gwp_op dans Resources.csv
#         scenario_resources_fn = scenario_data_dir / "Resources.csv"
#         df = pd.read_csv(scenario_resources_fn, sep=';', skiprows=2)
#         df.columns = df.columns.str.strip()
#         targets = ['AMMONIA_RE'] #['METHANOL_RE', 'AMMONIA_RE', 'H2_RE', 'GAS_RE', 'BIOETHANOL', 'BIODIESEL']
#         df.loc[df['parameter name'].isin(targets), 'gwp_op'] = new_gwp
#         targets_fixed = ['GAS_RE'] #['METHANOL_RE', 'AMMONIA_RE', 'H2_RE', 'GAS_RE', 'BIOETHANOL', 'BIODIESEL']
#         df.loc[df['parameter name'].isin(targets_fixed), 'gwp_op'] = 0.075
#         with open(scenario_resources_fn, 'w', encoding='utf-8') as f:
#             f.write(";;;Availability;Direct and indirect emissions;Price;\n")
#             f.write(";;units;[GWh/y];[ktCO2-eq./GWh];[Meuro/GWh];\n")
#             df.to_csv(f, sep=';', index=False)

#         # 3. Copier le fichier de TD
#         shutil.copy(td_base_case / "ESTD_12TD.dat", scenario_case_dir / "ESTD_12TD.dat")

#         # 4. Charger la configuration
#         config = es.load_config(config_fn=str(config_path))
#         config["case_study"] = scenario_name
#         config["Working_directory"] = str(scenario_case_dir)
#         config["data_dir"] = Path(scenario_data_dir)
#         config["print_data"] = True

#         # 🛠 Ajouter log_file explicitement dans ampl_options
#         config.setdefault("ampl_options", {})
#         config["ampl_options"]["log_file"] = str((scenario_case_dir / "output" / "log.txt").as_posix())

#         # 5. Nettoyage et création du dossier output
#         output_dir = scenario_case_dir / "output"
#         if output_dir.exists():
#             shutil.rmtree(output_dir)
#         output_dir.mkdir()

#         for file in scenario_case_dir.glob("*.run"):
#             file.unlink()
#         dat_file = scenario_case_dir / "ESTD_data.dat"
#         if dat_file.exists():
#             dat_file.unlink()

#         # 6. Importer les données, générer les .dat/.run
#         es.import_data(config)
#         es.print_data(config)

#         # 7. Lancer EnergyScope
#         es.run_es(config)

#         # 8. Sauvegarde des résultats
#         output_dst = root / f"RESULTS_gwp_{name_value:.3f}"
#         output_dst.mkdir(exist_ok=True)
#         for file in output_dir.glob("*.txt"):
#             shutil.copy(file, output_dst / file.name)

#         print(f"[✔] Terminé pour {scenario_name}")

#     except Exception as e:
#         print(f"[❌] Échec pour {scenario_name} → {e}")

# # === SCRIPT PRINCIPAL ===
# if __name__ == '__main__':
#     # generate_typical_days()
#     for i in range(N_RUNS):
#         run_scenario(i)
#     print("[🎯] Tous les scénarios sont terminés.")
