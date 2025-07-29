# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import shutil
import energyscope as es

# === PARAMÈTRES ===
gwp_gas_range = [0.000, 0.025, 0.050, 0.075, 0.100, 0.125, 0.150]
gwp_ammonia_min = 0.000
gwp_ammonia_max = 0.15
N_AMMONIA_STEPS = 5
STEP_AMMONIA = (gwp_ammonia_max - gwp_ammonia_min) / (N_AMMONIA_STEPS - 1)

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

# === FONCTION POUR UN SCÉNARIO AVEC GWP GAS ET GWP AMMONIA ===
def run_scenario(gwp_gas, gwp_ammonia):
    scenario_name = f"GAS_{gwp_gas:.3f}_AMMONIA_{gwp_ammonia:.3f}"
    print(f"[▶] {scenario_name}...")

    scenario_data_dir = root / "Data" / scenario_name
    scenario_case_dir = root / "case_studies" / scenario_name
    scenario_data_dir.mkdir(parents=True, exist_ok=True)
    scenario_case_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Copier les données de base
        shutil.copytree(base_data_dir, scenario_data_dir, dirs_exist_ok=True)

        # 2. Modifier Resources.csv
        scenario_resources_fn = scenario_data_dir / "Resources.csv"
        df = pd.read_csv(scenario_resources_fn, sep=';', skiprows=2)
        df.columns = df.columns.str.strip()
        df.loc[df['parameter name'] == 'GAS_RE', 'gwp_op'] = gwp_gas
        df.loc[df['parameter name'] == 'AMMONIA_RE', 'gwp_op'] = gwp_ammonia
        with open(scenario_resources_fn, 'w', encoding='utf-8') as f:
            f.write(";;;Availability;Direct and indirect emissions;Price;\n")
            f.write(";;units;[GWh/y];[ktCO2-eq./GWh];[Meuro/GWh];\n")
            df.to_csv(f, sep=';', index=False)

        # 3. Copier fichier TD
        shutil.copy(td_base_case / "ESTD_12TD.dat", scenario_case_dir / "ESTD_12TD.dat")

        # 4. Charger config
        config = es.load_config(config_fn=str(config_path))
        config["case_study"] = scenario_name
        config["Working_directory"] = str(scenario_case_dir)
        config["data_dir"] = Path(scenario_data_dir)
        config["print_data"] = True
        config.setdefault("ampl_options", {})
        config["ampl_options"]["log_file"] = str((scenario_case_dir / "output" / "log.txt").as_posix())

        # 5. Nettoyage dossier output
        output_dir = scenario_case_dir / "output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()
        for file in scenario_case_dir.glob("*.run"):
            file.unlink()
        dat_file = scenario_case_dir / "ESTD_data.dat"
        if dat_file.exists():
            dat_file.unlink()

        # 6. Import et run
        es.import_data(config)
        es.print_data(config)
        es.run_es(config)

        # 7. Sauvegarde résultats
        output_dst = root / f"RESULTS_GAS_{gwp_gas:.3f}_AMMONIA_{gwp_ammonia:.3f}"
        output_dst.mkdir(exist_ok=True)
        for file in output_dir.glob("*.txt"):
            shutil.copy(file, output_dst / file.name)

        print(f"[✔] Terminé pour {scenario_name}")

    except Exception as e:
        print(f"[❌] Échec pour {scenario_name} → {e}")

# === SCRIPT PRINCIPAL ===
if __name__ == '__main__':
    # generate_typical_days()
    for gwp_gas in gwp_gas_range:
        for i in range(N_AMMONIA_STEPS):
            gwp_ammonia = round(gwp_ammonia_min + i * STEP_AMMONIA, 3)
            run_scenario(gwp_gas, gwp_ammonia)
    print("[🎯] Tous les scénarios sont terminés.")
