import requests
import time
import schedule
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os

# Get the API key from an environment variable
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API_KEY environment variable not set.")



#threshold configuration

CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
TEMP_THRESHOLD = 35 # User-configurable threshold for alerts
ALERT_CONSECUTIVE_UPDATES = 2  # Consecutive updates before triggering alert
CHECK_INTERVAL = 0.5  # Reduced interval to 1 minute for testing

# Connect to SQLite database
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()

# Create table for daily weather summaries
cursor.execute('''CREATE TABLE IF NOT EXISTS weather_summary (
                  city TEXT,
                  date TEXT,
                  avg_temp REAL,
                  max_temp REAL,
                  min_temp REAL,
                  dominant_condition TEXT)''')

# Function to insert daily summary
def insert_daily_summary(city, date, avg_temp, max_temp, min_temp, dominant_condition):
    cursor.execute('''INSERT INTO weather_summary (city, date, avg_temp, max_temp, min_temp, dominant_condition)
                      VALUES (?, ?, ?, ?, ?, ?)''', (city, date, avg_temp, max_temp, min_temp, dominant_condition))
    conn.commit()

# Function to fetch weather data from OpenWeatherMap API
def fetch_weather(city):
    #print(f"Fetching weather data for {city}...")  
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    response = requests.get(url).json()

    if response.get('main'):
        temp_k = response['main']['temp']
        temp_c = temp_k - 273.15
        feels_like_k = response['main']['feels_like']
        feels_like_c = feels_like_k - 273.15
        weather_main = response['weather'][0]['main']
        timestamp = response['dt']
        #print(f"Data received for {city}: Temp = {temp_c:.2f}°C, Weather = {weather_main}, feels like ={feels_like_c:.2f} \n\n")  
        
        return {
            'temp': temp_c,
            'feels_like': feels_like_c,
            'weather_main': weather_main,
            'timestamp': timestamp
        }
    else:
        print(f"No valid data received for {city}")  #log
    return None

weather_data = {}

# Function to process and store weather data
def process_weather_data():
    print("Processing weather data...")  # log
    global weather_data

    for city in CITIES:
        data = fetch_weather(city)
        if data:
            timestamp = datetime.utcfromtimestamp(data['timestamp']).strftime('%Y-%m-%d')
            if city not in weather_data:
                weather_data[city] = {}
            
            if timestamp not in weather_data[city]:
                weather_data[city][timestamp] = {'temps': [], 'conditions': []}
            
            weather_data[city][timestamp]['temps'].append(data['temp'])
            weather_data[city][timestamp]['conditions'].append(data['weather_main'])
            #weather_data[city][timestamp]['feels_like_c'].append(data['feels_like'])
            print_weather_data_for_city(city)

            # Calculate daily rollups and aggregates at end of the day
            if len(weather_data[city][timestamp]['temps']) >= 1/CHECK_INTERVAL:
                temps = weather_data[city][timestamp]['temps']
                avg_temp = sum(temps) / len(temps)
                max_temp = max(temps)
                min_temp = min(temps)
                dominant_condition = max(set(weather_data[city][timestamp]['conditions']), key=weather_data[city][timestamp]['conditions'].count)
                
                insert_daily_summary(city, timestamp, avg_temp, max_temp, min_temp, dominant_condition)
                print(f"Stored daily summary for {city} on {timestamp}")  #log
                #visualize_weather_data(city)

alert_count = {city: 0 for city in CITIES}

def print_weather_data_for_city(city):
    if city in weather_data:
        print(f"Weather data for {city}:")
        for date, data in weather_data[city].items():
            temps = data['temps']
            conditions = data['conditions']
            #feel=data['feels_like']
            avg_temp = sum(temps) / len(temps) if temps else 0  # Calculate average temperature
            print(f"Date: {date}, Average Temp: {avg_temp:.2f}, Conditions: {', '.join(conditions)}")
    else:
        print(f"No weather data available for {city}.")

def check_alerts():
    print("Checking alerts...")  #log
    for city in CITIES:
        current_data = fetch_weather(city)
        if current_data:
            if current_data['temp'] > TEMP_THRESHOLD:
                alert_count[city] += 1
            else:
                alert_count[city] = 0

            if alert_count[city] >= ALERT_CONSECUTIVE_UPDATES:
                print(f"Alert: {city} temperature has exceeded {TEMP_THRESHOLD}°C for {ALERT_CONSECUTIVE_UPDATES} consecutive updates!")
                send_email_alert(city, current_data['temp'])
                alert_count[city] = 0

# Function to send email alert
def send_email_alert(city, temp):
    sender_email = "sender mailid"
    receiver_email = "reciver mailid"
    password ="password of sender"

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Weather Alert: {city} Temperature Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"The temperature in {city} has exceeded {TEMP_THRESHOLD}°C. Current temperature: {temp:.2f}°C"
    part = MIMEText(text, "plain")
    message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print(f"Email alert sent for {city}")  #log

# Function to display daily weather summaries
def visualize_weather_data(city):
    cursor.execute('SELECT * FROM weather_summary WHERE city = ?', (city,))
    data = cursor.fetchall()

    dates = [row[1] for row in data]
    avg_temps = [row[2] for row in data]

    plt.plot(dates, avg_temps, label='Avg Temp')
    plt.xlabel('Date')
    plt.ylabel('Temperature (Celsius)')
    plt.title(f'Weather Summary for {city}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

def main():
    schedule.every(CHECK_INTERVAL).minutes.do(process_weather_data)
    schedule.every(CHECK_INTERVAL).minutes.do(check_alerts)

    print("Scheduler started...")  #log
    while True:
        schedule.run_pending()
        time.sleep(1)
        
    

if __name__ == "__main__":
    main()

