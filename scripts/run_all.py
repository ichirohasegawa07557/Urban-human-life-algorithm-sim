import subprocess
import sys

subprocess.run([sys.executable, "scripts/run_urban_life_sim.py"], check=True)
subprocess.run([sys.executable, "scripts/run_counterfactuals.py"], check=True)
print("All urban human life outputs complete.")
