import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,QInputDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

import requests

API_KEY_FILE = 'api_key_QT.txt'

# Function to get the API key from file or prompt the user
def get_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as file:
            return file.read().strip()
    else:
        app = QApplication.instance() or QApplication(sys.argv)
        api_key, ok = QInputDialog.getText(None, 'API Key', 'Please enter your OpenWeatherMap API key:')
        if ok and api_key:
            with open(API_KEY_FILE, 'w') as file:
                file.write(api_key)
            return api_key
        else:
            sys.exit("API key is required to run the application")

# Function to validate API key
def validate_api_key(api_key):
    test_url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}"
    response = requests.get(test_url)
    if response.status_code == 401:
        raise ValueError("Invalid API Key")
    elif response.status_code == 429:
        raise ValueError("API rate limit exceeded")

# Function to get geographical coordinates
def get_coordinates(location, api_key):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&appid={api_key}"
    response = requests.get(geo_url)
    response.raise_for_status()
    geo_data = response.json()

    if not geo_data:
        raise ValueError("Location not found")

    lat = geo_data[0]['lat']
    lon = geo_data[0]['lon']
    state = geo_data[0].get('state', '').capitalize()
    country = geo_data[0].get('country', '').upper()
    return lat, lon, state, country

# Function to get weather data
def get_weather(api_key, city, area):
    try:
        validate_api_key(api_key)
        city_lat, city_lon, city_state, city_country = get_coordinates(city, api_key)
        
        if area:
            try:
                area_lat, area_lon, area_state, area_country = get_coordinates(area, api_key)
                
                if area_state != city_state or area_country != city_country:
                    return f"No area named '{area}' found in city '{city}'.", ""
                
                lat, lon = area_lat, area_lon
            except ValueError as val_err:
                return str(val_err), ""
        else:
            lat, lon = city_lat, city_lon

        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(weather_url)
        response.raise_for_status()
        data = response.json()
        
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']
        
        if temp < -100 or temp > 60:
            raise ValueError("Invalid temperature data received.")

        # Map weather condition codes to emojis
        emoji_mapping = {
            '01d': '☀️', '01n': '🌑',
            '02d': '⛅', '02n': '☁️',
            '03d': '☁️', '03n': '☁️',
            '04d': '🌧️', '04n': '🌧️',
            '09d': '🌧️', '09n': '🌧️',
            '10d': '🌦️', '10n': '🌦️',
            '11d': '⛈️', '11n': '⛈️',
            '13d': '❄️', '13n': '❄️',
            '50d': '🌫️', '50n': '🌫️'
        }
        weather_emoji = emoji_mapping.get(icon_code, '❓')
        weather_info = f"City: <b>{city}</b> ({city_state}, {city_country})<br>Area: <b>{area}</b><br>Temperature: <b>{temp}°C</b><br>Description: <b>{description}</b><br>"
        return weather_info, weather_emoji

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return "Error 401: Invalid API Key. Please check your API key.", ""
        elif response.status_code == 404:
            return "Error 404: Location not found.", ""
        else:
            return f"HTTP error occurred: {http_err} (Status code: {response.status_code})", ""
    except ValueError as val_err:
        return f"Location not found: {val_err}", ""
    except Exception as err:
        return f"An error occurred: {err}", ""

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = get_api_key()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Weather App')
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        font = QFont("Helvetica", 18, QFont.Bold)
        emoji_font = QFont("Segoe UI Emoji", 48)

        self.city_label = QLabel('City Name:')
        self.city_label.setFont(font)
        self.city_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.city_label)
        
        self.city_entry = QLineEdit()
        self.city_entry.setFont(font)
        self.city_entry.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.city_entry)

        self.area_label = QLabel('Area Name (optional):')
        self.area_label.setFont(font)
        self.area_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.area_label)
        
        self.area_entry = QLineEdit()
        self.area_entry.setFont(font)
        self.area_entry.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.area_entry)

        self.get_weather_button = QPushButton('Get Weather')
        self.get_weather_button.setFont(font)
        self.get_weather_button.clicked.connect(self.show_weather)
        self.layout.addWidget(self.get_weather_button)

        self.result_label = QLabel('')
        self.result_label.setFont(font)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.result_label)

        self.emoji_label = QLabel('')
        self.emoji_label.setFont(emoji_font)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.emoji_label)

        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.city_entry.returnPressed.connect(self.focus_area_entry)
        self.area_entry.returnPressed.connect(self.show_weather)
        self.get_weather_button.setDefault(True)

    def focus_area_entry(self):
        self.area_entry.setFocus()

    def show_weather(self):
        city = self.city_entry.text()
        area = self.area_entry.text()
        
        if not city:
            QMessageBox.warning(self, "Input Error", "Please enter a city name.")
            return

        weather_info, weather_emoji = get_weather(self.api_key, city, area)
        
        self.result_label.setText(weather_info)
        self.emoji_label.setText(weather_emoji)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WeatherApp()
    ex.show()
    sys.exit(app.exec_())
