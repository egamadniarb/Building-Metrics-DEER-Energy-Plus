import platform
import shutil
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
            batches[building_type][measure] = {}
        if system_type not in batches[building_type][measure].keys():
            batches[building_type][measure][system_type] = {}
        if type not in batches[building_type][measure][system_type].keys():
            batches[building_type][measure][system_type][type] = []
        batches[building_type][measure][system_type][type].append(file)

    return batches


def main():

    # root of the DEER package install
    if platform.system() in ["Windows"]:
        root = "D:\\"
        search_folder = "Simulations\\"
        results_folder = PurePath("D:\\Summary Results\\")
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
    results_file_name = "eplustbl.csv"

    # Get all the results files
    all_files = search_directories(search_path, results_file_name)

    # Create batches
    batches = by_batch(offset, all_files)

    # Do each batch
    for building_type in batches.keys():
        if building_type not in ["Asm"]:
            continue
        for measure in batches[building_type].keys():
            for system_type in batches[building_type][measure].keys():
                for type in batches[building_type][measure][system_type].keys():
                    for file in batches[building_type][measure][system_type][type]:
                        parts = PurePath(file).parts
                        building_type = parts[offset + 2]
                        cz = parts[offset + 1]
                        run = parts[offset + 3].split("-")
                        measure = run[0]
                        system_type = run[1]
                        run_type = run[2]
                        results_path = PurePath(
                            "{}/{}-{}-{}-{}-{}-{}".format(
                                results_folder,
                                building_type,
                                measure,
                                system_type,
                                run_type,
                                cz,
                                results_file_name,
                            )
                        )
                        print(results_path)
                        shutil.copy(file, results_path)


if __name__ == "__main__":
    main()
