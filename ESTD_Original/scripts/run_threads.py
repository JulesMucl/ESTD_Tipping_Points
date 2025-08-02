

# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import shutil
import energyscope as es



# === CHEMINS ===
root = Path(__file__).resolve().parent.parent
base_data_dir = root / "Data" / "2050"
td_base_case = root / "case_studies" / "base_TD"
config_path = root / "scripts" / "config_ref.yaml"


config = {

    'NUCLEAR': True,  # Utiliser le nucléaire dans le scénario

    'NAME': "BIOETHANOL_RE_ONLY_NUCLEAR",  # Nom du scénario

    'ONLY': True,

    "gwp_range_num": [round(i * 0.05, 3) for i in range(0, 6,2)],    

    "gwp_range_denum": 0, #[round(i * 0.01, 3) for i in range(40,60,5)],

    "gwp_range_other_fuels": 0, #[round(i * 0.01, 3) for i in range(70, 90, 5)],



}



# === FONCTION POUR UN SCÉNARIO AVEC NOUVEAU GWP_OP ===
def run_scenario(gwp_other_fuel, gwp_num, gwp_denum,config=config):
    NAME = config['NAME']
    if config['ONLY']:
        scenario_name = f"{NAME}_{gwp_num:.3f}"

    else:
        scenario_name = f"{NAME}__{gwp_num:.3f}_vs_{gwp_denum:.3f}"

    print(f"[▶] {scenario_name}...")

    scenario_data_dir = root / "Data" / scenario_name
    if config['NUCLEAR']:
        if config['ONLY']:
            scenario_case_dir = root / "case_studies" / "NUCLEAR" / "ONLY" /  NAME /"log" /scenario_name
        else:
            scenario_case_dir = root / "case_studies" / "NUCLEAR" / "RATIO" /  NAME /"log" / scenario_name

    else:
        scenario_case_dir = root / "case_studies" / "NON_NUCLEAR" /  NAME /"log" /scenario_name
    scenario_data_dir.mkdir(parents=True, exist_ok=True)
    scenario_case_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Copier les données de base
        shutil.copytree(base_data_dir, scenario_data_dir, dirs_exist_ok=True)

        # 2. Modifier les valeurs de gwp_op dans Resources.csv
        scenario_resources_fn = scenario_data_dir / "Resources.csv"
        df = pd.read_csv(scenario_resources_fn, sep=';', skiprows=2)
        df.columns = df.columns.str.strip()
        #---------------------------------------------------------------------------------------------------------00000000000000000000

        df.loc[df['parameter name'] == 'H2_RE', 'gwp_op']       = gwp_other_fuel
        df.loc[df['parameter name'] == 'METHANOL_RE', 'gwp_op'] = gwp_other_fuel
        df.loc[df['parameter name'] == 'BIODIESEL', 'gwp_op']   = gwp_other_fuel
        df.loc[df['parameter name'] == 'BIOETHANOL', 'gwp_op']  = gwp_num 
        df.loc[df['parameter name'] == 'AMMONIA_RE', 'gwp_op']  = gwp_other_fuel
        df.loc[df['parameter name'] == 'GAS_RE', 'gwp_op']      = gwp_other_fuel
        #---------------------------------------------------------------------------------------------------------00000000000000000000

        with open(scenario_resources_fn, 'w', encoding='utf-8') as f:
            f.write(";;;Availability;Direct and indirect emissions;Price;\n")
            f.write(";;units;[GWh/y];[ktCO2-eq./GWh];[Meuro/GWh];\n")
            df.to_csv(f, sep=';', index=False)

        # 3. Copier les TD
        shutil.copy(td_base_case / "ESTD_12TD.dat", scenario_case_dir / "ESTD_12TD.dat")
        
        # 5. Nettoyage output
        output_dir = scenario_case_dir / "output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()


        # 4. Charger config
        config = es.load_config(config_fn=str(config_path))
        config["case_study"] = scenario_name
        config["Working_directory"] = str(scenario_case_dir)
        config["data_dir"] = Path(scenario_data_dir)
        config["print_data"] = True

        config.setdefault("ampl_options", {})
        config["ampl_options"]["log_file"] = str((scenario_case_dir / "output" / "log.txt").as_posix())


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
        # output_dst = root / f"RESULTS__{NAME}"
        # output_dst.mkdir(exist_ok=True)
        # for file in output_dir.glob("*.txt"):
        #     shutil.copy(file, output_dst / file.name)

        print(f"[✔] Terminé pour {scenario_name}")

    except Exception as e:
        print(f"[❌] Échec pour {scenario_name} → {e}")

# === SCRIPT PRINCIPAL ===
if __name__ == '__main__':
    # generate_typical_days()  # Décommenter si nécessaire
    if config['gwp_range_num'] == 0:
        print("[❌] Aucune valeur dans gwp_range_num, veuillez vérifier la configuration.")
        
    
    if config['gwp_range_other_fuels'] == 0:

        if config['gwp_range_denum'] == 0:
            for gwp_num in config['gwp_range_num']:
                run_scenario(gwp_other_fuel=0, gwp_num=gwp_num, gwp_denum=0)

        else:
            for gwp_denum in config['gwp_range_denum']:
                for gwp_num in config['gwp_range_num']:
                    run_scenario(gwp_other_fuel=0, gwp_num=gwp_num, gwp_denum=gwp_denum)


    else:
        for gwp_other_fuel in config['gwp_range_other_fuels']:
            for gwp_denum in config['gwp_range_denum']:
                for gwp_num in config['gwp_range_num']:
                    
                    run_scenario(gwp_other_fuel=gwp_other_fuel, gwp_num=gwp_num, gwp_denum=gwp_denum)
 

    print("[🎯] Tous les scénarios sont terminés.")
    print("🎉🎉🎉 Let's go! You're amazing! 😄 🚀 😁 🎯")
    print("😄 😁 😊 🤩 😎 🥳 😃 😸 🎉 💫 🌟 ✨ 🙌 ❤️")
    print("🎉🎉🎉")





# === FIN DU SCRIPT ===