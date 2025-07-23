# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model

@author: Paolo Thiran, Matija Pavičević, Xavier Rixhon, Gauthier Limpens
"""

import os
from pathlib import Path
import energyscope as es
import matplotlib.pyplot as plt     # ← Ajouté


if __name__ == '__main__':
    analysis_only = False
    compute_TDs = True

    # loading the config file into a python dictionnary
    config = es.load_config(config_fn='config_ref.yaml')
    config['Working_directory'] = os.getcwd() # keeping current working directory into config
    
   # Reading the data of the csv
    es.import_data(config)

    if compute_TDs:
        es.build_td_of_days(config)
   
    if not analysis_only:
        # Printing the .dat files for the optimisation problem       
        es.print_data(config)

        # Running EnergyScope
        es.run_es(config)

    # # Example to print the sankey from this script
    # if config['print_sankey']:
    #     sankey_path = config['cs_path']/ config['case_study'] / 'output' / 'sankey'
    #     es.drawSankey(path=sankey_path)

        # Exemple pour tracer et sauvegarder le Sankey
    if config.get('print_sankey', False):
        # 1. Préparez le dossier de sortie
        sankey_path = Path(config['cs_path']) / config['case_study'] / 'output' / 'sankey'
        sankey_path.mkdir(parents=True, exist_ok=True)
        # 2. Tracé du Sankey (dans la figure active)
        es.drawSankey(path=sankey_path)

        # 3. Récupération de la figure active et sauvegarde
        fig = plt.gcf()                    # get current figure
        fig.tight_layout()                 # ajuste les marges
        fig.savefig(sankey_path / 'sankey.png', dpi=300)  # enregistre en 300 dpi
        plt.close(fig)                     # ferme la figure

    # Reading outputs
    outputs = es.read_outputs(config['case_study'], hourly_data=True, layers=['layer_ELECTRICITY','layer_HEAT_LOW_T_DECEN'])

    # Plots (examples)
    # primary resources used
    fig2, ax2 = es.plot_barh(outputs['resources_breakdown'][['Used']], title='Primary energy [GWh/y]')
    # elec assets
    elec_assets = es.get_assets_l(layer='ELECTRICITY', eff_tech=config['all_data']['Layers_in_out'],
                                  assets=outputs['assets'])
    fig3, ax3 = es.plot_barh(elec_assets[['f']], title='Electricity assets [GW_e]',
                             x_label='Installed capacity [GW_e]')
    # layer_ELECTRICITY for the 12 tds
    elec_layer_plot = es.plot_layer_elec_td(outputs['layer_ELECTRICITY'])
    # layer_HEAT_LOW_T_DECEN for the 12 tds
    fig,ax = es.hourly_plot(plotdata=outputs['layer_HEAT_LOW_T_DECEN'], nbr_tds=12)
    
    
    
