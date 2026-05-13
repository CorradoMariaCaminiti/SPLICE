# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 10:00:17 2026

@author: corra
"""

from onsset import *
from IPython.display import display, Markdown, HTML
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('run', 'funcs.ipynb')
get_ipython().run_line_magic('run', 'detailed_tech_parameters.ipynb')
import warnings
warnings.filterwarnings('ignore')
import time
import matplotlib.pylab as plt
import seaborn as sns
import pycountry
import yaml
from onsset.build_country_input import build_country_inputs
from onsset.detailed_tech_parameters import init_tech_info 
from onsset.funcs import run_scenario, finalize_results, save_variables, calc_summary_table
def run_onsset_scenario(countryy, coe, it, pypsaPath):
    config_path = os.path.join(pypsaPath, "config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    # Update name 
    country_prefix = config["run"]["name"].rsplit("_", 1)[0]
    scenario_name = f'{country_prefix}_{it}'
    
    inputs = build_country_inputs(countryy, coe) 
    globals().update(inputs)
    grid_vars = dict(zip(grid_params['Parameter'], grid_params['Value']))
    
    # Inject them as real variables
    globals().update(grid_vars)

    grid_calc, mg_pv_hybrid_calc, mg_wind_hybrid_calc, mg_hydro_calc, sa_pv_calc, sa_diesel_calc, mg_pv_hybrid_params, mg_wind_hybrid_params, mg_diesel_params, mg_interconnection, grid_reliability_option, cnse, grid_reliability = init_tech_info(grid_losses, grid_power_plants_capital_cost, grid_generation_cost, grid_discount_rate, grid_mv_line_capacity,
                       grid_MV_line_amperage_limit, grid_mv_line_cost, grid_lv_line_capacity, grid_lv_line_cost, grid_lv_line_max_length, 
                       grid_service_Transf_type, grid_service_Transf_cost, grid_max_nodes_per_serv_trans,
                       mini_grid_discount_rate, mg_mv_line_capacity, mg_MV_line_amperage_limit, mg_mv_line_cost, mg_lv_line_capacity, 
                       mg_lv_line_cost, mg_lv_line_max_length, mg_service_Transf_type, mg_service_Transf_cost, mg_max_nodes_per_serv_trans,
                       mg_hydro_capital_cost, shs_lifetime, standalone_discount_rate, sa_pv_capital_cost_1, sa_pv_capital_cost_2, sa_pv_capital_cost_3, 
                       sa_pv_capital_cost_4, sa_pv_capital_cost_5, min_mg_size, diesel_gen_cost, battery_cost, pv_life, diesel_life, inverter_cost,
                       inverter_life, lpsp_max, max_diesel, diesel_price, pv_cost, wind_cost)
    
    shares = {"Grid":0.70, "SA_PV":0.20, "MG_PVHybrid":0.05, "MG_Wind":0.02, "MG_Hydro":0.03}
    assign_shares = False
    priorities = ['MG_Hydro', 'MG_Wind', 'MG_PVHybrid']
    priority = False
    
    onsseter.df, new_lines_geojson = run_scenario(onsseter, end_year_pop, urban_ratio_end_year, start_year, end_year, yearsofanalysis, x_coordinates, y_coordinates, tier_1, 
                     tier_2, tier_3, tier_4, tier_5, hv_line_capacity, hv_line_cost, hv_mv_transformer_cost, hv_mv_transformer_type, eleclimits, time_steps, 
                     annual_new_grid_connections_limit, annual_grid_cap_gen_limit, num_people_per_hh_urban, num_people_per_hh_rural, urban_target_tier, 
                     rural_target_tier_large, rural_target_tier_small, rural_cutoff_size, mg_diesel_params, mg_wind_hybrid_params, wind_path, 
                     mg_pv_hybrid_params, pv_path, mg_hydro_calc, mg_wind_hybrid_calc, sa_pv_calc, mg_pv_hybrid_calc, min_mg_size, mg_min_grid_dist,
                     grid_generation_cost, grid_calc, sa_diesel_calc, max_grid_intensification_cost, auto_intensification, grid_mv_line_max_length, 
                     mg_interconnection, grid_reliability_option, cnse, grid_reliability, prio_choice, grid_emission_factor, shares, assign_shares, priorities,priority)
    
    
    finalize_results(onsseter, yearsofanalysis)
    
    output_dir = "output"
    output_dir_variables = os.path.join(output_dir, '{}_Variables.csv'.format(scenario_name))
    output_dir_results = os.path.join(output_dir, '{}_Results.csv'.format(scenario_name))
    output_dir_summaries = os.path.join(output_dir, '{}_Summaries.csv'.format(scenario_name))
    
    
    
    summary_table, columns = calc_summary_table(onsseter.df, yearsofanalysis)
    df_variables = save_variables(onsseter, start_year, end_year, end_electrification_rate_target, urban_target_tier, rural_target_tier_large,
                                  rural_target_tier_small, auto_intensification, max_grid_intensification_cost, end_year_pop, urban_ratio_end_year,
                                  grid_generation_cost, grid_power_plants_capital_cost, grid_losses, diesel_price, mg_hydro_capital_cost, min_mg_size,
                                  mg_min_grid_dist, mg_interconnection, pv_cost, battery_cost, inverter_cost, diesel_gen_cost, max_diesel, 
                                  sa_pv_capital_cost_1, sa_pv_capital_cost_2, sa_pv_capital_cost_3, sa_pv_capital_cost_4, sa_pv_capital_cost_5, 
                                  grid_mv_line_cost, grid_lv_line_cost, grid_mv_line_capacity, grid_lv_line_capacity, grid_lv_line_max_length, hv_line_cost, 
                                  grid_mv_line_max_length, annual_new_grid_connections_limit, annual_grid_cap_gen_limit, grid_discount_rate, 
                                  mini_grid_discount_rate, standalone_discount_rate)
    
    # Returning the result as a csv file
    onsseter.df.to_csv(output_dir_results, index=False)
    
    # Returning the summary as a csv file
    summary_table.to_csv(output_dir_summaries, index=True)
    
    # Returning the input variables as a csv file
    df_variables.to_csv(output_dir_variables, index=False)