#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import matplotlib.pylab as plt
import seaborn as sns
from onsset import *


# In[ ]:


def calc_summary_table(df, yearsofanalysis):

    techs = ["1", "2", "3", "5", "6", "7", "99"]
    tech_count = len(techs)
    no_ts = len(yearsofanalysis)

    summary = pd.Series(dtype=float, name='country')

    # Fill summary series dynamically
    for year in yearsofanalysis:
        for t in techs:
            year_str = str(year)
            code_col = f"{SET_ELEC_FINAL_CODE}{year_str}"
            pop_col = f"{SET_POP}{year_str}"
            new_conn_col = f"{SET_NEW_CONNECTIONS}{year_str}"
            cap_col = f"{SET_NEW_CAPACITY}{year_str}"
            invest_col = f"{SET_INVESTMENT_COST}{year_str}"
            emissions_col = f"AnnualEmissions{year_str}"

            # Population
            if t == '99':
                val = df[pop_col].sum() - df[f"{SET_ELEC_POP}{year_str}"].sum()
            else:
                val = df.loc[df[code_col] == int(t), pop_col].sum()
            summary[f"Population{year}{t}"] = val

            # New Connections
            if t == '99':
                val = 0
            else:
                val = df.loc[df[code_col] == int(t), new_conn_col].sum()
            summary[f"NewConnections{year}{t}"] = val

            # Capacity (MW)
            if t != '99':
                val = df.loc[(df[code_col] == int(t)), cap_col].sum() / 1000
                summary[f"Capacity{year}{t}"] = val

                # Investment
                val = df.loc[df[code_col] == int(t), invest_col].sum()
                summary[f"Investment{year}{t}"] = val

                # Emissions
                val = df.loc[df[code_col] == int(t), emissions_col].sum() / 1000000
                summary[f"Emissions{year}{t}"] = val

    summary = summary.fillna(0)

    # Create summary table
    index = techs + ['Total']
    columns = []

    for year in yearsofanalysis:
        columns.extend([
            f"Population{year}",
            f"NewConnections{year}",
            f"Capacity{year} (MW)",
            f"Investment{year} (million USD)",
            f"Emissions{year} (tCO2)"
        ])

    if no_ts > 1:
        columns.extend([
            "PopulationTotal",
            "NewConnectionsTotal",
            "CapacityTotal (MW)",
            "InvestmentTotal (million USD)",
            "EmissionsTotal (tCO2)"
        ])

    summary_table = pd.DataFrame(index=index, columns=columns)

    # Fill summary_table dynamically
    for i, year in enumerate(yearsofanalysis):
        base = i * tech_count
        for metric, col_suffix in zip(
            ["Population", "NewConnections", "Capacity", "Investment", "Emissions"],
            ["", "", " (MW)", " (million USD)", " (tCO2)"]
        ):
            col_name = f"{metric}{year}{col_suffix}"
            values = [
                summary.get(f"{metric}{year}{t}", 0) for t in techs
            ]
            if metric == "Investment":
                values_fmt = [round(v / 1e6, 2) for v in values]  # million USD
            elif metric in ["Population", "NewConnections"]:
                values_fmt = [int(v) for v in values]  # million USD
            else:
                values_fmt = [round(v, 2) for v in values]
            summary_table[col_name] = values_fmt + [sum(values_fmt)]

    if no_ts > 1:
        # Add total columns (summing across all years)
        for metric, col_suffix in zip(
            ["Population", "NewConnections", "Capacity", "Investment", "Emissions"],
            ["PopulationTotal", "NewConnectionsTotal", "CapacityTotal (MW)", "InvestmentTotal (million USD)", "EmissionsTotal (tCO2)"]
        ):
            #metric_cols = [col for col in summary_table.columns if col.startswith(metric)]
            #total_values = summary_table[metric_cols].sum(axis=1)
            #summary_table[col_suffix] = total_values
            if metric == "Population":
                # Use only the last year's population column
                final_year = yearsofanalysis[-1]
                last_col = f"Population{final_year}"
                summary_table[col_suffix] = summary_table[last_col]
            else:
                # Sum all columns for this metric
                metric_cols = [col for col in summary_table.columns if col.startswith(metric)]
                summary_table[col_suffix] = summary_table[metric_cols].sum(axis=1)

    # Map readable labels
    map_dict = {
        '1': 'Grid_dens',
        '2': 'Grid_ext',
        '3': 'SA_PV',
        '5': 'MG_PV_Hybrid',
        '6': 'MG_Wind',
        '7': 'MG_Hydro',
        '99': 'Non-electrified',
        'Total': 'Total'
    }
    summary_table.index = summary_table.index.to_series().map(map_dict)

    return summary_table, columns


# In[ ]:


def bar_plot(summary_table, columns, yearsofanalysis, techs):

    no_ts = len(yearsofanalysis)
    
    colors = ['#4e53de', '#a6aaff', '#ffc700', '#e628a0', '#1b8f4d', '#28e66d', '#808080']
    techs_colors = dict(zip(techs, colors))
    
    summary_plot=summary_table.drop(labels='Total',axis=0)
    fig_size = [35, 35]
    font_size = 1
    plt.rcParams["figure.figsize"] = fig_size
    f, axarr = plt.subplots(2, 2)
    fig_size = [15, 15]
    font_size = 20
    plt.rcParams["figure.figsize"] = fig_size

    if no_ts == 1:
        sns.barplot(x=summary_plot.index.tolist(), y=columns[0], data=summary_plot, ax=axarr[0, 0], palette=colors, hue=colors)
        axarr[0, 0].set_ylabel(columns[0], fontsize=2*font_size)
        axarr[0, 0].tick_params(axis='x', labelrotation=45)
        axarr[0, 0].tick_params(labelsize=font_size)
        sns.barplot(x=summary_plot.index.tolist(), y=columns[1], data=summary_plot, ax=axarr[0, 1], palette=colors, hue=colors)
        axarr[0, 1].set_ylabel(columns[1], fontsize=2*font_size)
        axarr[0, 1].tick_params(axis='x', labelrotation=45)
        axarr[0, 1].tick_params(labelsize=font_size)
        sns.barplot(x=summary_plot.index.tolist(), y=columns[2], data=summary_plot, ax=axarr[1, 0], palette=colors, hue=colors)
        axarr[1, 0].set_ylabel(columns[2], fontsize=2*font_size)
        axarr[1, 0].tick_params(axis='x', labelrotation=45)
        axarr[1, 0].tick_params(labelsize=font_size)
        sns.barplot(x=summary_plot.index.tolist(), y=columns[3], data=summary_plot, ax=axarr[1, 1], palette=colors, hue=colors)
        axarr[1, 1].set_ylabel(columns[3], fontsize=2*font_size)
        axarr[1, 1].tick_params(axis='x', labelrotation=45)
        axarr[1, 1].tick_params(labelsize=font_size)
    else:
        sns.barplot(x=summary_plot.index.tolist(), y=columns[-5], data=summary_plot, ax=axarr[0, 0], palette=colors, hue=colors)
        axarr[0, 0].set_ylabel(columns[-5], fontsize=2*font_size)
        axarr[0, 0].tick_params(axis='x', labelrotation=45)
        axarr[0, 0].tick_params(labelsize=font_size)
        sns.barplot(x=summary_plot.index.tolist(), y=columns[-4], data=summary_plot, ax=axarr[0, 1], palette=colors, hue=colors)
        axarr[0, 1].set_ylabel(columns[-4], fontsize=2*font_size)
        axarr[0, 1].tick_params(axis='x', labelrotation=45)
        axarr[0, 1].tick_params(labelsize=font_size)
        sns.barplot(x=summary_plot.index.tolist(), y=columns[-3], data=summary_plot, ax=axarr[1, 0], palette=colors, hue=colors)
        axarr[1, 0].set_ylabel(columns[-3], fontsize=2*font_size)
        axarr[1, 0].tick_params(axis='x', labelrotation=45)
        axarr[1, 0].tick_params(labelsize=font_size)
        sns.barplot(x=summary_plot.index.tolist(), y=columns[-2], data=summary_plot, ax=axarr[1, 1], palette=colors, hue=colors)
        axarr[1, 1].set_ylabel(columns[-2], fontsize=2*font_size)
        axarr[1, 1].tick_params(axis='x', labelrotation=45)
        axarr[1, 1].tick_params(labelsize=font_size)
    plt.show()


# In[ ]:


def map_plot(df, end_year, start_year):
    colors = ['#4e53de', '#a6aaff', '#ffc700', '#e628a0', '#1b8f4d', '#28e66d', '#808080']
    plt.figure(figsize=(9,9))
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)]==3, SET_X_DEG], df.loc[df['FinalElecCode{}'.format(end_year)]==3, SET_Y_DEG], color='#ffc700', marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)]==99, SET_X_DEG], df.loc[df['FinalElecCode{}'.format(end_year)]==99, SET_Y_DEG], color='#808080', marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)]==5, SET_X_DEG], df.loc[df['FinalElecCode{}'.format(end_year)]==5, SET_Y_DEG], color='#e628a0', marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)]==6, SET_X_DEG], df.loc[df['FinalElecCode{}'.format(end_year)]==6, SET_Y_DEG], color='#1b8f4d', marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)]==7, SET_X_DEG], df.loc[df['FinalElecCode{}'.format(end_year)]==7, SET_Y_DEG], color='#28e66d', marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)]==1, SET_X_DEG], df.loc[df['FinalElecCode{}'.format(end_year)]==1, SET_Y_DEG], color='#4e53de', marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)]==2, SET_X_DEG], df.loc[df['FinalElecCode{}'.format(end_year)]==2, SET_Y_DEG], color='#a6aaff', marker=',', linestyle='none')
    if df[SET_X_DEG].max() - df[SET_X_DEG].min() > df[SET_Y_DEG].max() - df[SET_Y_DEG].min():
        plt.xlim(df[SET_X_DEG].min() - 1, df[SET_X_DEG].max() + 1)
        plt.ylim((df[SET_Y_DEG].min()+df[SET_Y_DEG].max())/2 - 0.5*abs(df[SET_X_DEG].max() - df[SET_X_DEG].min()) - 1, (df[SET_Y_DEG].min()+df[SET_Y_DEG].max())/2 + 0.5*abs(df[SET_X_DEG].max() - df[SET_X_DEG].min()) + 1)
    else:
        plt.xlim((df[SET_X_DEG].min()+df[SET_X_DEG].max())/2 - 0.5*abs(df[SET_Y_DEG].max() - df[SET_Y_DEG].min()) - 1, (df[SET_X_DEG].min()+df[SET_X_DEG].max())/2 + 0.5*abs(df[SET_Y_DEG].max() - df[SET_Y_DEG].min()) + 1)
        plt.ylim(df[SET_Y_DEG].min() -1, df[SET_Y_DEG].max() +1)
    plt.figure(figsize=(30,30))
    plt.show()

    print('Number of new PV Hybrid mini-grid locations: ', len(onsseter.df[onsseter.df['FinalElecCode' + "{}".format(end_year)] == 5]) - len(onsseter.df.loc[onsseter.df['FinalElecCode{}'.format(start_year)] == 5]))


# In[ ]:


def finalize_results(self, yearsofanalysis, simplified=False):

    for year in yearsofanalysis:
        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2, 'Technology{}'.format(year)] = 'Grid extension'
    
    if simplified:
        del self.df['minTDdist']
        del self.df['MVConnectDist']
        del self.df['AnnualEmissionsTotal']
        for year in yearsofanalysis:
            del self.df['AnnualEmissions' + "{}".format(year)]
            del self.df['PVHybridEmissionFactor' + "{}".format(year)]
    else:
        for n in ['NewDist', 'GridCapacityRequired', 'X', 'Y', 'minTDdist',
                 'MVConnectDist', 'MaxDist', 'AverageToPeakLoadRatio',
                 'level_0', 'index']: # 'MaxDist', 'MaxIntensificationDist', 'AnnualEmissionsTotal'
            try:
                del self.df[n]
            except:
                pass
        #del self.df['NewDist']
        #del self.df['MaxIntensificationDist']
        #del self.df['GridCapacityRequired']
        #del self.df['MaxDist']
        #del self.df['X']
        #del self.df['Y']
        #del self.df['minTDdist']
        #del self.df['MVConnectDist']
        #del self.df['AnnualEmissionsTotal']
        for year in yearsofanalysis:
            for n in ['PreSelection', 'GridCapacityRequired', 'PVHybridEmissionFactor', 'UnmetDemand', 'FilterLCOE', 'MaxDist', 'MaxIntensificationDist',
                     'SADieselFuelCost', 'windHybridEmissionFactor', 'windHybridGenLCOE', 'MGDieselFuelCost', 'PVHybridGenLCOE', 'Off_Grid_Code']: 
                #'AnnualEmissions'
                try:
                    del self.df[n + "{}".format(year)]
                except:
                    pass
            #del self.df['PreSelection' + "{}".format(year)]
            #del self.df['AnnualEmissions' + "{}".format(year)]
            #del self.df['GridCapacityRequired' + "{}".format(year)]
            #del self.df['MaxDist' + "{}".format(year)]
            #del self.df['PVHybridEmissionFactor' + "{}".format(year)]

    for i in range(len(self.df.columns)):
        if self.df.iloc[:, i].dtype == 'float64':
            self.df.iloc[:, i] = pd.to_numeric(self.df.iloc[:, i], downcast='float')
        elif self.df.iloc[:, i].dtype == 'int64':
            self.df.iloc[:, i] = pd.to_numeric(self.df.iloc[:, i], downcast='signed')


# In[ ]:


def run_scenario(onsseter, end_year_pop, urban_ratio_end_year, start_year, end_year, yearsofanalysis, x_coordinates, y_coordinates, tier_1, 
                 tier_2, tier_3, tier_4, tier_5, hv_line_capacity, hv_line_cost, hv_mv_transformer_cost, hv_mv_transformer_type, eleclimits, time_steps, 
                 annual_new_grid_connections_limit, annual_grid_cap_gen_limit, num_people_per_hh_urban, num_people_per_hh_rural, urban_target_tier, 
                 rural_target_tier_large, rural_target_tier_small, rural_cutoff_size, mg_diesel_params, mg_wind_hybrid_params, wind_path, 
                 mg_pv_hybrid_params, pv_path, mg_hydro_calc, mg_wind_hybrid_calc, sa_pv_calc, mg_pv_hybrid_calc, min_mg_size, mg_min_grid_dist,
                 grid_generation_cost, grid_calc, sa_diesel_calc, max_grid_intensification_cost, auto_intensification, grid_mv_line_max_length, 
                 mg_interconnection, grid_reliability_option, cnse, grid_reliability, prio_choice, grid_emission_factor, shares, assign_shares, priorities,priority):
    
    x_coords = x_coordinates * 1
    y_coords = y_coordinates * 1
    onsseter.df[SET_HH_DEMAND] = 0


    print('Starting', time.ctime())
    
    techs = ["Grid", "SA_PV", "MG_PVHybrid", "MG_Wind", "MG_Hydro"]
    tech_codes = [1, 3, 5, 6, 7]
    tiers = {1: tier_1, 2: tier_2, 3: tier_3, 4: tier_4, 5: tier_5}
    
    onsseter.project_pop_and_urban(end_year_pop, urban_ratio_end_year, start_year, yearsofanalysis)
    
    onsseter.prepare_wtf_tier_columns(tier_1, tier_2, tier_3, tier_4, tier_5)
    
    onsseter.current_mv_line_dist()
    
    onsseter.add_xy_3395()
    
    try:
        onsseter.df.reset_index(inplace=True)
    except ValueError:
        pass
    
    Technology.set_default_values(base_year=start_year, start_year=start_year, end_year=end_year, hv_line_type=hv_line_capacity, 
                                  hv_line_cost=hv_line_cost, hv_mv_sub_station_cost=hv_mv_transformer_cost, hv_mv_substation_type=hv_mv_transformer_type)
    
    new_lines_geojson = {}
    
    for year in yearsofanalysis:
            
        eleclimit = eleclimits[year]
        time_step = time_steps[year]
        
        grid_connect_limit = time_step * annual_new_grid_connections_limit
        grid_cap_gen_limit = time_step * annual_grid_cap_gen_limit * 1000
            
        onsseter.calculate_demand(year, num_people_per_hh_urban, num_people_per_hh_rural, time_step,
                                  urban_target_tier, rural_target_tier_large, rural_target_tier_small, rural_cutoff_size, tiers)
    
        onsseter.calculate_unmet_demand(year, reliability=grid_reliability)
    
        try:
            del onsseter.df[SET_MG_DIESEL_FUEL + "{}".format(year)]
            del onsseter.df[SET_SA_DIESEL_FUEL + "{}".format(year)]
        except:
            pass
        onsseter.diesel_cost_columns(mg_diesel_params, mg_diesel_params, year)
        mean = onsseter.df[SET_MG_DIESEL_FUEL + "{}".format(year)].mean()
        onsseter.df[SET_MG_DIESEL_FUEL + "{}".format(year)].fillna(mean, inplace=True)
    
        print('Optimize Wind Hybrid Systems', time.ctime())
        wind_hybrid_lcoe, wind_hybrid_capacity, wind_hybrid_investment, wind_check = \
                        onsseter.wind_hybrids_lcoe_lookuptable(year, time_step, end_year, mg_wind_hybrid_params, wind_path=wind_path)
        wind_hybrid_investment.fillna(0, inplace=True)
        wind_hybrid_capacity.fillna(0, inplace=True)
    
        mg_wind_hybrid_calc.hybrid_fuel = wind_hybrid_lcoe
        mg_wind_hybrid_calc.hybrid_investment=wind_hybrid_investment
        mg_wind_hybrid_calc.hybrid_capacity=wind_hybrid_capacity

        #print(wind_hybrid_lcoe.min())
        #print(wind_hybrid_lcoe)
            
        print('Optimize MG Hybrid Systems', time.ctime())
        hybrid_lcoe, hybrid_capacity, hybrid_investment, check = \
                        onsseter.pv_hybrids_lcoe_lookuptable(year, time_step, end_year, mg_pv_hybrid_params, pv_path=pv_path)
        hybrid_investment.fillna(0, inplace=True)
        hybrid_capacity.fillna(0, inplace=True)
    
        mg_pv_hybrid_calc.hybrid_fuel = hybrid_lcoe
        mg_pv_hybrid_calc.hybrid_investment=hybrid_investment
        mg_pv_hybrid_calc.hybrid_capacity=hybrid_capacity
        
        print('Calculate Off-Grid LCOEs', time.ctime())
        sa_pv_investment, sa_pv_capacity, mg_pv_hybrid_investment, mg_pv_hybrid_capacity, mg_wind_investment, mg_wind_capacity, \
                mg_hydro_investment, mg_hydro_capacity = onsseter.calculate_off_grid_lcoes(mg_hydro_calc, mg_wind_hybrid_calc, sa_pv_calc, mg_pv_hybrid_calc,
                                                                                           year, end_year, time_step, techs, tech_codes,
                                                                                           min_mg_size, mg_min_grid_dist)
        
        print('Calculate Grid LCOEs', time.ctime())
        grid_investment, grid_capacity, grid_cap_gen_limit, grid_connect_limit = \
                    onsseter.pre_electrification(grid_generation_cost, year, time_step, end_year, grid_calc, sa_diesel_calc, grid_reliability_option,
                                                 grid_cap_gen_limit, grid_connect_limit)
        
        onsseter.max_extension_dist(year, time_step, end_year, start_year, grid_calc, sa_diesel_calc, grid_reliability_option,
                                    max_grid_intensification_cost, auto_intensification=auto_intensification)

        # onsseter.df.loc[onsseter.df[SET_MV_DIST_PLANNED] >= 0, 'MaxIntensificationDist'] = -1
    
        onsseter.pre_selection(eleclimit, year, time_step, 2, auto_intensification, prio_choice)
    
        
        onsseter.df[SET_LCOE_GRID + "{}".format(year)], onsseter.df[SET_MIN_GRID_DIST + "{}".format(year)], \
            grid_investment, grid_capacity, x_coords, y_coords, new_lines_geojson[year] = \
            onsseter.elec_extension_numba(grid_calc, mg_diesel_params, grid_reliability_option, grid_mv_line_max_length, year, start_year, end_year, time_step, grid_cap_gen_limit, grid_connect_limit,
                                          x_coords, y_coords, mg_interconnection=mg_interconnection, auto_intensification=auto_intensification, 
                                          prioritization=2, threshold=max_grid_intensification_cost,
                                          )
        
        print('Calculating results columns', time.ctime())
        onsseter.results_columns(techs=techs, tech_codes=tech_codes, year=year, time_step=time_step, prio=2, auto_intensification=auto_intensification, 
                                 mg_interconnection=mg_interconnection, shares=shares, assign_shares=assign_shares, priorities=priorities, priority=priority)
    
        onsseter.calculate_investments_and_capacity(sa_pv_investment, sa_pv_capacity, mg_pv_hybrid_investment, mg_pv_hybrid_capacity, 
                                                    mg_wind_investment, mg_wind_capacity, mg_hydro_investment, mg_hydro_capacity, 
                                                    grid_investment, grid_capacity, year)
    
        if year == yearsofanalysis[-1]:
            final_step = True
        else:
            final_step = False
    
        onsseter.check_grid_limitations(time_step * annual_new_grid_connections_limit, 
                                        time_step * annual_grid_cap_gen_limit * 1000, 
                                        year, time_step, final_step)
    
        onsseter.apply_limitations(eleclimit, year, time_step, 2, auto_intensification)
    
        onsseter.calculate_emission(grid_factor=grid_emission_factor, year=year,
                                    time_step=time_step, start_year=start_year)
    
        onsseter.df.loc[(onsseter.df[SET_ELEC_FINAL_CODE + '{}'.format(year)] == 1) &
                            (onsseter.df[SET_ELEC_FINAL_CODE + '{}'.format(start_year)] != 1),
                            SET_ELEC_FINAL_CODE + '{}'.format(year)] = 2
        print('')

    return onsseter.df, new_lines_geojson


# In[ ]:


def save_variables(onsseter, start_year, end_year, end_electrification_rate_target, urban_target_tier, rural_target_tier_large,
                   rural_target_tier_small, auto_intensification, max_grid_intensification_cost, end_year_pop, urban_ratio_end_year,
                   grid_generation_cost, grid_power_plants_capital_cost, grid_losses, diesel_price, mg_hydro_capital_cost, min_mg_size,
                   mg_min_grid_dist, mg_interconnection, pv_cost, battery_cost, inverter_cost, diesel_gen_cost, max_diesel, sa_pv_capital_cost_1,
                   sa_pv_capital_cost_2, sa_pv_capital_cost_3, sa_pv_capital_cost_4, sa_pv_capital_cost_5, grid_mv_line_cost, grid_lv_line_cost,
                   grid_mv_line_capacity, grid_lv_line_capacity, grid_lv_line_max_length, hv_line_cost, grid_mv_line_max_length, 
                   annual_new_grid_connections_limit, annual_grid_cap_gen_limit, grid_discount_rate, mini_grid_discount_rate, standalone_discount_rate):
    list1 = [('Start_year',start_year,'','',''), 
         ('End_year',end_year,'','',''),
         ('End year electrification rate target',end_electrification_rate_target,'','',''),
         ('Start year elec rate modelled', onsseter.df.ElecPopCalib.sum() / onsseter.df.PopStartYear.sum(), '', '', ''), 
         ('Urban target tier', urban_target_tier, '', '', ''),
         ('Rural target tier large', rural_target_tier_large, '', '', ''),
         ('Rural target tier small', rural_target_tier_small, '', '', ''),
         ('Intensification distance', auto_intensification, '', '', 'Distance from existing MV network (km) for automatic connection to the grid'),
         ('Max intensification cost', max_grid_intensification_cost, 'Maximum cost per household (USD/household) for forced grid intensification'),
         ('Pop start year', onsseter.df.PopStartYear.sum(), '', '', 'Population in the start of the analysis'),
         ('pop_end_year',end_year_pop,'','','the projected population in the end year (e.g. 2030)'),
         ('urban_ratio_start_year', onsseter.df.loc[onsseter.df['IsUrban'] == 2, 'PopStartYear'].sum() / onsseter.df.PopStartYear.sum(), '','','the urban population population ratio in the start year'), 
         ('urban_ratio_end_year',urban_ratio_end_year,'','','the urban population population ratio in the end year'),
         ('grid_generation_cost',grid_generation_cost,'','','This is the grid cost electricity USD/kWh as expected in the end year of the analysis'),
         ('grid_power_plants_capital_cost',grid_power_plants_capital_cost,'','','The cost in USD/kW to for capacity upgrades of the grid-connected power plants'),
         ('grid_losses',grid_losses,'','','The fraction of electricity lost in transmission and distribution (percentage)'),
         ('diesel_price',diesel_price,'','','This is the diesel price in USD/liter as expected in the end year of the analysis'),
         ('mg_hydro_capital_cost',mg_hydro_capital_cost,'','','Mini-grid Hydro capital cost (USD/kW) as expected in the years of the analysis'),
         ('min_mg_size', min_mg_size, 'Minimum number of connections (households) for mini-grids to be considered'), 
         ('mg_min_grid_dist', mg_min_grid_dist, 'Minimum distance from existing MV lines for mini-grids to be considered as an option'), 
         ('mg_interconnection', mg_interconnection, 'Whether mini-grids should be allowed to be interconnected to the grid in a later time-step. 0 = NO, 1 = YES'), 
         ('pv_cost', pv_cost, 'Mini-grid: PV panel costs including BoS (PV inverter, charge controller) (USD/kW)'), 
         ('battery_cost', battery_cost, 'Mini-grid: battery capital cost, USD/kWh of storage capacity'), 
         ('inverter_cost', inverter_cost, 'Mini-grid: Battery inverter (USD/kW)'), 
         ('diesel_gen_cost', diesel_gen_cost, 'Mini-grid: diesel generator capital cost, USD/kW rated power'), 
         ('max_diesel', max_diesel, 'Mini-grid: Maximum share of generation that can come from diesel generators (0-1). Set to 0 for fully renewable mini-grids'), 
         ('sa_pv_capital_cost_1',sa_pv_capital_cost_1,'','','Stand-alone PV capital cost (USD/kW) for household systems under 20 W'),
         ('sa_pv_capital_cost_2',sa_pv_capital_cost_2,'','','Stand-alone PV capital cost (USD/kW) for household systems between 21-50 W'),
         ('sa_pv_capital_cost_3',sa_pv_capital_cost_3,'','','Stand-alone PV capital cost (USD/kW) for household systems between 51-100 W'),
         ('sa_pv_capital_cost_4',sa_pv_capital_cost_4,'','','Stand-alone PV capital cost (USD/kW) for household systems between 101-200 W'),
         ('sa_pv_capital_cost_5',sa_pv_capital_cost_5,'','','Stand-alone PV capital cost (USD/kW) for household systems over 200 W'),
         ('grid_mv_line_cost',grid_mv_line_cost,'','','Cost of MV lines in USD/km'),
         ('grid_lv_line_cost',grid_lv_line_cost,'','','Cost of LV lines in USD/km'),
         ('grid_mv_line_capacity',grid_mv_line_capacity,'','','Capacity of MV lines in kW/line'),
         ('grid_lv_line_capacity',grid_lv_line_capacity,'','','Capacity of LV lines in kW/line'),
         ('grid_lv_line_max_length',grid_lv_line_max_length,'','','Maximum length of LV lines (km)'),
         ('hv_line_cost',hv_line_cost,'','','Cost of HV lines in USD/km'),
         ('max_grid_extension_dist',grid_mv_line_max_length,'','','Maximum distance that the grid may be extended by means of MV lines'),
         ('annual_new_grid_connections_limit', annual_new_grid_connections_limit,'','','This is the maximum amount of new households that can be connected to the grid in one year (thousands)'),
         ('grid_capacity_limit',annual_grid_cap_gen_limit,'','','This is the maximum generation capacity that can be added to the grid in one year (MW)'),
         ('grid_discount_rate', grid_discount_rate, 'Grid discount rate'),
         ('mini_grid_discount_rate',mini_grid_discount_rate , 'Mini-grid discount rate'),
         ('standalone_discount_rate', standalone_discount_rate, 'Stand-alone PV discount rate'),

         ]
    labels = ['Variable','Value', 'Source', 'Comments', 'Description']
    df_variables = pd.DataFrame.from_records(list1, columns=labels)

    return df_variables


# In[1]:


def dropdown_popup(options):
    selected_value = None

    def on_select():
        nonlocal selected_value
        selected_value = variable.get()
        window.destroy()

    # Use Toplevel instead of creating a new Tk instance
    window = tk.Toplevel()
    window.title("Choose an option")

    variable = tk.StringVar(window)
    variable.set(options[0])  # default value

    dropdown = tk.OptionMenu(window, variable, *options)
    dropdown.pack(padx=100, pady=10)

    button = tk.Button(window, text="OK", command=on_select)
    button.pack(pady=20, padx=40)

    # Update the window to calculate size
    window.update_idletasks()

    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Get window width and height
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Calculate x and y coordinates
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set geometry
    window.geometry(f"+{x}+{y}")

    # Wait until this window is closed
    window.grab_set()
    window.wait_window()

    return selected_value


# In[ ]:




