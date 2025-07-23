# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import shutil
import energyscope as es

# === PARAMÈTRES ===
gwp_up = 1
gwp_down = 0.0
N_RUNS = 30
STEP = 0.02

# === CHEMINS ===
root = Path(__file__).resolve().parent.parent
base_data_dir = root / "Data" / "2050"
td_base_case = root / "case_studies" / "base_TD"
config_path = root / "scripts" / "config_ref.yaml"

# === FONCTION POUR CONSTRUIRE LES TD UNE FOIS ===
def generate_typical_days():
    print("[⏳] Construction des TD...")
    config = es.load_config(config_fn=str(config_path))
    config["Working_directory"] = str(td_base_case)
    config["case_study"] = "base_TD"
    config["print_data"] = True
    config["analysis_only"] = False
    es.import_data(config)
    es.build_td_of_days(config)
    es.print_data(config)
    print("[✅] TD générés.")

# === FONCTION POUR UN SCÉNARIO AVEC NOUVEAU gwp_op ===
def run_scenario(run_idx):
    new_gwp = round(run_idx * STEP, 3)
    new_gwp += gwp_down
    name_value = new_gwp
    scenario_name = f"H2_RE_gwp_{name_value:.3f}"
    print(f"[▶] {scenario_name}...")

    scenario_data_dir = root / "Data" / scenario_name
    scenario_case_dir = root / "case_studies" / scenario_name
    scenario_data_dir.mkdir(parents=True, exist_ok=True)
    scenario_case_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Copier les données de base
        shutil.copytree(base_data_dir, scenario_data_dir, dirs_exist_ok=True)

        # 2. Modifier les valeurs de gwp_op dans Resources.csv
        scenario_resources_fn = scenario_data_dir / "Resources.csv"
        df = pd.read_csv(scenario_resources_fn, sep=';', skiprows=2)
        df.columns = df.columns.str.strip()
        targets = ['H2_RE'] #['METHANOL_RE', 'AMMONIA_RE', 'H2_RE', 'GAS_RE', 'BIOETHANOL', 'BIODIESEL']
        df.loc[df['parameter name'].isin(targets), 'gwp_op'] = new_gwp
        with open(scenario_resources_fn, 'w', encoding='utf-8') as f:
            f.write(";;;Availability;Direct and indirect emissions;Price;\n")
            f.write(";;units;[GWh/y];[ktCO2-eq./GWh];[Meuro/GWh];\n")
            df.to_csv(f, sep=';', index=False)

        # 3. Copier le fichier de TD
        shutil.copy(td_base_case / "ESTD_12TD.dat", scenario_case_dir / "ESTD_12TD.dat")

        # 4. Charger la configuration
        config = es.load_config(config_fn=str(config_path))
        config["case_study"] = scenario_name
        config["Working_directory"] = str(scenario_case_dir)
        config["data_dir"] = Path(scenario_data_dir)
        config["print_data"] = True

        # 🛠 Ajouter log_file explicitement dans ampl_options
        config.setdefault("ampl_options", {})
        config["ampl_options"]["log_file"] = str((scenario_case_dir / "output" / "log.txt").as_posix())

        # 5. Nettoyage et création du dossier output
        output_dir = scenario_case_dir / "output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()

        for file in scenario_case_dir.glob("*.run"):
            file.unlink()
        dat_file = scenario_case_dir / "ESTD_data.dat"
        if dat_file.exists():
            dat_file.unlink()

        # 6. Importer les données, générer les .dat/.run
        es.import_data(config)
        es.print_data(config)

        # 7. Lancer EnergyScope
        es.run_es(config)

        # 8. Sauvegarde des résultats
        output_dst = root / f"RESULTS_gwp_{name_value:.3f}"
        output_dst.mkdir(exist_ok=True)
        for file in output_dir.glob("*.txt"):
            shutil.copy(file, output_dst / file.name)

        print(f"[✔] Terminé pour {scenario_name}")

    except Exception as e:
        print(f"[❌] Échec pour {scenario_name} → {e}")

# === SCRIPT PRINCIPAL ===
if __name__ == '__main__':
    # generate_typical_days()
    for i in range(N_RUNS):
        run_scenario(i)
    print("[🎯] Tous les scénarios sont terminés.")
