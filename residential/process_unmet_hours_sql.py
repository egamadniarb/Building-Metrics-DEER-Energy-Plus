import platform
import csv
import sqlite3
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


def process(offset, all_files, output_file):

    for file in all_files:

        parts = PurePath(file).parts
        cz = parts[offset + 3]
        building_type_root = parts[offset + 1].split("_")[1]
        if building_type_root == "SFm":
            bits = parts[offset + 4].split("&")
            building_type = building_type_root + "_" + bits[1] + "_Story"
            year = parts[offset + 1].split("_")[2]

            if year == "1985" and int(cz[2:4]) < 10:
                continue
            bits2 = parts[offset].split(" ")[1]
            if bits2 == "Furnace":
                bits3 = parts[offset + 5].split("_")[0:2]
                rating = bits3[0] + "_" + bits3[1]
                if bits[2] == "rNCGF":
                    system_type = "Gas_Furnace_NCGF"
                elif bits[2] == "rDXGF":
                    system_type = "Gas_Furnace_DXGF"
                else:
                    system_type = "Shit"
            elif bits2 == "SEER":
                bits3 = parts[offset + 5].split("_")
                if bits[2] == "rDXGF":
                    system_type = "SEER_Rated_DXGF"
                    rating = "SEER_" + bits3[0].split("-")[3].split(".")[0]
                elif bits[2] == "rDXHP":
                    system_type = "SEER_Rated_DXHP"
                    rating = "SEER_" + bits3[3]
                else:
                    system_type = "Shit"
        elif building_type_root == "MFm":
            bits = parts[offset + 4].split("&")
            building_type = building_type_root
            bits2 = parts[offset].split(" ")[1]
            if bits2 == "Furnace":
                bits3 = parts[offset + 5].split("_")[0:2]
                rating = bits3[0] + "_" + bits3[1]
                if bits[2] == "rNCGF":
                    system_type = "Gas_Furnace_NCGF"
                elif bits[2] == "rDXGF":
                    system_type = "Gas_Furnace_DXGF"
                else:
                    system_type = "Shit"
            if bits2 == "SEER":
                bits3 = parts[offset + 5].split("_")
                if bits[2] == "rDXGF":
                    system_type = "SEER_Rated_DXGF"
                    rating = "SEER_" + bits3[0].split("-")[3].split(".")[0]
                elif bits[2] == "rDXHP":
                    system_type = "SEER_Rated_DXHP"
                    rating = "SEER_" + bits3[3]
                else:
                    system_type = "Shit"
        elif building_type_root == "DMo":
            bits = parts[offset + 4].split("&")
            building_type = building_type_root
            bits2 = parts[offset].split(" ")[1]
            if bits2 == "Furnace":
                bits3 = parts[offset + 5].split("_")[0:2]
                rating = bits3[0] + "_" + bits3[1]
                if bits[2] == "rNCGF":
                    system_type = "Gas_Furnace_NCGF"
                elif bits[2] == "rDXGF":
                    system_type = "Gas_Furnace_DXGF"
                else:
                    system_type = "Shit"
            if bits2 == "SEER":
                bits3 = parts[offset + 5].split("_")
                if bits[2] == "rDXGF":
                    system_type = "SEER_Rated_DXGF"
                    rating = "SEER_" + bits3[0].split("-")[3].split(".")[0]
                elif bits[2] == "rDXHP":
                    system_type = "SEER_Rated_DXHP"
                    rating = "SEER_" + bits3[3]
                else:
                    system_type = "Shit"
                if not rating == "SEER_13":
                    continue
        else:
            print("Shit")

        if not system_type == "SEER_Rated_DXGF":
            continue
        # print(building_type, system_type, rating, cz)

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Building Type",
                "System Type",
                "Rating",
                "Climate Zone",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()

        output_row = {
            "Building Type": building_type,
            "System Type": system_type,
            "Rating": rating,
            "Climate Zone": cz,
        }

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Building Type",
                "System Type",
                "Rating",
                "Climate Zone",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writerow(output_row)

        query = "SELECT RowName, Value \
                            FROM TabularDataWithStrings \
                            WHERE TableName = {} and \
                                RowName != {}".format(
            '"Comfort and Setpoint Not Met Summary"',
            '"Time Not Comfortable Based on Simple ASHRAE 55-2004"',
        )

        with sqlite3.connect(file) as conn:
            cur = conn.cursor()
            cur.execute(query)
            facility_occupied_rows = cur.fetchall()
            facility_occupied_heating = float(facility_occupied_rows[0][1].strip())
            facility_occupied_cooling = float(facility_occupied_rows[1][1].strip())

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Time Setpoint Not Met During Occupied Heating",
                "Time Setpoint Not Met During Occupied Cooling",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()

        output_row = {
            "Time Setpoint Not Met During Occupied Heating": facility_occupied_heating,
            "Time Setpoint Not Met During Occupied Cooling": facility_occupied_cooling,
        }

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Time Setpoint Not Met During Occupied Heating",
                "Time Setpoint Not Met During Occupied Cooling",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writerow(output_row)

        # print(facility_occupied_heating, facility_occupied_cooling)

        ######################################################################
        # Occupied Heating
        ######################################################################

        # query = "SELECT RowName, ColumnName, Value \
        #                     FROM TabularDataWithStrings \
        #                     WHERE TableName = {} and \
        #                         ColumnName = {}".format(
        #     '"Time Setpoint Not Met"',
        #     '"During Occupied Heating"',
        # )

        # with sqlite3.connect(file) as conn:
        #     cur = conn.cursor()
        #     cur.execute(query)
        #     system_occupied_rows = cur.fetchall()

        # occupied_heating = []
        # for system_occupied_row in system_occupied_rows:
        #     hours = []
        #     hours.append(system_occupied_row[0].strip())
        #     hours.append(float(system_occupied_row[2].strip()))
        #     occupied_heating.append(hours)

        # with open(output_file, "a", newline="") as csvfile:
        #     fieldnames = [
        #         "Zone",
        #         "Time Setpoint Not Met During Occupied Heating",
        #     ]
        #     writer = csv.DictWriter(csvfile, fieldnames)
        #     writer.writeheader()

        # output_rows = []
        # for system in occupied_heating:
        #     output_row = {
        #         "Zone": system[0],
        #         "Time Setpoint Not Met During Occupied Heating": system[1],
        #     }
        #     output_rows.append(output_row)

        # with open(output_file, "a", newline="") as csvfile:
        #     fieldnames = [
        #         "Zone",
        #         "Time Setpoint Not Met During Occupied Heating",
        #     ]
        #     writer = csv.DictWriter(csvfile, fieldnames)
        #     writer.writerows(output_rows)

        # ######################################################################
        # # Occupied Cooling
        # ######################################################################

        # query = "SELECT RowName, ColumnName, Value \
        #                     FROM TabularDataWithStrings \
        #                     WHERE TableName = {} and \
        #                         ColumnName = {}".format(
        #     '"Time Setpoint Not Met"',
        #     '"During Occupied Cooling"',
        # )

        # with sqlite3.connect(file) as conn:
        #     cur = conn.cursor()
        #     cur.execute(query)
        #     system_occupied_rows = cur.fetchall()

        # occupied_cooling = []
        # for system_occupied_row in system_occupied_rows:
        #     hours = []
        #     hours.append(system_occupied_row[0].strip())
        #     hours.append(float(system_occupied_row[2].strip()))
        #     occupied_cooling.append(hours)

        # with open(output_file, "a", newline="") as csvfile:
        #     fieldnames = [
        #         "Zone",
        #         "Time Setpoint Not Met During Occupied Cooling",
        #     ]
        #     writer = csv.DictWriter(csvfile, fieldnames)
        #     writer.writeheader()

        # output_rows = []
        # for system in occupied_cooling:
        #     output_row = {
        #         "Zone": system[0],
        #         "Time Setpoint Not Met During Occupied Cooling": system[1],
        #     }
        #     output_rows.append(output_row)

        # with open(output_file, "a", newline="") as csvfile:
        #     fieldnames = [
        #         "Zone",
        #         "Time Setpoint Not Met During Occupied Cooling",
        #     ]
        #     writer = csv.DictWriter(csvfile, fieldnames)
        #     writer.writerows(output_rows)

        ######################################################################
        # Heating
        ######################################################################

        query = "SELECT RowName, ColumnName, Value \
                            FROM TabularDataWithStrings \
                            WHERE TableName = {} and \
                                ColumnName = {}".format(
            '"Time Setpoint Not Met"',
            '"During Heating"',
        )

        with sqlite3.connect(file) as conn:
            cur = conn.cursor()
            cur.execute(query)
            system_rows = cur.fetchall()

        heating = []
        for system_row in system_rows:
            hours = []
            hours.append(system_row[0].strip())
            hours.append(float(system_row[2].strip()))
            heating.append(hours)

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Zone",
                "Time Setpoint Not Met During Heating",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()

        output_rows = []
        for system in heating:
            output_row = {
                "Zone": system[0],
                "Time Setpoint Not Met During Heating": system[1],
            }
            output_rows.append(output_row)

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Zone",
                "Time Setpoint Not Met During Heating",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writerows(output_rows)

        ######################################################################
        # Cooling
        ######################################################################

        query = "SELECT RowName, ColumnName, Value \
                            FROM TabularDataWithStrings \
                            WHERE TableName = {} and \
                                ColumnName = {}".format(
            '"Time Setpoint Not Met"',
            '"During Cooling"',
        )

        with sqlite3.connect(file) as conn:
            cur = conn.cursor()
            cur.execute(query)
            system_rows = cur.fetchall()

        cooling = []
        for system_row in system_rows:
            hours = []
            hours.append(system_row[0].strip())
            hours.append(float(system_row[2].strip()))
            cooling.append(hours)

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Zone",
                "Time Setpoint Not Met During Cooling",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()

        output_rows = []
        for system in cooling:
            output_row = {
                "Zone": system[0],
                "Time Setpoint Not Met During Cooling": system[1],
            }
            output_rows.append(output_row)

        with open(output_file, "a", newline="") as csvfile:
            fieldnames = [
                "Zone",
                "Time Setpoint Not Met During Cooling",
            ]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writerows(output_rows)


def main():

    # root of the DEER package install
    if platform.system() in ["Windows"]:
        root = "D:\\Res Runs\\DEER-Prototypes-EnergyPlus\\"
        search_folder = "residential measures\\"
        results_folder = PurePath("D:\\Unmet Hours\\")
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
    results_file_name = "instance-out.sql"

    # Output file_name

    output_file = PurePath.joinpath(
        results_folder,
        PurePath("Unmet Hours.csv"),
    )

    # Get all the results files
    all_files = search_directories(search_path, results_file_name)

    print(len(all_files))

    process(offset, all_files, output_file)


if __name__ == "__main__":
    main()
