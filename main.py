lat_lon = [49.68138481648979, 18.413335864739878]


import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import click


@click.command()
@click.option('--coordinates', type=click.STRING, help='Comma separated latitude,longitude', required=True)
def weather(coordinates):
    coordinates = [c.strip() for c in coordinates.split(',')]
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coordinates[0],
        "longitude": coordinates[1],
        "hourly": [
            "temperature_2m",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "snow_depth",
            "weather_code",
        ],
        "past_days": 3,
        "forecast_days": 4,
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
    hourly_rain = hourly.Variables(2).ValuesAsNumpy()
    hourly_showers = hourly.Variables(3).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(4).ValuesAsNumpy()
    hourly_snow_depth = hourly.Variables(5).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(6).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["rain"] = hourly_rain
    hourly_data["showers"] = hourly_showers
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["snow_depth"] = hourly_snow_depth
    hourly_data["weather_code"] = hourly_weather_code

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    chart = hourly_dataframe.plot(x="date", y="temperature_2m", color="red", zorder=10)
    chart.set_facecolor("black")
    chart.axhline(y=0, color="white", linestyle="--", lw=0.5, zorder=10)
    chart.axvline(
        x=pd.to_datetime(datetime.today()),
        color="white",
        linestyle="-",
        lw=1,
        zorder=10,
    )

    chart.text(
        pd.to_datetime(datetime.today()),
        0.15,
        "today",
        color="white",
        ha="right",
        va="top",
        rotation=90,
        transform=chart.get_xaxis_transform(),
        zorder=10,
    )

    for idx, df in hourly_dataframe.iterrows():
        if df["weather_code"] in [0, 1, 2, 3]:
            # clear, Mainly clear, partly cloudy, and overcast
            pass

        elif df["weather_code"] in [45, 48]:
            # Fog and depositing rime fog
            pass

        elif df["weather_code"] in [51, 53, 55]:
            # Drizzle: Light, moderate, and dense intensity
            chart.axvline(x=df["date"], color="blue", linestyle="-", lw=5)

        elif df["weather_code"] in [56, 57]:
            # 	Freezing Drizzle: Light and dense intensity
            chart.axvline(x=df["date"], color="#27CECA", linestyle="-", lw=5)

        elif df["weather_code"] in [61, 63, 65]:
            # Rain: Slight, moderate and heavy intensity
            chart.axvline(x=df["date"], color="blue", linestyle="-", lw=5)
        elif df["weather_code"] in [66, 67]:
            # Freezing Rain: Light and heavy intensity
            chart.axvline(x=df["date"], color="#27CECA", linestyle="-", lw=5)
        elif df["weather_code"] in [71]:
            # Snow fall: Slight, moderate, and heavy intensity
            chart.axvline(x=df["date"], color="#B8FDCD", linestyle="-", lw=5)
        elif df["weather_code"] in [73]:
            # Snow fall: Slight, moderate, and heavy intensity
            chart.axvline(x=df["date"], color="#42DC71", linestyle="-", lw=5)
        elif df["weather_code"] in [75]:
            # Snow fall: Slight, moderate, and heavy intensity
            chart.axvline(x=df["date"], color="#007624", linestyle="-", lw=5)
        elif df["weather_code"] in [77]:
            # Snow grains
            chart.axvline(x=df["date"], color="#B8FDCD", linestyle="-", lw=5)
        elif df["weather_code"] in [80, 81, 82]:
            # Rain showers: Slight, moderate, and violent
            chart.axvline(x=df["date"], color="blue", linestyle="-", lw=5)
        elif df["weather_code"] in [85, 86]:
            # Snow showers slight and heavy
            chart.axvline(x=df["date"], color="#B8FDCD", linestyle="-", lw=5)
        elif df["weather_code"] in [95, 96, 99]:
            # Snow showers slight and heavy
            chart.axvline(x=df["date"], color="yellow", linestyle="-", lw=5)

    red = mpatches.Patch(color="red", label="Temperature")
    snow_one = mpatches.Patch(color="#B8FDCD", label="Light snowfall")
    snow_two = mpatches.Patch(color="#42DC71", label="Moderate snowfall")
    snow_three = mpatches.Patch(color="#007624", label="Heavy snowfall")
    blue_patch = mpatches.Patch(color="blue", label="Rain")
    blue_patch_two = mpatches.Patch(color="#27CECA", label="Freezing rain")
    black_patch = mpatches.Patch(color="yellow", label="STORM")

    plt.legend(
        handles=[
            red,
            snow_one,
            snow_two,
            snow_three,
            blue_patch,
            blue_patch_two,
            black_patch,
        ],
        loc="upper left",
        prop={"size": 6},
    )
    plt.show()


if __name__ == "__main__":
    weather()
