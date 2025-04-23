import platform
import csv
import re
from pathlib import Path, PurePath


def make_search_paths(root, folder):
    return PurePath.joinpath(PurePath(root), PurePath(folder))


def search_directories(path, file_name):
    paths = []
    for dir_name, sub_dirs, files in Path.walk(path):
        for file in files:
            if file.lower() == file_name:
                paths.append(PurePath.joinpath(dir_name, file))

    return paths


def by_batch(offset, all_files):
    batches = {}
    for file in all_files:
        parts = PurePath(file).parts
        building_type = parts[offset + 2]
        cz = parts[offset + 1]
        run = parts[offset + 3].split("-")
        measure = run[0]
        system_type = run[1]
        type = run[2]
        if building_type not in batches.keys():
            batches[building_type] = {}
        if measure not in batches[building_type].keys():
            batches[building_type][measure] = []
        batches[building_type][measure].append(file)

    return batches


def write_results(results, output_file):
    energy_results = []
    building_type_list = list(results.keys())
    building_type_list.sort()
    for building_type in building_type_list:
        cz_list = list(results[building_type].keys())
        cz_list.sort()
        for cz in cz_list:
            system_type_list = list(results[building_type][cz].keys())
            system_type_list.sort()
            for system_type in system_type_list:
                measure_list = list(results[building_type][cz][system_type].keys())
                measure_list.sort()
                for measure in measure_list:
                    row = {
                        "Building Type": building_type,
                        "Climate Zone": cz,
                        "System Type": system_type,
                        "Heating Gas Energy": round(
                            results[building_type][cz][system_type][measure][
                                "heating_gas_accumulator"
                            ],
                            2,
                        ),
                        "Heating Electricity Energy": round(
                            results[building_type][cz][system_type][measure][
                                "heating_electricity_accumulator"
                            ],
                            2,
                        ),
                        "Cooling Energy": round(
                            results[building_type][cz][system_type][measure][
                                "cooling_accumulator"
                            ],
                            2,
                        ),
                        "Heating Gas Total Energy": round(
                            results[building_type][cz][system_type][measure][
                                "heating_gas_total_accumulator"
                            ],
                            2,
                        ),
                        "Heating Electricity Total Energy": round(
                            results[building_type][cz][system_type][measure][
                                "heating_electricity_total_accumulator"
                            ],
                            2,
                        ),
                        "Cooling Total Energy": round(
                            results[building_type][cz][system_type][measure][
                                "cooling_total_accumulator"
                            ],
                            2,
                        ),
                    }

                    energy_results.append(row)

    with open(output_file, "a", newline="") as csvfile:
        fieldnames = [
            "Building Type",
            "Climate Zone",
            "System Type",
            "Heating Gas Energy",
            "Heating Electricity Energy",
            "Cooling Energy",
            "Heating Gas Total Energy",
            "Heating Electricity Total Energy",
            "Cooling Total Energy",
        ]
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(energy_results)


def main():

    # root of the DEER package install
    if platform.system() in ["Windows"]:
        root = "C:\\"
        search_folder = "Saved Runs\\"
        results_folder = PurePath("C:\\Results\\")
    elif platform.system() in ["Linux", "Darwin"]:
        root = "/Users/jwj/"
        search_folder = "e_plus_runs/"
        results_folder = PurePath("/Users/jwj/e_plus_results/")
    else:
        print("What, exactly, are you running this on!")
        exit()

    search_path = make_search_paths(root, search_folder)
    offset = len(PurePath(root).parts) + len(PurePath(search_folder).parts)

    # Results file_name
    results_file_name = "instance-var.csv"

    # Get all the results files
    all_files = search_directories(search_path, results_file_name)

    # Create batches by building type and measure, only for the measure type not the baseline type
    batches = by_batch(offset, all_files)

    # Do each batch
    for building_type in batches.keys():
        for measure in batches[building_type].keys():
            print(
                "Processing Building Type: {}, Measure: {}".format(
                    building_type, measure
                )
            )
            results_output_file = PurePath.joinpath(
                results_folder, PurePath("{}-{}.csv".format(building_type, measure))
            )
            column_match_output_file = PurePath.joinpath(
                results_folder,
                PurePath("{}-{}-columns.txt".format(building_type, measure)),
            )
            print("Into Results File {}".format(str(results_output_file)))
            batch = batches[building_type][measure]

            # write_results(results, results_output_file)


if __name__ == "__main__":
    main()
