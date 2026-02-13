import os
import sys
import subprocess
from pathlib import Path

VENV_DIR = Path(".venv")

def run(cmd):
    subprocess.check_call(cmd, shell=False)

def main():

    # 1. Creates venv if it doens't exist
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        print("Virtual environment already exists.")

    # 2. Path to python in venv folder
    if os.name == "nt":
        python = VENV_DIR / "Scripts" / "python.exe"
    else:
        python = VENV_DIR / "bin" / "python"

    # 3. Updates pip
    print("Updating pip...")
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])

    # 4. Install dependecies
    if Path("requirements.txt").exists():
        print("Installing dependecies...")
        run([str(python), "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    else:
        print("requirements.txt not found!")

    print("Environment set up successfully.")

    if os.name == "nt":
        print(f'In order to activate it:\nPowerShell:\n\t{VENV_DIR}/bin/Activate.ps1\nCommand Prompt (cmd):\n\t{VENV_DIR}/Scripts/activate.bat')
    else:
        print(f'In order to activate it:\n\tsource {VENV_DIR}/bin/activate')

if __name__ == "__main__":
    main()