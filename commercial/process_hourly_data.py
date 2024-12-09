import platform
import csv
import re
from pathlib import Path, PurePath


def get_all_column_headings(file):
    col_list = []
    with open(file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_col_list = list(row.keys())
            break

    return all_col_list


def find_column_headings(file, filter_expression):
    col_list = []
    all_col_list = get_all_column_headings(file)

    for col in all_col_list:
        if re.search(filter_expression, col):
            col_list.append(col)

    return col_list


def make_search_paths(root, search_folders):
    search_paths = []
    for folder in search_folders:
        search_paths.append(PurePath.joinpath(PurePath(root), PurePath(folder)))
    return search_paths


def search_directories(root_paths, file_name):
    paths = []
    for path in root_paths:
        for dir_name, sub_dirs, files in Path.walk(path):
            for file in files:
                if file.lower() == file_name:
                    paths.append(PurePath.joinpath(dir_name, file))

    return paths


def set_up(offset, all_files):

    results = {}

    for file in all_files:
        parts = PurePath(file).parts
        building_type = parts[6 + offset].split("&")[0]
        measure = parts[7 + offset].split("-")[4]
        system_type = parts[7 + offset].split("-")[3]
        cz = parts[5 + offset]
        if building_type not in results.keys():
            results[building_type] = {}
        if cz not in results[building_type].keys():
            results[building_type][cz] = {}
        if system_type not in results[building_type][cz].keys():
            results[building_type][cz][system_type] = {}
        if measure not in results[building_type][cz][system_type].keys():
            results[building_type][cz][system_type][measure] = {}
        results[building_type][cz][system_type][measure]["file"] = file
        results[building_type][cz][system_type][measure]["columns"] = {}

        results[building_type][cz][system_type][measure]["columns"]["all"] = (
            get_all_column_headings(file)
        )
        results[building_type][cz][system_type][measure]["columns"]["heating"] = (
            find_column_headings(file, "Heating Coil .* Energy")
        )
        results[building_type][cz][system_type][measure]["columns"]["cooling"] = (
            find_column_headings(file, "Cooling Coil .* Energy")
        )
        results[building_type][cz][system_type][measure]["columns"]["fan"] = (
            find_column_headings(file, "Fan Runtime Fraction")
        )

    return results


def print_it(results):
    building_type_list = list(results.keys())
    building_type_list.sort()
    for building_type in building_type_list:
        print(building_type)
        cz_list = list(results[building_type].keys())
        cz_list.sort()
        for cz in cz_list:
            print("\t{}".format(cz))
            system_type_list = list(results[building_type][cz].keys())
            system_type_list.sort()
            for system_type in system_type_list:
                print("\t\t{}".format(system_type))
                measure_list = list(results[building_type][cz][system_type].keys())
                measure_list.sort()
                for measure in measure_list:
                    print("\t\t\t{}".format(measure))
                    print(
                        "\t\t\t{}".format(
                            results[building_type][cz][system_type][measure]["file"]
                        )
                    )
                    for set in ["heating", "cooling", "fan"]:
                        print("\t\t\t\t{} Columns: ".format(set))
                        for col in results[building_type][cz][system_type][measure][
                            "columns"
                        ][set]:
                            print("\t\t\t\t\t{}".format(col))


def main():

    # root of the DEER package install
    if platform.system() in ["Windows"]:
        root = "Z:\\"
    elif platform.system() in ["Linux", "Darwin"]:
        root = "/Users/jwj/Work/"
    else:
        print("What, exactly, are you running this on!")
        exit()

    search_folders = ["DEER-Prototypes-EnergyPlus-SWHC009/commercial measures/"]
    search_paths = make_search_paths(root, search_folders)
    offset = len(PurePath(root).parts)

    # Results file_name
    results_file_name = "instance-var.csv"

    # Get all the results files
    all_files = search_directories(search_paths, results_file_name)

    results = set_up(offset, all_files)

    print_it(results)


if __name__ == "__main__":
    main()
