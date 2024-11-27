"""
Script to run QuakeSupport test run scripts
"""

# --- Import modules ---
import sys
import subprocess

if __name__ == "__main__":
    # --- Dynamic Python interpreter selection ---
    python_interpreter = sys.executable

    # --- Download and prepare input data for QuakeMigrate ---
    subprocess.run([python_interpreter, "get.py"], check=True)
    subprocess.run([python_interpreter, "align.py"], check=True)
    subprocess.run([python_interpreter, "format.py"], check=True)

    # --- Execute QuakeMigrate runs ---
    subprocess.run([python_interpreter, "runs.py"], check=True)

    # --- Generate pick plots from QuakeMigrate output ---
    subprocess.run([python_interpreter, "QMPicksPlot.py"], check=True)

    # --- Prepare input data for GrowClust from QuakeMigrate output ---
    subprocess.run([python_interpreter, "QMevID.py"], check=True)
    subprocess.run([python_interpreter, "QMevlist.py"], check=True)
    subprocess.run([python_interpreter, "QMstlist.py"], check=True)
    subprocess.run([python_interpreter, "generate.py"], check=True)
