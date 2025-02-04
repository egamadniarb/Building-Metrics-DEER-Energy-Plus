import pandas as pd
from datetime import datetime, timedelta


def adjust_hours(df, column):
    adjusted_times = []

    for time_str in df[column]:
        date_part, time_part = time_str.split(" ")
        hour, minute = map(int, time_part.split(":"))

        if hour == 24:  # Convert 24:00 to 23:00 of the same day
            new_hour = 23
        else:
            new_hour = hour - 1  # Shift all other hours back by 1

        new_time_str = f"{date_part} {new_hour:02d}:{minute:02d}"
        adjusted_times.append(new_time_str)

    df["datetime"] = pd.to_datetime(adjusted_times, format="%m-%d %H:%M")
    return df


# Example dataset
data = pd.DataFrame(
    {
        "datetime": ["02-01 01:00", "02-01 12:00", "02-01 24:00"],
        "flag": [1, 1, 1],
    }
)


# Apply the correction
data = adjust_hours(data, "datetime")

print(data)
