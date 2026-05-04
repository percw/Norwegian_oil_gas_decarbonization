import subprocess
import sys
import os

def run_pipeline():
    print("🚀 Starting the Norwegian Oil & Gas Decarbonization Pipeline")
    
    scripts = [
        "src/01_data_building.py",
        "src/02_data_cleaning.py",
        "src/03_data_processing.py",
        "src/04_modeling.py",
        "src/05_optimization.py"
    ]
    
    for script in scripts:
        print(f"\n⏳ Running {script}...")
        try:
            # We run the scripts as standalone python processes
            result = subprocess.run([sys.executable, script], check=True, text=True)
            print(f"✅ Successfully finished {script}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error while running {script}. Pipeline stopped.")
            sys.exit(1)

    print("\n🎉 Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()
