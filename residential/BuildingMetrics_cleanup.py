# %%
import os
import shutil

# This will be different on different systems/installions
root_folder = "Z:\\DEER-Prototypes-EnergyPlus"
measure_folder_paths = [
    "residential measures\\SWHC031-03 Furnace",
    "residential measures\\SWHC049-03 SEER Rated AC HP",
]
for measure in measure_folder_paths:
    measure_folder_path = os.path.join(root_folder, measure)
    os.chdir(measure_folder_path)
    current_dir = os.getcwd()
    dir_content = os.listdir(current_dir)
    dir_prototypes = [
        dir for dir in dir_content if os.path.isdir(f"{current_dir}\\{dir}")
    ]

    for prototype in dir_prototypes:
        os.chdir(f"{prototype}/")
        if os.path.isdir(f"runs"):
            print("Removing: " + f"{prototype}\\runs")
            shutil.rmtree(f"runs")
        if os.path.isfile(f"results-profile-elec.csv"):
            print("Removing: " + f"{prototype}\\results-profile-elec.csv")
            os.unlink(f"results-profile-elec.csv")
        if os.path.isfile(f"results-profile-gas.csv"):
            print("Removing: " + f"{prototype}\\results-profile-gas.csv")
            os.unlink(f"results-profile-gas.csv")
        if os.path.isfile(f"results-summary.csv"):
            print("Removing: " + f"{prototype}\\results-summary.csv")
            os.unlink(f"results-summary.csv")
        os.chdir("..")
# %%
