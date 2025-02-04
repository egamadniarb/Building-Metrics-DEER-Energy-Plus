import pandas as pd
from datetime import datetime


def analyze_schedule(data):
    data["datetime"] = pd.to_datetime(data["datetime"])
    data["date"] = data["datetime"].dt.date
    data["hour"] = data["datetime"].dt.hour
    data["weekday"] = data["datetime"].dt.weekday

    # Group data by date, separating weekdays and weekends
    weekday_grouped = data[data["weekday"] < 5].groupby("date")
    weekend_grouped = data[data["weekday"] >= 5].groupby("date")

    def get_schedule_ranges(df):
        schedule_ranges = []
        on_period = None
        for _, row in df.iterrows():
            if row["flag"] == 1:
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
        schedule_ranges = get_schedule_ranges(group)
        formatted_schedule = format_schedule(schedule_ranges)

        if formatted_schedule != prev_weekday_schedule:
            schedule_output += f"Starting on {date}, the schedule is on for weekdays: {formatted_schedule}\n"

        prev_weekday_schedule = formatted_schedule

    for date, group in weekend_grouped:
        schedule_ranges = get_schedule_ranges(group)
        formatted_schedule = format_schedule(schedule_ranges)

        if formatted_schedule != prev_weekend_schedule:
            schedule_output += f"Starting on {date}, the schedule is on for weekends: {formatted_schedule}\n"

        prev_weekend_schedule = formatted_schedule

    return schedule_output.strip()


# Example usage
data = pd.DataFrame(
    {
        "datetime": pd.date_range(start="2024-01-01", periods=24 * 91, freq="h"),
        "flag": ([0] * 3 + [1] * 3 + [0] * 3 + [1] * 5 + [0] * 10) * 31
        + ([0] * 6 + [1] * 3 + [0] * 6 + [1] * 2 + [0] * 7) * 29
        + ([0] * 5 + [1] * 6 + [0] * 5 + [1] * 3 + [0] * 5) * 31,
    }
)

print(analyze_schedule(data))
