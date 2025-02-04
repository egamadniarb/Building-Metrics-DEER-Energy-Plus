import platform
import csv
import re
from pathlib import Path, PurePath
import pandas as pd
from datetime import datetime


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


def should_ignore(building_type, system_type, column):

    if system_type in ["cDXGF", "cDXHP", "cPTAC"]:
        if not re.search("SZ-CAV", column, flags=re.IGNORECASE):
            return True
        if building_type in ["EPr", "ESe", "EUn", "MBT", "RFF", "RSD", "RtL", "Htl"]:
            if re.search("KITCHEN", column, flags=re.IGNORECASE):
                return True
        if building_type in ["EUn"]:
            if re.search("DORM", column, flags=re.IGNORECASE):
                return True
    if system_type in ["cPVVG"]:
        if not re.search("SZ-VAV", column, flags=re.IGNORECASE):
            return True
        if building_type in ["ECC", "Htl"]:
            if re.search("KITCHEN", column, flags=re.IGNORECASE):
                return True
        if building_type in ["MBT"]:
            if re.search("LAB", column, flags=re.IGNORECASE):
                return True
        if re.search(" ATU", column, flags=re.IGNORECASE):
            return True
    return False


def set_up(offset, all_files):

    results = {}

    for file in all_files:
        parts = PurePath(file).parts
        building_type = parts[6 + offset].split("&")[0]
        measure = parts[7 + offset].split("-")[4]
        system_type = parts[7 + offset].split("-")[3]
        cz = parts[5 + offset]

        # if measure not in ["Unocc"]:
        #     continue

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

        heating_gas = find_column_headings(file, "Heating Coil NaturalGas Energy")
        heating_electricity = find_column_headings(
            file, "Heating Coil Electricity Energy"
        )
        cooling = find_column_headings(file, "Cooling Coil .* Energy")
        schedules = find_column_headings(file, "SCHEDULE")

        results[building_type][cz][system_type][measure]["columns"]["heating_gas"] = {}
        for heating_col in heating_gas:
            # if should_ignore(building_type, system_type, heating_col):
            #     results[building_type][cz][system_type][measure]["columns"][
            #         "heating_gas"
            #     ][heating_col] = "Ignore"
            #     continue
            for schedule_col in schedules:
                if heating_col.split(":")[0].removesuffix(
                    "HEATING COIL"
                ) == schedule_col.split(":")[0].removesuffix("OPERATION SCHEDULE"):
                    results[building_type][cz][system_type][measure]["columns"][
                        "heating_gas"
                    ][heating_col] = schedule_col

        results[building_type][cz][system_type][measure]["columns"][
            "heating_electricity"
        ] = {}
        for heating_col in heating_electricity:
            # if should_ignore(building_type, system_type, heating_col):
            #     results[building_type][cz][system_type][measure]["columns"][
            #         "heating_electricity"
            #     ][heating_col] = "Ignore"
            #     continue
            for schedule_col in schedules:
                if heating_col.split(":")[0].removesuffix(
                    "HEATING COIL"
                ) == schedule_col.split(":")[0].removesuffix("OPERATION SCHEDULE"):
                    results[building_type][cz][system_type][measure]["columns"][
                        "heating_electricity"
                    ][heating_col] = schedule_col

        results[building_type][cz][system_type][measure]["columns"]["cooling"] = {}
        for cooling_col in cooling:
            # if should_ignore(building_type, system_type, cooling_col):
            #     results[building_type][cz][system_type][measure]["columns"]["cooling"][
            #         cooling_col
            #     ] = "Ignore"
            #     continue
            for schedule_col in schedules:
                if cooling_col.split(":")[0].removesuffix(
                    "COOLING COIL"
                ) == schedule_col.split(":")[0].removesuffix("OPERATION SCHEDULE"):
                    results[building_type][cz][system_type][measure]["columns"][
                        "cooling"
                    ][cooling_col] = schedule_col

    return results


def analyze_schedule(data, flag):

    def adjust_hours(df, column):
        adjusted_times = []

        for time_str in df[column]:
            date_part, time_part = time_str.split("  ")
            hour, minute, second = map(int, time_part.split(":"))

            if hour == 24:  # Convert 24:00 to 23:00 of the same day
                new_hour = 23
            else:
                new_hour = hour - 1  # Shift all other hours back by 1

            new_time_str = (
                f"{date_part.strip()} {new_hour:02d}:{minute:02d}:{second:02d}"
            )
            adjusted_times.append(new_time_str)

        df["datetime"] = pd.to_datetime(adjusted_times, format="%m/%d %H:%M:%S")
        return df

    data = adjust_hours(data, "Date/Time")
    data["date"] = data["datetime"].dt.date
    data["hour"] = data["datetime"].dt.hour
    data["weekday"] = data["datetime"].dt.weekday

    # Group data by date, separating weekdays and weekends
    weekday_grouped = data[data["weekday"] < 5].groupby("date")
    weekend_grouped = data[data["weekday"] >= 5].groupby("date")

    def get_schedule_ranges(df, flag):
        schedule_ranges = []
        on_period = None
        for _, row in df.iterrows():
            if row[flag] == 1:
                if on_period is None:
                    on_period = row["hour"]
            else:
                if on_period is not None:
                    schedule_ranges.append((on_period, row["hour"]))
                    on_period = None
        if on_period is not None:
            schedule_ranges.append(
                (on_period, 24)
            )  # Ensure the last on-period is captured correctly
        return schedule_ranges

    def format_schedule(ranges):
        return (
            ", ".join([f"{start}:00 to {end}:00" for start, end in ranges])
            if ranges
            else "N/A"
        )

    schedule_output = ""
    prev_weekday_schedule = None
    prev_weekend_schedule = None

    for date, group in weekday_grouped:
        schedule_ranges = get_schedule_ranges(group, flag)
        formatted_schedule = format_schedule(schedule_ranges)

        if formatted_schedule != prev_weekday_schedule:
            schedule_output += f"Starting on {date}, the schedule is on for weekdays: {formatted_schedule}\n"

        prev_weekday_schedule = formatted_schedule

    for date, group in weekend_grouped:
        schedule_ranges = get_schedule_ranges(group, flag)
        formatted_schedule = format_schedule(schedule_ranges)

        if formatted_schedule != prev_weekend_schedule:
            schedule_output += f"Starting on {date}, the schedule is on for weekends: {formatted_schedule}\n"

        prev_weekend_schedule = formatted_schedule

    return schedule_output.strip()


def process_schedules(results):

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
                    file = results[building_type][cz][system_type][measure]["file"]

                    for heating_gas_col in results[building_type][cz][system_type][
                        measure
                    ]["columns"]["heating_gas"].keys():
                        # if (
                        #     results[building_type][cz][system_type][measure]["columns"][
                        #         "heating_gas"
                        #     ][heating_gas_col]
                        #     == "Ignore"
                        # ):
                        #     continue

                        data = pd.read_csv(
                            file,
                            usecols=[
                                "Date/Time",
                                results[building_type][cz][system_type][measure][
                                    "columns"
                                ]["heating_gas"][heating_gas_col],
                            ],
                        )
                        print(
                            "\n\nBuilding Type: {} CZ: {} System Type: {} Measure: {} Coil: {}".format(
                                building_type,
                                cz,
                                system_type,
                                measure,
                                heating_gas_col,
                            )
                        )
                        print(
                            analyze_schedule(
                                data,
                                results[building_type][cz][system_type][measure][
                                    "columns"
                                ]["heating_gas"][heating_gas_col],
                            )
                        )

                    for heating_electricity_col in results[building_type][cz][
                        system_type
                    ][measure]["columns"]["heating_electricity"].keys():
                        # if (
                        #     results[building_type][cz][system_type][measure]["columns"][
                        #         "heating_electricity"
                        #     ][heating_electricity_col]
                        #     == "Ignore"
                        # ):
                        #     continue

                        data = pd.read_csv(
                            file,
                            usecols=[
                                "Date/Time",
                                results[building_type][cz][system_type][measure][
                                    "columns"
                                ]["heating_electricity"][heating_electricity_col],
                            ],
                        )
                        print(
                            "\n\nBuilding Type: {} CZ: {} System Type: {} Measure: {} Coil: {}".format(
                                building_type,
                                cz,
                                system_type,
                                measure,
                                heating_electricity_col,
                            )
                        )
                        print(
                            analyze_schedule(
                                data,
                                results[building_type][cz][system_type][measure][
                                    "columns"
                                ]["heating_electricity"][heating_electricity_col],
                            )
                        )

                    for cooling_col in results[building_type][cz][system_type][measure][
                        "columns"
                    ]["cooling"].keys():
                        # if (
                        #     results[building_type][cz][system_type][measure]["columns"][
                        #         "cooling"
                        #     ][cooling_col]
                        #     == "Ignore"
                        # ):
                        #     continue

                        data = pd.read_csv(
                            file,
                            usecols=[
                                "Date/Time",
                                results[building_type][cz][system_type][measure][
                                    "columns"
                                ]["cooling"][cooling_col],
                            ],
                        )
                        print(
                            "\n\nBuilding Type: {} CZ: {} System Type: {} Measure: {} Coil: {}".format(
                                building_type,
                                cz,
                                system_type,
                                measure,
                                cooling_col,
                            )
                        )
                        print(
                            analyze_schedule(
                                data,
                                results[building_type][cz][system_type][measure][
                                    "columns"
                                ]["cooling"][cooling_col],
                            )
                        )


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

    process_schedules(results)


if __name__ == "__main__":
    main()
