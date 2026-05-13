#!/usr/bin/env python
# coding: utf-8

# In[1]:


#from onsset import *


# In[2]:

from onsset import *
def init_tech_info(grid_losses, grid_power_plants_capital_cost, grid_generation_cost, grid_discount_rate, grid_mv_line_capacity,
                   grid_MV_line_amperage_limit, grid_mv_line_cost, grid_lv_line_capacity, grid_lv_line_cost, grid_lv_line_max_length, 
                   grid_service_Transf_type, grid_service_Transf_cost, grid_max_nodes_per_serv_trans,
                   mini_grid_discount_rate, mg_mv_line_capacity, mg_MV_line_amperage_limit, mg_mv_line_cost, mg_lv_line_capacity, 
                   mg_lv_line_cost, mg_lv_line_max_length, mg_service_Transf_type, mg_service_Transf_cost, mg_max_nodes_per_serv_trans,
                   mg_hydro_capital_cost, shs_lifetime, standalone_discount_rate, sa_pv_capital_cost_1, sa_pv_capital_cost_2, sa_pv_capital_cost_3, 
                   sa_pv_capital_cost_4, sa_pv_capital_cost_5, min_mg_size, diesel_gen_cost, battery_cost, pv_life, diesel_life, inverter_cost,
                   inverter_life, lpsp_max, max_diesel, diesel_price, pv_cost, wind_cost):

    # Decide whether mini-grids should be allowed to be interconnected to the grid in a later time-step.
    mg_interconnection = 0         # 0 = NO, 1 = YES

    # Decide on factors regarding centralized grid reliability 
    grid_reliability_option = 'None' # Choose between 'None' and 'CNSE' (Cost of Non-Served Energy)
    cnse = 0.  # Value of non-served energy, USD/kWH
    grid_reliability = 1  # If using 'CNSE', specify the reliability of the grid, e.g. 0.9 means the grid can meet the demand for 90% of the annual load
    
    # Centralized grid costs
    grid_calc = Technology(om_of_td_lines=0.02,
                           distribution_losses=grid_losses,
                           connection_cost_per_hh=100,
                           capacity_factor=1,
                           tech_life=30,
                           grid_capacity_investment=grid_power_plants_capital_cost,
                           grid_price=grid_generation_cost,
                           discount_rate=grid_discount_rate,
                           mv_line_type=grid_mv_line_capacity,
                           mv_line_amperage_limit=grid_MV_line_amperage_limit, 
                           mv_line_cost=grid_mv_line_cost, 
                           lv_line_type=grid_lv_line_capacity, 
                           lv_line_cost=grid_lv_line_cost, 
                           lv_line_max_length=grid_lv_line_max_length, 
                           service_transf_type=grid_service_Transf_type, 
                           service_transf_cost=grid_service_Transf_cost,
                           max_nodes_per_serv_trans=grid_max_nodes_per_serv_trans,
                           cnse=cnse)
    
    mg_pv_hybrid_calc = Technology(om_of_td_lines=0.02,
                                   distribution_losses=0.05,
                                   connection_cost_per_hh=100,
                                   capacity_factor=0.5,
                                   tech_life=20,
                                   mini_grid=True,
                                   hybrid=True,
                                   discount_rate=mini_grid_discount_rate,
                                   mv_line_type=mg_mv_line_capacity,
                                   mv_line_amperage_limit=mg_MV_line_amperage_limit, 
                                   mv_line_cost=mg_mv_line_cost, 
                                   lv_line_type=mg_lv_line_capacity, 
                                   lv_line_cost=mg_lv_line_cost, 
                                   lv_line_max_length=mg_lv_line_max_length, 
                                   service_transf_type=mg_service_Transf_type, 
                                   service_transf_cost=mg_service_Transf_cost,
                                   max_nodes_per_serv_trans=mg_max_nodes_per_serv_trans)
    
    mg_wind_hybrid_calc = Technology(om_of_td_lines=0.02,
                                     distribution_losses=0.05,
                                     connection_cost_per_hh=100,
                                     capacity_factor=0.5,
                                     tech_life=20,
                                     mini_grid=True,
                                     hybrid=True,
                                     discount_rate=mini_grid_discount_rate,
                                     mv_line_type=mg_mv_line_capacity,
                                     mv_line_amperage_limit=mg_MV_line_amperage_limit, 
                                     mv_line_cost=mg_mv_line_cost, 
                                     lv_line_type=mg_lv_line_capacity, 
                                     lv_line_cost=mg_lv_line_cost, 
                                     lv_line_max_length=mg_lv_line_max_length, 
                                     service_transf_type=mg_service_Transf_type, 
                                     service_transf_cost=mg_service_Transf_cost,
                                     max_nodes_per_serv_trans=mg_max_nodes_per_serv_trans)
    
    # Mini-grid hydro costs
    mg_hydro_calc = Technology(om_of_td_lines=0.02,
                                distribution_losses=0.05,
                                connection_cost_per_hh=100,
                                capacity_factor=0.5,
                                tech_life=30,
                                capital_cost=mg_hydro_capital_cost,
                                om_costs=0.02,
                                discount_rate=mini_grid_discount_rate,
                                mv_line_type=mg_mv_line_capacity,
                                mv_line_amperage_limit=mg_MV_line_amperage_limit, 
                                mv_line_cost=mg_mv_line_cost, 
                                lv_line_type=mg_lv_line_capacity, 
                                lv_line_cost=mg_lv_line_cost, 
                                lv_line_max_length=mg_lv_line_max_length, 
                                service_transf_type=mg_service_Transf_type, 
                                service_transf_cost=mg_service_Transf_cost,
                                max_nodes_per_serv_trans=mg_max_nodes_per_serv_trans
                                )
    
    # Stand-alone PV costs
    sa_pv_calc = Technology(base_to_peak_load_ratio=0.9,
                            tech_life=shs_lifetime,
                            om_costs=0.05,
                            discount_rate=standalone_discount_rate,
                            capital_cost={0.020: sa_pv_capital_cost_1, 
                                          0.050: sa_pv_capital_cost_2, 
                                          0.100: sa_pv_capital_cost_3, 
                                          1: sa_pv_capital_cost_4, 
                                          float("inf"): sa_pv_capital_cost_5},
                            standalone=True
                            )
    
    mg_pv_hybrid_params = {
                    'min_mg_connections': min_mg_size,  # minimum number of households in settlement for mini-grids to be considered as an option
                    'diesel_cost': diesel_gen_cost,  # diesel generator capital cost, USD/kW rated power
                    'discount_rate': mini_grid_discount_rate,
                    'n_chg': 0.92,  # charge efficiency of battery
                    'n_dis': 0.92,  # discharge efficiency of battery
                    'battery_cost': battery_cost,  # battery capital cost, USD/kWh of storage capacity
                    'pv_cost': pv_cost,  # PV panel capital cost, USD/kW peak power
                    'charge_controller': 0,  # PV charge controller cost, USD/kW peak power, set to 0 if already included in pv_cost
                    'pv_inverter': 0,  # PV inverter cost, USD/kW peak power, set to 0 if already included in pv_cost
                    'pv_life': pv_life,  # PV panel expected lifetime, years
                    'diesel_life': diesel_life,  # diesel generator expected lifetime, years
                    'pv_om': 0.015,  # annual OM cost of PV panels
                    'diesel_om': 0.1,  # annual OM cost of diesel generator
                    'battery_inverter_cost': inverter_cost,
                    'battery_inverter_life': inverter_life,
                    'dod_max': 0.8,  # maximum depth of discharge of battery
                    'inv_eff': 0.93,  # inverter_efficiency
                    'lpsp_max': lpsp_max,  # maximum loss of load allowed over the year, in share of kWh
                    'diesel_limit': max_diesel,  # Max annual share of mini-grid generation from diesel gen-set
                    'full_life_cycles': 2000  # Equivalent full life-cycles of battery until replacement
                }
    
    mg_wind_hybrid_params = {
                    'min_mg_connections': min_mg_size,  # minimum number of households in settlement for mini-grids to be considered as an option
                    'diesel_cost': diesel_gen_cost,  # diesel generator capital cost, USD/kW rated power
                    'discount_rate': mini_grid_discount_rate,
                    'n_chg': 0.92,  # charge efficiency of battery
                    'n_dis': 0.92,  # discharge efficiency of battery
                    'battery_cost': battery_cost,  # battery capital cost, USD/kWh of storage capacity
                    'wind_cost': wind_cost,  # Wind turbine capital cost, USD/kW peak power
                    'charge_controller': 0,  # PV charge controller cost, USD/kW peak power, set to 0 if already included in pv_cost
                    'wind_life': 25,  # Wind turbine expected lifetime, years
                    'diesel_life': diesel_life,  # diesel generator expected lifetime, years
                    'wind_om': 0.015,  # annual OM cost of wind turbine
                    'diesel_om': 0.1,  # annual OM cost of diesel generator
                    'battery_inverter_cost': inverter_cost,
                    'battery_inverter_life': inverter_life,
                    'dod_max': 0.8,  # maximum depth of discharge of battery
                    'inv_eff': 0.93,  # inverter_efficiency
                    'lpsp_max': lpsp_max,  # maximum loss of load allowed over the year, in share of kWh
                    'diesel_limit': 0.7,  # Max annual share of mini-grid generation from diesel gen-set
                    'full_life_cycles': 2000  # Equivalent full life-cycles of battery until replacement
                }
    
    mg_diesel_params = {'diesel_price': diesel_price,
                      'efficiency': 0.33,
                      'diesel_truck_consumption': 33.7,
                      'diesel_truck_volume': 15000}
    
    # Stand-alone diesel generator specs - for grid backup
    sa_diesel_calc = Technology(base_to_peak_load_ratio=0.9,
                                capacity_factor=0.7,
                                tech_life=10,
                                om_costs=0.1,
                                capital_cost=938,
                                diesel_price=diesel_price,
                                standalone=True,
                                efficiency=0.28,
                                diesel_truck_consumption=14,
                                diesel_truck_volume=300)    

    return grid_calc, mg_pv_hybrid_calc, mg_wind_hybrid_calc, mg_hydro_calc, sa_pv_calc, sa_diesel_calc, mg_pv_hybrid_params, mg_wind_hybrid_params, mg_diesel_params, mg_interconnection, grid_reliability_option, cnse, grid_reliability


# In[ ]:




