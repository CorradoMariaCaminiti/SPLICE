# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 11:22:34 2026

@author: corra
"""

import os
import pypsa
import csv
import re 
import yaml
pypsa_path_original = r"C:\Users\corra\pypsa-earth"
results_folder = r"C:\Users\corra\pypsa-earth\results"
config_path = os.path.join(pypsa_path_original, "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)
# Country / network prefix
country_prefix = config["run"]["name"].rsplit("_", 1)[0] 

# List all folders in the results folder
all_folders = os.listdir(results_folder)
pattern = re.compile(rf"{re.escape(country_prefix)}_(\d+)$") 


iteration_numbers = []
for folder in all_folders:
    match = pattern.match(folder)
    if match:
        iteration_numbers.append(int(match.group(1)))

# Get the highest iteration number
if iteration_numbers:
    highest_iteration = max(iteration_numbers)
else:
    print('Watch out')  # default if no folder found

iter_folder = os.path.join(results_folder, f"{country_prefix}_{highest_iteration}")

# Define iteration as a variable
iteration = highest_iteration
# Locate the .nc file (assuming one per folder)
nc_files = [f for f in os.listdir(os.path.join(iter_folder,"networks")) if f.endswith(".nc")]
if not nc_files:
    raise FileNotFoundError(f"No .nc file found in {iter_folder}")

nc_file_path = os.path.join(iter_folder,"networks", nc_files[0])

# Load network
network = pypsa.Network(nc_file_path)

# Total system cost (objective) in USD
total_cost = network.objective

# Total energy produced by all generators (MWh)
total_energy_mwh = network.generators_t.p.sum().sum()

# COE in USD/kWh
COE = total_cost / (total_energy_mwh * 1000)  # convert MWh -> kWh

print(f"{COE:.6f}") 
csv_filename="coe_results.csv"
initial_folder = os.path.join(
    r"C:\Users\corra\pypsa-earth\results",
    f"{country_prefix}_0"  # combine prefix + iteration here
)
csv_path = os.path.join(initial_folder, csv_filename)
file_exists = os.path.isfile(csv_path)

with open(csv_path, mode="a", newline="") as f:
    writer = csv.writer(f)
    # Write header if file does not exist
    if not file_exists:
        writer.writerow(["country", "iteration", "COE_USD_per_kWh"])
    writer.writerow([iteration, COE])