import platform
import os
import csv
import re
import datetime
from pathlib import Path, PurePath


def get_column_headings(file, filter_expression):
    col_list = []
    with open(file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_col_list = list(row.keys())
            break

    for col in all_col_list:
        if re.search(filter_expression, col):
            col_list.append(col)

    return col_list


def is_peak_time(date_time, cz):
    prime_times = {}

    # The times given mean exactly what it says they do!
    # Start Hour = 16
    # End Hour = 21
    # Means data collected between the hours of 16:00 and 21:00
    #
    # Energy+ times are ending times.
    # 17:00 is data collected between 16:00 and 17:00
    #
    # Be carefull!
    #
    prime_times["CZ01"] = {
        "Start Month": "08",
        "End Month": "08",
        "Start Day": "26",
        "End Day": "28",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ02"] = {
        "Start Month": "08",
        "End Month": "08",
        "Start Day": "26",
        "End Day": "28",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ03"] = {
        "Start Month": "08",
        "End Month": "08",
        "Start Day": "26",
        "End Day": "28",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ04"] = {
        "Start Month": "08",
        "End Month": "08",
        "Start Day": "26",
        "End Day": "28",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ05"] = {
        "Start Month": "09",
        "End Month": "09",
        "Start Day": "16",
        "End Day": "18",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ06"] = {
        "Start Month": "09",
        "End Month": "09",
        "Start Day": "02",
        "End Day": "04",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ07"] = {
        "Start Month": "09",
        "End Month": "09",
        "Start Day": "02",
        "End Day": "04",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ08"] = {
        "Start Month": "09",
        "End Month": "09",
        "Start Day": "02",
        "End Day": "04",
        "Start Hour": "16",
        "End Hour": "21",
    }

    prime_times["CZ09"] = {
        "Start Month": "09",
        "End Month": "09",
        "Start Day": "01",
        "End Day": "03",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ10"] = {
        "Start Month": "06",
        "End Month": "07",
        "Start Day": "29",
        "End Day": "01",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ11"] = {
        "Start Month": "06",
        "End Month": "07",
        "Start Day": "29",
        "End Day": "01",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ12"] = {
        "Start Month": "06",
        "End Month": "07",
        "Start Day": "29",
        "End Day": "01",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ13"] = {
        "Start Month": "06",
        "End Month": "07",
        "Start Day": "29",
        "End Day": "01",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ14"] = {
        "Start Month": "06",
        "End Month": "07",
        "Start Day": "29",
        "End Day": "01",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ15"] = {
        "Start Month": "06",
        "End Month": "07",
        "Start Day": "29",
        "End Day": "01",
        "Start Hour": "16",
        "End Hour": "21",
    }
    prime_times["CZ16"] = {
        "Start Month": "08",
        "End Month": "08",
        "Start Day": "12",
        "End Day": "14",
        "Start Hour": "16",
        "End Hour": "21",
    }

    datadate = date_time.split("  ")[0].strip()

    # Just to make things more confusing I subtract 1 from the E+ hour because Python
    # can't understand 24:00. They are now data from the hour starting at
    datahour = int(date_time.split("  ")[1].strip().split(":")[0]) - 1

    datamonth = datadate.split("/")[0]
    dataday = datadate.split("/")[1]
    data_timestamp = datetime.datetime.strptime(
        "{}/{} {}".format(datamonth, dataday, datahour), "%m/%d %H"
    )
    start_timestamp = datetime.datetime.strptime(
        "{}/{} {}".format(
            prime_times[cz]["Start Month"],
            prime_times[cz]["Start Day"],
            prime_times[cz]["Start Hour"],
        ),
        "%m/%d %H",
    )
    end_timestamp = datetime.datetime.strptime(
        "{}/{} {}".format(
            prime_times[cz]["End Month"],
            prime_times[cz]["End Day"],
            prime_times[cz]["End Hour"],
        ),
        "%m/%d %H",
    )

    if (
        data_timestamp.month >= start_timestamp.month
        and data_timestamp.month <= end_timestamp.month
    ):
        if (
            data_timestamp.day >= start_timestamp.day
            and data_timestamp.day <= end_timestamp.day
        ):
            if (
                data_timestamp.hour >= start_timestamp.hour
                and data_timestamp.hour < end_timestamp.hour
            ):
                return True

    return False


def compute_averages(file_name, data_keys, tce_keys, cooling, cz):
    heating_accumulators = {}
    heating_counters = {}
    heating_averages = {}
    peak_heating_accumulators = {}
    peak_heating_counters = {}
    peak_heating_averages = {}
    cooling_accumulators = {}
    cooling_counters = {}
    cooling_averages = {}
    peak_cooling_accumulators = {}
    peak_cooling_counters = {}
    peak_cooling_averages = {}

    for key in data_keys:
        heating_accumulators[key] = 0
        heating_counters[key] = 0
        cooling_accumulators[key] = 0
        cooling_counters[key] = 0
        peak_heating_accumulators[key] = 0
        peak_heating_counters[key] = 0
        peak_cooling_accumulators[key] = 0
        peak_cooling_counters[key] = 0

    with open(file_name, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key in data_keys:
                # Skip zeros and less than 2 minutes run time (2/60)
                # obvously 0 is less than 2/60 but I leave it like this to be self
                # documenting
                if float(row[key]) == 0 or float(row[key]) < 2 / 60:
                    pass
                else:
                    # if there is no A/C
                    if not cooling:
                        heating_accumulators[key] += float(row[key])
                        heating_counters[key] += 1
                        if is_peak_time(row["Date/Time"], cz):
                            peak_heating_accumulators[key] += float(row[key])
                            peak_heating_counters[key] += 1
                    else:
                        # If cooling coil energy use is zero, it's heating
                        if float(row[tce_keys[key.split()[1]]]) == 0:
                            heating_accumulators[key] += float(row[key])
                            heating_counters[key] += 1
                            if is_peak_time(row["Date/Time"], cz):
                                peak_heating_accumulators[key] += float(row[key])
                                peak_heating_counters[key] += 1
                        # Otherwise cooling
                        else:
                            cooling_accumulators[key] += float(row[key])
                            cooling_counters[key] += 1
                            if is_peak_time(row["Date/Time"], cz):
                                peak_cooling_accumulators[key] += float(row[key])
                                peak_cooling_counters[key] += 1

    for key in data_keys:
        if heating_counters[key] != 0:
            heating_averages[key] = heating_accumulators[key] / heating_counters[key]
        else:
            heating_averages[key] = 0
        if peak_heating_counters[key] != 0:
            peak_heating_averages[key] = (
                peak_heating_accumulators[key] / peak_heating_counters[key]
            )
        else:
            peak_heating_averages[key] = 0

        if cooling_counters[key] != 0:
            cooling_averages[key] = cooling_accumulators[key] / cooling_counters[key]
        else:
            cooling_averages[key] = 0
        if peak_cooling_counters[key] != 0:
            peak_cooling_averages[key] = (
                peak_cooling_accumulators[key] / peak_cooling_counters[key]
            )
        else:
            peak_cooling_averages[key] = 0

    building_heating_counter = 0
    building_heating_sum = 0
    building_cooling_counter = 0
    building_cooling_sum = 0
    peak_building_heating_counter = 0
    peak_building_heating_sum = 0
    peak_building_cooling_counter = 0
    peak_building_cooling_sum = 0
    for key in data_keys:
        if heating_averages[key] != 0:
            building_heating_counter += 1
            building_heating_sum += heating_averages[key]
        if peak_heating_averages[key] != 0:
            peak_building_heating_counter += 1
            peak_building_heating_sum += peak_heating_averages[key]
        if cooling_averages[key] != 0:
            building_cooling_counter += 1
            building_cooling_sum += cooling_averages[key]
        if peak_cooling_averages[key] != 0:
            peak_building_cooling_counter += 1
            peak_building_cooling_sum += peak_cooling_averages[key]

    building_heating_average = (
        building_heating_sum / building_heating_counter
        if building_heating_counter != 0
        else "N/A"
    )
    peak_building_heating_average = (
        peak_building_heating_sum / peak_building_heating_counter
        if peak_building_heating_counter != 0
        else "N/A"
    )

    building_cooling_average = (
        building_cooling_sum / building_cooling_counter
        if building_cooling_counter != 0
        else "N/A"
    )
    peak_building_cooling_average = (
        peak_building_cooling_sum / peak_building_cooling_counter
        if peak_building_cooling_counter != 0
        else "N/A"
    )

    return (
        heating_averages,
        cooling_averages,
        building_heating_average,
        building_cooling_average,
        peak_heating_averages,
        peak_cooling_averages,
        peak_building_heating_average,
        peak_building_cooling_average,
    )


def process_files(offset, input_files, output_file, cooling):
    equip_results = []
    building_results = []
    peak_equip_results = []
    peak_building_results = []
    for file in input_files:
        # Get the "Part Load Ratio" columns, these are the values to average

        PLR_columns = get_column_headings(file, "Part Load Ratio")

        # Get the "Cooling Coil Total Cooling Energy" columns
        TCE_columns = []
        TCE_lookup = {}
        if cooling:
            TCE_columns = get_column_headings(file, "Cooling Coil Total Cooling Energy")

            # Make the TCE columns into a lookup table (dict) based on the
            # equipment name (2nd word in the column header)

            TCE_lookup = {col.split()[1]: col for col in TCE_columns}

        # What exactly is being worked on is encoded in the full path name of the
        # file being processed. Pull out the CZ and rating. This is windows so
        # double backslash (yuck)

        parts = PurePath(file).parts
        rating = parts[7 + offset]
        cz = parts[5 + offset]

        (
            heating_averages,
            cooling_averages,
            building_heating_average,
            building_cooling_average,
            peak_heating_averages,
            peak_cooling_averages,
            peak_building_heating_average,
            peak_building_cooling_average,
        ) = compute_averages(file, PLR_columns, TCE_lookup, cooling, cz)

        res_row = {}
        res_row["CZ"] = cz
        res_row["Rating"] = rating
        res_row["Type"] = "Heating"
        res_row.update(heating_averages)
        equip_results.append(res_row)

        res_row = {}
        res_row["CZ"] = cz
        res_row["Rating"] = rating
        res_row["Type"] = "Cooling"
        res_row.update(cooling_averages)
        equip_results.append(res_row)

        res_row = {}
        res_row["CZ"] = cz
        res_row["Rating"] = rating
        res_row["Type"] = "Heating"
        res_row.update(peak_heating_averages)
        peak_equip_results.append(res_row)

        res_row = {}
        res_row["CZ"] = cz
        res_row["Rating"] = rating
        res_row["Type"] = "Cooling"
        res_row.update(peak_cooling_averages)
        peak_equip_results.append(res_row)

        building_results.append(
            {
                "CZ": cz,
                "Rating": rating,
                "Heating": building_heating_average,
                "Cooling": building_cooling_average,
            }
        )

        peak_building_results.append(
            {
                "CZ": cz,
                "Rating": rating,
                "Heating": peak_building_heating_average,
                "Cooling": peak_building_cooling_average,
            }
        )

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Equipment Averages"])

    with open(output_file, "a", newline="") as csvfile:
        fieldnames = ["CZ", "Rating", "Type"] + PLR_columns
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(equip_results)

    with open(output_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Building Averages"])

    with open(output_file, "a", newline="") as csvfile:
        fieldnames = ["CZ", "Rating", "Heating", "Cooling"]
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(building_results)

    with open(output_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Peak Time Equipment Averages"])

    with open(output_file, "a", newline="") as csvfile:
        fieldnames = ["CZ", "Rating", "Type"] + PLR_columns
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(peak_equip_results)

    with open(output_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Peak Time Building Averages"])

    with open(output_file, "a", newline="") as csvfile:
        fieldnames = ["CZ", "Rating", "Heating", "Cooling"]
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(peak_building_results)


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


def get_files(
    offset, all_files, target_group, target_measure, target_case, target_rating
):

    results = []

    for file in all_files:
        parts = PurePath(file).parts
        group = parts[2 + offset]
        measure = parts[3 + offset]
        case = parts[6 + offset]
        rating = parts[7 + offset]
        cz = parts[5 + offset]

        if (
            group == target_group
            and measure == target_measure
            and case == target_case
            and rating == target_rating
        ):
            results.append(file)

    results.sort(key=lambda part: PurePath(part).parts[5 + offset])

    return results


def main():

    # root of the DEER package install
    if platform.system() in ["Windows"]:
        root = "Z:\\"
    elif platform.system() in ["Linux", "Darwin"]:
        root = "/Users/jwj/Work/"

    search_folders = ["DEER-Prototypes-EnergyPlus/residential measures/"]
    search_paths = make_search_paths(root, search_folders)
    offset = len(PurePath(root).parts)

    # Results file_name
    results_file_name = "eplusvar.csv"

    # Get all the results files
    all_files = search_directories(search_paths, results_file_name)

    # what measure, climate zone, case and efficiency rating is encoded into the parts of the
    # full path name to the results file as follows:
    #
    # measure group
    #   measure
    #       climate zone
    #           case
    #               rating
    #
    # for example:
    #
    # SWHC031-03 Furnace
    #   SWHC031-03 Furnace_DMo
    #       <climate zone>
    #           DMo&0&rDXGF&Ex&SpaceHtg_eq__GasFurnace
    #               AFUE_80_baseline                        <-- Wanted
    #               Msr-Res-GasFurnace-AFUE92-ECM
    #               Msr-Res-GasFurnace-AFUE95-ECM
    #               Msr-Res-GasFurnace-AFUE97-ECM
    #           DMo&0&rDXGF&New&SpaceHtg_eq__GasFurnace
    #               AFUE_80_baseline
    #               Msr-Res-GasFurnace-AFUE92-ECM
    #               Msr-Res-GasFurnace-AFUE95-ECM
    #               Msr-Res-GasFurnace-AFUE97-ECM
    #           DMo&0&rNCGF&Ex&SpaceHtg_eq__GasFurnace
    #               AFUE_80_baseline                        <-- Wanted
    #               Msr-Res-GasFurnace-AFUE92-ECM
    #               Msr-Res-GasFurnace-AFUE95-ECM
    #               Msr-Res-GasFurnace-AFUE97-ECM
    #           DMo&0&rNCGF&New&SpaceHtg_eq__GasFurnace
    #               AFUE_80_baseline
    #               Msr-Res-GasFurnace-AFUE92-ECM
    #               Msr-Res-GasFurnace-AFUE95-ECM
    #               Msr-Res-GasFurnace-AFUE97-ECM

    # make a list of the runs to do
    runs = []

    # Furnace DMo
    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_DMo"
    run["Case"] = "DMo&0&rDXGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = True
    run["Output"] = "DMo_Furnace_Ex_DXGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_DMo"
    run["Case"] = "DMo&0&rNCGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = False
    run["Output"] = "DMo_Furnace_Ex_NCGF_AFUE_80_averages.csv"
    runs.append(run)

    # Furnace SFm
    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1975"
    run["Case"] = "SFm&1&rDXGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = True
    run["Output"] = "SFm_Furnace_1975_1_Floor_DXGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1975"
    run["Case"] = "SFm&2&rDXGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = True
    run["Output"] = "SFm_Furnace_1975_2_Floors_DXGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1975"
    run["Case"] = "SFm&1&rNCGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = False
    run["Output"] = "SFm_Furnace_1975_1_Floor_NCGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1975"
    run["Case"] = "SFm&2&rNCGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = False
    run["Output"] = "SFm_Furnace_1975_2_Floors_NCGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1985"
    run["Case"] = "SFm&1&rDXGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = True
    run["Output"] = "SFm_Furnace_1985_1_Floor_DXGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1985"
    run["Case"] = "SFm&2&rDXGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = True
    run["Output"] = "SFm_Furnace_1985_2_Floors_DXGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1985"
    run["Case"] = "SFm&1&rNCGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = False
    run["Output"] = "SFm_Furnace_1985_1_Floor_NCGF_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_SFm_1985"
    run["Case"] = "SFm&2&rNCGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = False
    run["Output"] = "SFm_Furnace_1985_2_Floors_NCGF_AFUE_80_averages.csv"
    runs.append(run)

    # Furnace MFm
    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_MFm_Ex"
    run["Case"] = "MFm&0&rDXGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = True
    run["Output"] = "MFm_DXGF_Ex_AFUE_80_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC031-03 Furnace"
    run["Measure"] = "SWHC031-03 Furnace_MFm_Ex"
    run["Case"] = "MFm&0&rNCGF&Ex&SpaceHtg_eq__GasFurnace"
    run["Rating"] = "AFUE_80_baseline"
    run["Cooling"] = False
    run["Output"] = "MFm_NCGF_Ex_AFUE_80_averages.csv"
    runs.append(run)

    # Heat Pump DMo
    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_DMo"
    run["Case"] = "DMo&0&rDXGF&Ex&dxAC_equip"
    run["Rating"] = "dxAC-Res-SEER-13.0"
    run["Cooling"] = True
    run["Output"] = "DMo_SEER Rated AC_HP Ex_DXGF_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_DMo"
    run["Case"] = "DMo&0&rDXHP&Ex&dxHP_equip"
    run["Rating"] = "HSPF_7p0_SEER_13_Pre"
    run["Cooling"] = True
    run["Output"] = "DMo_SEER Rated AC_HP Ex_DXHP_SEER_13_averages.csv"
    runs.append(run)

    # Heat Pump SFm
    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1975"
    run["Case"] = "SFm&1&rDXGF&Ex&dxAC_equip"
    run["Rating"] = "dxAC-Res-SEER-13.0"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1975_1_Floor_DXGF_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1975"
    run["Case"] = "SFm&2&rDXGF&Ex&dxAC_equip"
    run["Rating"] = "dxAC-Res-SEER-13.0"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1975_2_Floors_DXGF_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1975"
    run["Case"] = "SFm&1&rDXHP&Ex&dxHP_equip"
    run["Rating"] = "HSPF_7p0_SEER_13_Pre"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1975_1_Floor_DXHP_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1975"
    run["Case"] = "SFm&2&rDXHP&Ex&dxHP_equip"
    run["Rating"] = "HSPF_7p0_SEER_13_Pre"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1975_2_Floors_DXHP_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1985"
    run["Case"] = "SFm&1&rDXGF&Ex&dxAC_equip"
    run["Rating"] = "dxAC-Res-SEER-13.0"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1985_1_Floor_DXGF_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1985"
    run["Case"] = "SFm&2&rDXGF&Ex&dxAC_equip"
    run["Rating"] = "dxAC-Res-SEER-13.0"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1985_2_Floors_DXGF_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1985"
    run["Case"] = "SFm&1&rDXHP&Ex&dxHP_equip"
    run["Rating"] = "HSPF_7p0_SEER_13_Pre"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1985_1_Floor_DXHP_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_SFm_1985"
    run["Case"] = "SFm&2&rDXHP&Ex&dxHP_equip"
    run["Rating"] = "HSPF_7p0_SEER_13_Pre"
    run["Cooling"] = True
    run["Output"] = "SFm_SEER Rated AC_HP_1985_2_Floors_DXHP_SEER_13_averages.csv"
    runs.append(run)

    # Heat Pump MFm

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_MFm_Ex"
    run["Case"] = "MFm&0&rDXGF&Ex&dxAC_equip"
    run["Rating"] = "dxAC-Res-SEER-13.0"
    run["Cooling"] = True
    run["Output"] = "MFm_DXGF_SEER_13_averages.csv"
    runs.append(run)

    run = {}
    run["Group"] = "SWHC049-03 SEER Rated AC HP"
    run["Measure"] = "SWHC049-03 SEER Rated AC HP_MFm_Ex"
    run["Case"] = "MFm&0&rDXHP&Ex&dxHP_equip"
    run["Rating"] = "HSPF_7p0_SEER_13_Pre"
    run["Cooling"] = True
    run["Output"] = "MFm_DXHP_SEER_13_averages.csv"
    runs.append(run)

    # and do them

    # open an audit file
    audit_flie = open("audit.log", "w")

    for run in runs:
        results = get_files(
            offset, all_files, run["Group"], run["Measure"], run["Case"], run["Rating"]
        )
        audit_flie.write(
            "Measure Group: "
            + run["Group"]
            + " Measure: "
            + run["Measure"]
            + " Case: "
            + run["Case"]
            + " Rating: "
            + run["Rating"]
            + "\n"
        )
        audit_flie.write("\n")
        for results_file in results:
            audit_flie.write(results_file + "\n")
        audit_flie.write("\n")

        process_files(
            offset,
            results,
            run["Output"],
            run["Cooling"],
        )

    audit_flie.close()


if __name__ == "__main__":
    main()
