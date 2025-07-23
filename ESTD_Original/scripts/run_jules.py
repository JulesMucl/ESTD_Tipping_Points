#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to automate multiple EnergyScope runs with varying GWP_limit.
Generates 10 scenarios from 100000 ktCO2-eq./year to 5000 ktCO2-eq./year.
"""

import os
from pathlib import Path
import numpy as np
import energyscope as es
import matplotlib.pyplot as plt


def run_scenario(gwp):
    # Load base config
    config = es.load_config('config_ref.yaml')
    # Override parameters
    config['GWP_limit'] = gwp
    config['case_study'] = f'Scenario_emissions_{gwp}'
    config['Working_directory'] = os.getcwd()

    # Import data and build typical days
    es.import_data(config)
    es.build_td_of_days(config)

    # Print data and run model
    es.print_data(config)
    es.run_es(config)

    # Optional: generate Sankey diagram if enabled
    if config.get('print_sankey', False):
        sankey_path = Path(config['cs_path']) / config['case_study'] / 'output' / 'sankey'
        sankey_path.mkdir(parents=True, exist_ok=True)
        es.drawSankey(path=sankey_path)
        fig = plt.gcf()
        fig.tight_layout()
        fig.savefig(sankey_path / 'sankey.png', dpi=300)
        plt.close(fig)

    # Read outputs (optional return for further analysis)
    outputs = es.read_outputs(
        config['case_study'],
        hourly_data=True,
        layers=['layer_ELECTRICITY', 'layer_HEAT_LOW_T_DECEN']
    )
    return outputs


if __name__ == '__main__':
    # Generate 10 emission limits from 100000 down to 5000 ktCO2-eq./year
    gwp_values = [int(v) for v in np.linspace(100000, 5000, 10)]

    for gwp in gwp_values:
        print(f'Running scenario with GWP_limit = {gwp} ktCO2-eq./year')
        run_scenario(gwp)

    print('All scenarios completed.')













# # -*- coding: utf-8 -*-
# """
# This script modifies the input data and runs the EnergyScope model
# for N runs by changing the gwp_op value of METHANOL_RE.
# """

# import os
# from pathlib import Path
# import pandas as pd
# import energyscope as es

# if __name__ == '__main__':
#     analysis_only = False
#     compute_TDs = True
#     N_RUNS = 5
#     STEP = 0.1  # Increase in gwp_op per run [ktCO2-eq./GWh]

#     # Root path and Resources.csv
#     root = Path(__file__).resolve().parent.parent
#     resources_fn = root / "Data" / "2050" / "Resources.csv"

#     # Load base config
#     base_config = es.load_config(config_fn='config_ref.yaml')
#     opts = base_config['ampl_options'].get('gurobi_options', '')
#     base_config['ampl_options']['gurobi_options'] = opts + ' Threads=4'

#     # Backup original file (entire content)
#     with open(resources_fn, 'r', encoding='utf-8') as f:
#         original_lines = f.readlines()

#     # Load as dataframe: skip metadata + units
#     df_orig = pd.read_csv(resources_fn, sep=';', skiprows=2)
#     df_orig.columns = df_orig.columns.str.strip()

#     # Ensure 'Comment' exists
#     if 'Comment' not in df_orig.columns:
#         df_orig['Comment'] = ''

#     for run_idx in range(N_RUNS):
#         df = df_orig.copy()

#         # Get base value and compute new gwp_op
#         base_gwp = df.loc[df['parameter name'] == 'METHANOL_RE', 'gwp_op'].astype(float).iloc[0]
#         new_gwp = base_gwp + run_idx * STEP
#         df.loc[df['parameter name'] == 'METHANOL_RE', 'gwp_op'] = new_gwp

#         # Overwrite file, keeping original header lines
#         with open(resources_fn, 'w', encoding='utf-8') as f:
#             f.write(";;;Availability;Direct and indirect emissions;Price;\n")
#             f.write(";;units;[GWh/y];[ktCO2-eq./GWh];[Meuro/GWh];\n")
#             df.to_csv(f, sep=';', index=False)

#         # Prepare run
#         config = base_config.copy()
#         config['Working_directory'] = os.getcwd()
#         es.import_data(config)

#         if compute_TDs:
#             es.build_td_of_days(config)

#         if not analysis_only:
#             es.print_data(config)
#             es.run_es(config)

#         print(f"=== Run {run_idx} terminé avec METHANOL_RE gwp = {new_gwp:.3f} ===")

#     # Restore original file
#     with open(resources_fn, 'w', encoding='utf-8') as f:
#         f.writelines(original_lines)

#     print("Resources.csv restauré dans son état initial.")
