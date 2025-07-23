# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import shutil
import energyscope as es

# === PARAMÈTRES ===
methanol_gwps = [0.22, 0.23, 0.24, 0.25]
h2_gwps = [round(i * 0.05, 3) for i in range(0, 8)]  # 0.00 → 0.30

# === CHEMINS ===
root = Path(__file__).resolve().parent.parent.parent
base_data_dir = root / "Data" / "2050"
td_base_case = root / "case_studies" / "base_TD"
config_path = root / "scripts" / "config_ref.yaml"

# === FONCTION POUR UN SCÉNARIO AVEC NOUVEAUX GWP_OP ===
def run_scenario(g_meth, g_h2):
    scenario_name = f"meth{g_meth:.3f}_h2{g_h2:.3f}"
    print(f"[▶] {scenario_name}...")

    scenario_data_dir = root / "Data" / scenario_name
    scenario_case_dir = root / "case_studies" / scenario_name
    scenario_data_dir.mkdir(parents=True, exist_ok=True)
    scenario_case_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Copier les données de base
        shutil.copytree(base_data_dir, scenario_data_dir, dirs_exist_ok=True)

        # 2. Modifier les valeurs de gwp_op dans Resources.csv
        resources_path = scenario_data_dir / "Resources.csv"
        df = pd.read_csv(resources_path, sep=';', skiprows=2)
        df.columns = df.columns.str.strip()
        df.loc[df['parameter name'] == 'METHANOL_RE', 'gwp_op'] = g_meth
        df.loc[df['parameter name'] == 'H2_RE', 'gwp_op'] = g_h2
        with open(resources_path, 'w', encoding='utf-8') as f:
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

        # 5. Ajouter log_file
        config.setdefault("ampl_options", {})
        config["ampl_options"]["log_file"] = str((scenario_case_dir / "output" / "log.txt").as_posix())

        # 6. Nettoyage
        output_dir = scenario_case_dir / "output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()

        for file in scenario_case_dir.glob("*.run"):
            file.unlink()
        dat_file = scenario_case_dir / "ESTD_data.dat"
        if dat_file.exists():
            dat_file.unlink()

        # 7. Importer, générer, run
        es.import_data(config)
        es.print_data(config)
        es.run_es(config)

        # 8. Sauvegarde des résultats
        output_dst = root / f"RESULTS_{scenario_name}"
        output_dst.mkdir(exist_ok=True)
        for file in output_dir.glob("*.txt"):
            shutil.copy(file, output_dst / file.name)

        print(f"[✔] Terminé pour {scenario_name}")

    except Exception as e:
        print(f"[❌] Échec pour {scenario_name} → {e}")

# === SCRIPT PRINCIPAL ===
if __name__ == '__main__':
    for g_meth in methanol_gwps:
        for g_h2 in h2_gwps:
            run_scenario(g_meth, g_h2)
    print("[🎯] Tous les scénarios sont terminés.")
