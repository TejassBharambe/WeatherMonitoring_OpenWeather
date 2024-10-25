# WeatherMonitoring_OpenWeather

This application fetches real-time weather data for selected cities, processes and stores daily summaries, and sends alerts if the temperature exceeds a user-defined threshold. The application uses the OpenWeatherMap API for weather data, SQLite for data storage, and matplotlib for data visualization. Alerts are sent via email after consecutive updates indicating temperatures above the threshold.

## Table of Contents
- [Features](#features)
- [Dependencies](#dependencies)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Database](#database)
- [Troubleshooting](#troubleshooting)

## Features
- **Real-Time Weather Monitoring**: Retrieves weather data for multiple cities at user-defined intervals.
- **Daily Summaries**: Stores daily weather summaries (average, max, min temperature) in an SQLite database.
- **Temperature Alerts**: Sends an email alert if a city’s temperature exceeds a specified threshold for consecutive updates.
- **Visualization**: Plots daily temperature summaries for historical data visualization.

## Dependencies

This application uses the following dependencies:

- **Python 3.7+**
- `requests`: for API requests.
- `schedule`: for scheduling tasks.
- `sqlite3`: for storing daily weather summaries.
- `matplotlib`: for plotting temperature trends.
- `smtplib`: for sending email alerts.

### Install Dependencies

Install required packages using pip:

```bash
pip install requests schedule matplotlib
```

Docker Image
```
  docker pull tejas033/weather_monitering_system:tejas_first_img
```
TO run Please provide your API key in
```
docker run --rm -e API_KEY=your_api_key_here tejas_first_img
```
