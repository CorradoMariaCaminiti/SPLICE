# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 15:09:10 2026

@author: corra
"""

import os
import yaml

def configModifier(it, pypsaPath, path_demand):
    config_path = os.path.join(pypsaPath, "config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    # Update name 
    country_prefix = config["run"]["name"].rsplit("_", 1)[0] 
    config["run"]["name"] = f'{country_prefix}_{it}'

    # Update demand source
    config["load_options"]["disaggregation"]["geospatial"]["source"] = path_demand

    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)