# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 17:07:47 2026

@author: corra
"""

def build_country_inputs(country, coe):
    """
    Build all OnSSET inputs for a country and scenario.
    Returns all variables used later in the notebook.
    """
    
    import pycountry
    import pandas as pd
    
    inputs = {}
    
    # Country codes
    alpha_2 = pycountry.countries.lookup(country).alpha_2
    alpha_3 = pycountry.countries.lookup(country).alpha_3
    inputs["alpha_2"] = alpha_2
    inputs["alpha_3"] = alpha_3
    
    # Settlement processor
    input_file = "input/OnSSET_InputFile_Calibrated_v1.csv"
    from onsset import SettlementProcessor
    onsseter = SettlementProcessor(input_file)
    onsseter.conditioning()
    inputs["onsseter"] = onsseter
    
    # Paths for PV/Wind data
    pv_path = "input/ug-2-pv.csv"
    
    wind_path = "input/ug-2-wind.csv"
    inputs["pv_path"] = pv_path
    inputs["wind_path"] = wind_path
    
    # Existing MV lines
 
    existing_mv = "input/UGA/UGA/UGA_mv_lines.shp"
    x_mv_exist, y_mv_exist = onsseter.start_extension_points(existing_mv)
    inputs["x_coordinates"] = x_mv_exist
    inputs["y_coordinates"] = y_mv_exist
    
    # Read specs Excel
    spec_path = r"input\UGA_specs.xlsx"
    specs_data = pd.read_excel(spec_path, sheet_name="SpecsData")
    scenario_parameters = pd.read_excel(spec_path, sheet_name="ScenarioParameters")
    inputs["specs_data"] = specs_data
    inputs["scenario_parameters"] = scenario_parameters
    
    # Modeling period & electrification target
    start_year = int(specs_data.loc[0, "StartYear"])
    end_year = int(specs_data.loc[0, "EndYEar"])
    end_electrification_rate_target = float(scenario_parameters.loc[0, "EndYearTarget"]) 
    print(f"The target electrification rate is: {end_electrification_rate_target:.2%}")
    yearsofanalysis = [end_year]
    eleclimits = {end_year: end_electrification_rate_target}
    time_steps = {end_year: end_year - start_year}
    
    inputs.update({
        "start_year": start_year,
        "end_year": end_year,
        "yearsofanalysis": yearsofanalysis,
        "end_electrification_rate_target":end_electrification_rate_target,
        "eleclimits": eleclimits,
        "time_steps": time_steps
    })
      
    # Demographics
    end_year_pop = specs_data.loc[0, "PopEndYear"]
    urban_ratio_end_year = specs_data.loc[0, "UrbanRatioEndYear"]
    num_people_per_hh_urban = specs_data.loc[0, "NumPeoplePerHHUrban"]
    num_people_per_hh_rural = specs_data.loc[0, "NumPeoplePerHHRural"]
    
    inputs.update({
        "end_year_pop": end_year_pop,
        "urban_ratio_end_year": urban_ratio_end_year,
        "num_people_per_hh_urban": num_people_per_hh_urban,
        "num_people_per_hh_rural": num_people_per_hh_rural
    })
    
    
    grid_generation_cost = coe           #LCOE     ### This is the grid cost electricity USD/kWh as expected in the end year of the analysis
    grid_power_plants_capital_cost = specs_data.loc[0,'GridCapacityInvestmentCost'] # 2500      ### The cost in USD/kW is for capacity upgrades of the grid
    grid_losses = specs_data.loc[0,'GridLosses']# 0.15                         ### The fraction of electricity lost in transmission and distribution (percentage)
    
    ef_path = "input/HGEF.csv"
    emission_factors = pd.read_csv(ef_path)
    grid_emission_factor = emission_factors.loc[emission_factors['Country']==alpha_3, 'OperatingMargin'].values[0]     ### This is the average emissions from grid generation (gCO2/kWh), see e.g. https://unfccc.int/documents/461676
    
    annual_new_grid_connections_limit = 99999999 #99999999 # This is the maximum amount of new households that can be connected to the grid in one year
    annual_grid_cap_gen_limit = specs_data.loc[0,'NewGridGenerationCapacityAnnualLimitMW']#9999999   
        
    inputs.update({
        "grid_generation_cost": grid_generation_cost,
        "grid_power_plants_capital_cost": grid_power_plants_capital_cost,
        "grid_losses": grid_losses,
        "grid_emission_factor": grid_emission_factor, 
        "emission_factors": emission_factors, 
        "annual_new_grid_connections_limit": annual_new_grid_connections_limit, 
        "annual_grid_cap_gen_limit": annual_grid_cap_gen_limit
    })       
    
    #Centralized grid parameter 
    # Grid Transmission and distribution costs
    hv_line_capacity=110 # kV
    hv_line_cost=106000 * 1.35 # USD/km 106000
    
    grid_mv_line_capacity=33 # kV
    grid_mv_line_cost=25000 * 1.35 # USD/kW 25000 44300
    grid_mv_line_max_length=150 # km
    grid_MV_line_amperage_limit = 275  # Ampere (A)
    
    grid_lv_line_capacity=0.4 #kV
    grid_lv_line_max_length=1 # km
    grid_lv_line_cost=15000 * 1.35 # USD/km 15000
    
    grid_service_Transf_type=75  # kVA
    grid_service_Transf_cost=9000 * 1.38  # $/unit
    grid_max_nodes_per_serv_trans=95  # maximum number of nodes served by each service (MV/LV) transformer
    
    hv_mv_transformer_type = 16000 #kVA
    hv_mv_transformer_cost = 980000 * 1.38 # USD/unit
    
    import pandas as pd

# Create a DataFrame with the grid parameters for easy copy-paste

    grid_params = {
        "Parameter": [
            "hv_line_capacity",
            "hv_line_cost",
            "grid_mv_line_capacity",
            "grid_mv_line_cost",
            "grid_mv_line_max_length",
            "grid_MV_line_amperage_limit",
            "grid_lv_line_capacity",
            "grid_lv_line_max_length",
            "grid_lv_line_cost",
            "grid_service_Transf_type",
            "grid_service_Transf_cost",
            "grid_max_nodes_per_serv_trans",
            "hv_mv_transformer_type",
            "hv_mv_transformer_cost"
        ],
        "Value": [
            hv_line_capacity,
            hv_line_cost,
            grid_mv_line_capacity,
            grid_mv_line_cost,
            grid_mv_line_max_length,
            grid_MV_line_amperage_limit,
            grid_lv_line_capacity,
            grid_lv_line_max_length,
            grid_lv_line_cost,
            grid_service_Transf_type,
            grid_service_Transf_cost,
            grid_max_nodes_per_serv_trans,
            hv_mv_transformer_type,
            hv_mv_transformer_cost
        ]
    }

    inputs["grid_params"] = grid_params   
    
    
    #Off-grid Technology parameter 
    min_mg_size = 100             # Minimum number of households in a settlement for mini-grids to be considered
    mg_min_grid_dist = 0  
    diesel_price = 1.43          
    pv_cost = 1400                      # PV panel costs including BoS (PV inverter, charge controller) (USD/kW)
    battery_cost = 550                 # battery capital cost, USD/kWh of storage capacity                    
    inverter_cost  = 598             # Battery inverter, USD/kW
    diesel_gen_cost = 500              # diesel generator capital cost, USD/kW rated power
    wind_cost = 2500                   # Wind turbine capital cost, USD/kW peak power
    
    inverter_life=20    # Battery inverter expected lifetime in mini-grid, years
    diesel_life=20      # diesel generator expected lifetime in mini-grid, years
    pv_life=25          # PV panel expected lifetime in mini-grid, years
            
    lpsp_max=0.10         # maximum loss of load allowed over the year, in share of kWh (e.g. 0.1 means that the mini-grid will be able to meet at least 90% of the demand over the year)
    max_diesel = 0.5     
    mg_hydro_capital_cost = {float("inf"): 15000}   
    
    
    mg_mv_line_capacity=33 # kV
    mg_mv_line_cost = 25000 # USD/kW
    mg_MV_line_amperage_limit = 275  # Ampere (A)
    
    mg_lv_line_capacity=0.4 #kV
    mg_lv_line_max_length=1 # km
    mg_lv_line_cost=15000 # USD/km
    
    mg_service_Transf_type=75  # kVA 75
    mg_service_Transf_cost=9000  # $/unit 9000
    mg_max_nodes_per_serv_trans=1  # maximum number of nodes served by each service (MV/LV) transformer 95
    
    sa_pv_capital_cost_1 = 11600          ### Solar Home System capital cost (USD/kW) for household systems under 20 W
    sa_pv_capital_cost_2 = 7500          ### Solar Home System capital cost (USD/kW) for household systems between 21-50 W
    sa_pv_capital_cost_3 = 7500           ### Solar Home System capital cost (USD/kW) for household systems between 51-100 W
    sa_pv_capital_cost_4 = 8000           ### Solar Home System capital cost (USD/kW) for household systems between 101-1000 W
    sa_pv_capital_cost_5 = 8000           ### Solar Home System capital cost (USD/kW) for household systems over 1 kW
    
    shs_lifetime = 5                      ### Expected technology lifetime of Solar Home System
    grid_discount_rate = 0.08 # E.g. 0.08 means a discount rate of 8%
    mini_grid_discount_rate = 0.08
    standalone_discount_rate = 0.08
  
    
  
    
    inputs.update({
        "min_mg_size": min_mg_size,
        "mg_min_grid_dist": mg_min_grid_dist,
        "diesel_price": diesel_price,
        "pv_cost": pv_cost, 
        "battery_cost": battery_cost, 
        "inverter_cost": inverter_cost, 
        "diesel_gen_cost": diesel_gen_cost,
        "wind_cost": wind_cost,
        "inverter_life": inverter_life,
        "diesel_life": diesel_life,
        "pv_life": pv_life,
        "lpsp_max": lpsp_max,
        "max_diesel": max_diesel,
        "mg_hydro_capital_cost": mg_hydro_capital_cost,
        "mg_mv_line_capacity": mg_mv_line_capacity,
        "mg_mv_line_cost": mg_mv_line_cost,
        "mg_MV_line_amperage_limit": mg_MV_line_amperage_limit,
        "mg_lv_line_capacity": mg_lv_line_capacity,
        "mg_lv_line_max_length": mg_lv_line_max_length,
        "mg_lv_line_cost": mg_lv_line_cost,
        "mg_service_Transf_type": mg_service_Transf_type,
        "mg_service_Transf_cost": mg_service_Transf_cost,
        "mg_max_nodes_per_serv_trans": mg_max_nodes_per_serv_trans,
        "sa_pv_capital_cost_1": sa_pv_capital_cost_1,
        "sa_pv_capital_cost_2": sa_pv_capital_cost_2,
        "sa_pv_capital_cost_3": sa_pv_capital_cost_3, 
        "sa_pv_capital_cost_4": sa_pv_capital_cost_4,
        "sa_pv_capital_cost_5": sa_pv_capital_cost_5,
        "shs_lifetime": shs_lifetime, 
        "grid_discount_rate": grid_discount_rate,
        "mini_grid_discount_rate": mini_grid_discount_rate,
        "standalone_discount_rate": standalone_discount_rate,        
    })
    # Electricity tiers
    inputs.update({
        "tier_1": 75,
        "tier_2": 260,
        "tier_3": 500,
        "tier_4": 1250,
        "tier_5": 3000
    })
    
    # Scenario demand tiers
    rural_cutoff_size = 100
    urban_target_tier = scenario_parameters.loc[0,'UrbanTargetTier']
    rural_target_tier_large = scenario_parameters.loc[0,'RuralTargetTier']
    rural_target_tier_small = scenario_parameters.loc[0,'RuralTargetTier']
    
    inputs.update({
        "rural_cutoff_size": rural_cutoff_size,
        "urban_target_tier": urban_target_tier,
        "rural_target_tier_large": rural_target_tier_large,
        "rural_target_tier_small": rural_target_tier_small
    })
    
    # Productive demand & rollout
    inputs.update({
        "productive_demand": 1,
        "auto_intensification": 0,
        "max_grid_intensification_cost": 2000,
        "prio_choice": 1
    })
    
    # You can continue adding the **rest of the variables** exactly like above:
    # grid_losses, grid_power_plants_capital_cost, grid_generation_cost, etc.
    # All variables that are **used by init_tech_info**
    
    return inputs
