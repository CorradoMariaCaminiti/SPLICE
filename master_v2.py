import os
import subprocess
from onsset.main_runner import run_onsset_scenario
from onsset.footbridge import footbridge
from onsset.configModifier import configModifier

print("⚠️ Did you check the name in the config in PyPSA?")
input("Press ENTER to continue...")

countryy = "Uganda" 

#Insert here your address of the folder
pypsaPath = r"D:\iep_pypsa-earth" #Substitute here the pypsa position in your machine
conda_exe = os.path.join(r"C:\Users","corra","anaconda3", "Scripts", "conda.exe") #Substitute here the conda.exe
coe = 0.1                # initial guess
prev_coe = float("inf")  # ensures first iteration runs
eps = 1e-4               # convergence tolerance
it = 0
max_it = 20              # safety stop
while abs(coe - prev_coe) > eps and it < max_it: 
    prev_coe = coe
    run_onsset_scenario(countryy, coe, it, pypsaPath) 
    demandLocation = footbridge(it, pypsaPath)
    configModifier(it, pypsaPath, demandLocation)
    conda_env_name = "pypsa-earth"
    
    # Snakemake command
    command = [
        conda_exe, "run", "-n", conda_env_name,
        "snakemake", "-j", "all", "solve_all_networks"
    ]
    
    # Run the command in the workflow folder
    result = subprocess.run(command, cwd=pypsaPath, text=True)
    print("Finito pypsa")
    
    command = [
        conda_exe, "run",
        "-n", conda_env_name,
        "python",
        "calculateCOE.py"
    ]
    
    result = subprocess.run(
        command,
        cwd=pypsaPath,
        text=True,
        capture_output=True
    ) 
    coe_str = result.stdout.strip()
    coe = float(coe_str)  
    print(f"Iteration {it}: COE = {coe:.6f}, ΔCOE = {abs(coe - prev_coe):.6e}")
    it+= 1



