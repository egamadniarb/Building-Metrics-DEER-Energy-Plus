import platform
import os
import csv
from pathlib import Path, PurePath


def make_search_paths(root, search_folders):
    search_paths = []
    for folder in search_folders:
        search_paths.append(PurePath.joinpath(Path(root), Path(folder)))
    return search_paths


def search_directories(root_paths, file_name):
    paths = []
    for path in root_paths:
        for dir_name, sub_dirs, files in os.walk(path):
            for file in files:
                if file.lower() == file_name:
                    paths.append(os.path.join(dir_name, file))

    return paths


def process_files(input_files):

    printing = False
    for file in input_files:
        dx_cooling = False
        dx_heating = False
        si = False
        parts = PurePath(file).parts
        measure = parts[3 + offset]
        case = parts[6 + offset]
        rating = parts[7 + offset]
        cz = parts[5 + offset]

        if measure not in measures:
            continue
        if case not in cases:
            continue
        if rating not in ratings:
            continue
        if measure not in outputs.keys():
            outputs[measure] = {}
        if case not in outputs[measure].keys():
            outputs[measure][case] = {}
        if rating not in outputs[measure][case].keys():
            outputs[measure][case][rating] = {}
        with open(file, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 0:
                    if row[0] == "System Sizing Information":
                        if (
                            "System Sizing Information"
                            not in outputs[measure][case][rating].keys()
                        ):
                            outputs[measure][case][rating][
                                "System Sizing Information"
                            ] = {}
                        if (
                            "Data"
                            not in outputs[measure][case][rating][
                                "System Sizing Information"
                            ].keys()
                        ):
                            outputs[measure][case][rating]["System Sizing Information"][
                                "Data"
                            ] = []
                        si = True
                        printing = True
                    elif row[0] == "DX Cooling Coil Standard Rating Information":
                        if (
                            "DX Cooling Coil Standard Rating Information"
                            not in outputs[measure][case][rating].keys()
                        ):
                            outputs[measure][case][rating][
                                "DX Cooling Coil Standard Rating Information"
                            ] = {}
                        if (
                            "Data"
                            not in outputs[measure][case][rating][
                                "DX Cooling Coil Standard Rating Information"
                            ].keys()
                        ):
                            outputs[measure][case][rating][
                                "DX Cooling Coil Standard Rating Information"
                            ]["Data"] = []
                        dx_cooling = True
                        printing = True
                    elif row[0] == "DX Heating Coil Standard Rating Information":
                        if (
                            "DX Heating Coil Standard Rating Information"
                            not in outputs[measure][case][rating].keys()
                        ):
                            outputs[measure][case][rating][
                                "DX Heating Coil Standard Rating Information"
                            ] = {}
                        if (
                            "Data"
                            not in outputs[measure][case][rating][
                                "DX Heating Coil Standard Rating Information"
                            ].keys()
                        ):
                            outputs[measure][case][rating][
                                "DX Heating Coil Standard Rating Information"
                            ]["Data"] = []
                        dx_heating = True
                        printing = True

                    else:
                        if row[0] != "":
                            printing = False
                            si = False
                            dx_cooling = False
                            dx_heating = False
                        if printing:
                            if row[1] == "":
                                row[0] = "CZ"
                                if si:
                                    outputs[measure][case][rating][
                                        "System Sizing Information"
                                    ]["Header"] = row
                                if dx_cooling:
                                    outputs[measure][case][rating][
                                        "DX Cooling Coil Standard Rating Information"
                                    ]["Header"] = row
                                if dx_heating:
                                    outputs[measure][case][rating][
                                        "DX Heating Coil Standard Rating Information"
                                    ]["Header"] = row

                            else:
                                row[0] = cz
                                if si:
                                    outputs[measure][case][rating][
                                        "System Sizing Information"
                                    ]["Data"].append(row)
                                if dx_cooling:
                                    outputs[measure][case][rating][
                                        "DX Cooling Coil Standard Rating Information"
                                    ]["Data"].append(row)
                                if dx_heating:
                                    outputs[measure][case][rating][
                                        "DX Heating Coil Standard Rating Information"
                                    ]["Data"].append(row)


if __name__ == "__main__":
    # root of the DEER package install
    if platform.system() in ["Windows"]:
        root = "Z:\\"
    elif platform.system() in ["Linux", "Darwin"]:
        root = "/Users/jwj/Work/"

    search_folders = ["DEER-Prototypes-EnergyPlus/residential measures/"]
    search_paths = make_search_paths(root, search_folders)

    # Results file_name
    eplustbl_results_file = "eplustbl.csv"

    outputs = {}

    offset = len(PurePath(root).parts)

    measures = [
        "SWHC031-03 Furnace_SFm_1985",
        "SWHC031-03 Furnace_SFm_1975",
        # "SWHC049-03 SEER Rated AC HP_DMo",
        "SWHC049-03 SEER Rated AC HP_SFm_1985",
        # "SWHC031-03 Furnace_DMo",
        # "SWHC031-03 Furnace_MFm_Ex",
        # "SWHC049-03 SEER Rated AC HP_MFm_Ex",
        "SWHC049-03 SEER Rated AC HP_SFm_1975",
    ]

    cases = [
        "SFm&1&rDXHP&Ex&dxHP_equip",
        "SFm&1&rDXGF&Ex&SpaceHtg_eq__GasFurnace",
        "SFm&2&rDXGF&Ex&dxAC_equip",
        "MFm&0&rNCGF&Ex&SpaceHtg_eq__GasFurnace",
        # "DMo&0&rDXHP&New&dxHP_equip",
        "SFm&2&rNCGF&Ex&SpaceHtg_eq__GasFurnace",
        "SFm&2&rDXGF&Ex&SpaceHtg_eq__GasFurnace",
        "MFm&0&rDXGF&Ex&SpaceHtg_eq__GasFurnace",
        "SFm&1&rNCGF&Ex&SpaceHtg_eq__GasFurnace",
        "MFm&0&rDXGF&Ex&dxAC_equip",
        "SFm&2&rDXHP&Ex&dxHP_equip",
        "SFm&1&rDXGF&Ex&dxAC_equip",
        "DMo&0&rDXHP&Ex&dxHP_equip",
        "DMo&0&rDXGF&Ex&SpaceHtg_eq__GasFurnace",
        "DMo&0&rNCGF&Ex&SpaceHtg_eq__GasFurnace",
        # "DMo&0&rDXGF&New&dxAC_equip",
        "DMo&0&rDXGF&Ex&dxAC_equip",
        "MFm&0&rDXHP&Ex&dxHP_equip",
    ]

    ratings = [
        "HSPF_7p0_SEER_13_Pre",
        # "HSPF_9p4_SEER_17_Msr",
        # "HSPF_9p5_SEER_18_Msr",
        "dxAC-Res-SEER-13.0",
        # "dxAC-Res-SEER-14.5",
        # "dxAC-Res-SEER-21.0",
        # "HSPF_9p5_SEER_19_Msr",
        # "dxAC-Res-SEER-15.0",
        # "dxAC-Res-SEER-19.0",
        # "HSPF_8p8_SEER_15_Std",
        # "dxAC-Res-SEER-16.0",
        # "dxAC-Res-SEER-20.0",
        # "HSPF_8p0_SEER_14_Std",
        "AFUE_80_baseline",
        # "dxAC-Res-SEER-18.0",
        # "HSPF_8p2_SEER_14.5_Std",
        # "HSPF_9p0_SEER_16_Msr",
        # "dxAC-Res-SEER-14.0",
        # "HSPF_10p5_SEER_21_Msr",
        # "HSPF_10p0_SEER_20_Msr",
        # "dxAC-Res-SEER-17.0",
    ]

    files = search_directories(search_paths, eplustbl_results_file)

    process_files(files)

    with open("Sizing.csv", "w", newline="") as csvfile:
        result_writer = csv.writer(csvfile)
        for measure in outputs.keys():
            for case in outputs[measure].keys():
                for rating in outputs[measure][case].keys():
                    result_writer.writerow([measure, case, rating])
                    for thing in outputs[measure][case][rating].keys():
                        result_writer.writerow([thing])
                        result_writer.writerow(
                            outputs[measure][case][rating][thing]["Header"]
                        )
                        outputs[measure][case][rating][thing]["Data"].sort(
                            key=lambda row: row[0]
                        )
                        for row in outputs[measure][case][rating][thing]["Data"]:
                            result_writer.writerow(row)
