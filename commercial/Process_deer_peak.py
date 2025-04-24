import platform
import csv
from pathlib import Path, PurePath
import datetime


def make_search_paths(root, folder):
    return PurePath.joinpath(PurePath(root), PurePath(folder))


def search_directories(path, file_name):
    paths = []
    for dir_name, sub_dirs, files in Path.walk(path):
        for file in files:
            if file.lower() == file_name:
                paths.append(PurePath.joinpath(dir_name, file))

    return paths


def get_deer_peak_day_range(cz):

    peakspec = dict(
        [
            ("CZ01", 238),
            ("CZ02", 238),
            ("CZ03", 238),
            ("CZ04", 238),
            ("CZ05", 259),
            ("CZ06", 245),
            ("CZ07", 245),
            ("CZ08", 245),
            ("CZ09", 244),
            ("CZ10", 180),
            ("CZ11", 180),
            ("CZ12", 180),
            ("CZ13", 180),
            ("CZ14", 180),
            ("CZ15", 180),
            ("CZ16", 224),
        ]
    )

    start_datetime = datetime.datetime.strptime(
        "2023" + "-" + str(peakspec[cz]), "%Y-%j"
    )
    start_date = start_datetime.date()
    numdays = 3
    date_range = [start_date + datetime.timedelta(days=x) for x in range(numdays)]

    return date_range


def get_time_range():
    start_datetime = datetime.datetime.strptime("15:00:00", "%H:%M:%S")
    num_hours = 5
    datetime_range = [
        start_datetime + datetime.timedelta(hours=x) for x in range(num_hours)
    ]
    time_range = []
    for range_time in datetime_range:
        time_range.append(range_time.time())
    return time_range


def fix_datetime_stamp(datetime_stamp):
    year = 2023
    data_datetime = datetime_stamp.strip()
    data_date = data_datetime.split("  ")[0]
    data_day = int(data_date.split("/")[1])
    data_month = int(data_date.split("/")[0])
    data_time = data_datetime.split("  ")[1]
    data_hour = int(data_time.split(":")[0]) - 1
    return datetime.datetime(year, data_month, data_day, hour=data_hour)


def process(offset, all_files, output_file):

    bad_file_list = []
    for file in all_files:
        parts = PurePath(file).parts
        building_type = parts[offset + 2]
        cz = parts[offset + 1]
        run = parts[offset + 3].split("-")
        measure = run[0]
        system_type = run[1]
        type = run[2]

        peak_days = get_deer_peak_day_range(cz)
        # for day in peak_days:
        #     print(day)
        #

        # This is a little crazy. The data is stamped ending hour. What we want is the
        # hours between 16:00 and 21:00 STANDARD TIME.
        # All of the peak days fall in Day light savings time. So we need to subtract an hour.
        #
        # In the end we get what we want which is the 5 hours starting with the hour ENDING 16:00
        # to the hour ending 20:00 daylight savings time which is the same as the hours BETWEEN 16:00
        # and 21:00 Standard time.

        peak_hours = get_time_range()
        # for hour in peak_hours:
        #     print(hour)

        temperature_accumulator = 0
        electric_usage_accumulator = 0
        with open(file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                datetime_stamp = fix_datetime_stamp(row["Date/Time"])
                if (
                    datetime_stamp.date() in peak_days
                    and datetime_stamp.time() in peak_hours
                ):
                    print(row["Electricity:Facility [J](Hourly) "])
                    print(
                        row[
                            "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)"
                        ]
                    )

            # avg_temperature = temperature_accumulator / 5
            # avg_electricity_usage = electric_usage_accumulator / 5
            # print(
            #     building_type,
            #     measure,
            #     system_type,
            #     type,
            #     cz,
            #     avg_temperature,
            #     avg_electricity_usage,
            # )
        break


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
    results_file_name = "instance-var.csv"

    # Output file_name

    output_file = PurePath.joinpath(
        results_folder,
        PurePath("Deer Peak.csv"),
    )

    # Get all the results files
    all_files = search_directories(search_path, results_file_name)

    process(offset, all_files, output_file)


if __name__ == "__main__":
    main()
