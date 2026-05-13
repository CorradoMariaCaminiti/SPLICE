# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 14:18:30 2026

@author: corra
"""

import pandas as pd 
import os
import geopandas as gpd
from shapely.geometry import Point  
import numpy as np
import yaml 
def footbridge(it, pypsapath): 
    config_path = os.path.join(pypsapath, "config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    # Update name 
    country_prefix = config["run"]["name"].rsplit("_", 1)[0]
    scenario_name = f'{country_prefix}_{it}'
    output_dir = "output"
    input_file = os.path.join(output_dir, '{}_Results.csv'.format(scenario_name)) 
    
    #input_file = rf"output\ETP_Scenario_longRun_v1_highLCOE_{it}_Results.csv"
    df = pd.read_csv(input_file)
    
    gdf = gpd.read_file(r"input\ug-1\final_clusters.shp") 
    merged = gdf.merge(df, left_on="id", right_on="id")  
    
    techs = ["Grid","Grid Ext", "SA_PV", "MG_PVHybrid", "MG_Wind", "MG_Hydro","Unelectrified"]
    tech_codes = [1, 2, 3, 5, 6, 7, 99] 
    
    tech_map = dict(zip(techs, tech_codes)) 
    code_map = dict(zip(tech_codes, techs))
    merged['TechCode2065'] = merged['FinalElecCode2065'].map(lambda x: tech_map.get(x, x))  
    merged['TechName2065'] = merged['FinalElecCode2065'].map(lambda x: code_map.get(x, x))
    merged['TechName2024'] = merged['FinalElecCode2024'].map(lambda x: code_map.get(x, x)) 
    
    spec_path = r"input\UGA_specs.xlsx"
    scenario_parameters = pd.read_excel(spec_path, sheet_name="ScenarioParameters")
    urban_target_tier = scenario_parameters.loc[0,'UrbanTargetTier']
    rural_target_tier_large = scenario_parameters.loc[0,'RuralTargetTier']
    rural_target_tier_small = scenario_parameters.loc[0,'RuralTargetTier']
    tiers = ({
        "1": 75,
        "2": 260,
        "3": 500,
        "4": 1250,
        "5": 3000
    })
    rural_tier_key = str(int(rural_target_tier_large)) 
    rural_target_value = tiers[rural_tier_key] 
    urban_tier_key = str(int(rural_target_tier_large)) 
    urban_target_value = tiers[urban_tier_key]
    merged['TargetPerCapita'] = np.where(merged['IsUrban'] == 2,  urban_target_value, rural_target_value)
    merged['TotalEnergyPerCell'] = (merged['Pop2065'] * merged['TargetPerCapita'])

    columnToKeep = ['id', 'TechName2024', 'TechName2065', 'TotalEnergyPerCell','Pop2065', 'geometry']
    merged_light = merged[columnToKeep] 
    
     # Tengo solo quelli che 2065 sono connessi alla rete 
    

    
       
    merged_light_up = merged_light[merged_light['TechName2065'].isin(['Grid', 'Grid Ext'])]                                                   
    areas = gpd.read_file(r'input\regionsUpgraded_GADM.gpkg')  
    initialGeometries = areas['geometry'] 
    
    # 1. Make sure merged_light_up is a GeoDataFrame
    if not isinstance(merged_light_up, gpd.GeoDataFrame):
        merged_light_up = gpd.GeoDataFrame(merged_light_up, geometry='geometry', crs=areas.crs)
    
    # 2. Ensure both GeoDataFrames use the same CRS
    merged_light_up = merged_light_up.to_crs(areas.crs)
    
    # 3. Spatial join: assign each point (cell) to the polygon it falls inside
    merged_with_areas = gpd.sjoin(merged_light_up, areas, how="left", predicate="within")
    
    # 4. Group by polygon and sum the energy values
    energy_sum = merged_with_areas.groupby(merged_with_areas.index_right)['TotalEnergyPerCell'].sum()
    
    # 5. Add the new attribute to your areas GeoDataFrame
    areas['TotalEnergySum'] = energy_sum
    areas['TotalEnergySum'] = areas['TotalEnergySum'].fillna(0) 
    
    areas = areas.rename(columns={'TotalEnergySum': 'demand'})
    
    areas['demand'] = areas['demand']/1e3 #kwh -mwh
    centroids = areas.centroid
    
    # Reproject centroids to a meter-based CRS (Web Mercator for simplicity)
    centroids_m = centroids.to_crs(epsg=3857)
    
    # Buffer in meters (100 m)
    buffers_m = centroids_m.buffer(0.1)
    
    areas['geometry'] = buffers_m.to_crs(epsg=4326) 
    
    industrial = gpd.read_file(r'input\industrialDem.gpkg')  
    industrial["IndustrialDemand"] = industrial["IndustrialDemand"].fillna(0)
    
    areas = areas.merge(industrial[['GID_1', 'IndustrialDemand']], left_on='GID_1', right_on='GID_1', how='left') 
    areas['country'] = 'UG' 
    areas.drop(columns=["COUNTRY"], inplace = True) 
    path = os.path.join(pypsapath, f"data/demand_{it}.geojson")
    areas.to_file(path, driver="GeoJSON") 
    return path