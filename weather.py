import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import os
import re
import sys


# Function to change the button color when hovering
def on_enter(event):
    event.widget.config(bg="green", fg="white")

# Function to reset the button color when not hovering
def on_leave(event):
    event.widget.config(bg="skyblue", fg="black")

API_KEY_FILE = 'api_key_tk.txt'

# Function to get the API key from file or prompt the user
def get_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as file:
            return file.read().strip()
    else:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        api_key = simpledialog.askstring("API Key", "Please enter your OpenWeatherMap API key:")
        if api_key:
            with open(API_KEY_FILE, 'w') as file:
                file.write(api_key)
            return api_key
        else:
            messagebox.showerror("API Key Required", "API key is required to run the application")
            sys.exit("API key is required to run the application")

# Function to validate API key
def validate_api_key(api_key):
    test_url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}"
    response = requests.get(test_url)
    if response.status_code == 401:
        raise ValueError("Invalid API Key")
    elif response.status_code == 429:
        raise ValueError("API rate limit exceeded")

# Function to validate input
def validate_input(input_text):
    if len(input_text) < 3:
        return False
    return bool(re.match("^[A-Za-z\s]+$", input_text))

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
    state = geo_data[0].get('state', '').lower()
    country = geo_data[0].get('country', '').lower()
    return lat, lon, state, country

# Function to get weather data
def get_weather():
    city = city_entry.get()
    area = area_entry.get()
    api_key = get_api_key()

    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    if not validate_input(city) or (area and not validate_input(area)):
        messagebox.showwarning("Input Error", "Invalid input. Please enter valid city and area names.")
        return

    try:
        validate_api_key(api_key)
        lat, lon, state, country = get_coordinates(city, api_key)
        if area:
            area_lat, area_lon, area_state, area_country = get_coordinates(area, api_key)
            if area_state != state or area_country != country:
                raise ValueError(f"No area named '{area}' found in city '{city}'")
            lat, lon = area_lat, area_lon

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
        
        result_label.config(text=f"City: {city} ({state}, {country})\nArea: {area}\nTemperature: {temp}°C\nDescription: {description}\n", font=("Helvetica", 14), fg="Green")
        emoji_label.config(text=weather_emoji, font=("Segoe UI Symbol", 30))
    
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            messagebox.showerror("Invalid API Key", "Error 401: Invalid API Key. Please check your API key.")
        elif response.status_code == 404:
            messagebox.showerror("Not Found", "Error 404: Location not found.")
        else:
            messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err} (Status code: {response.status_code})")
    except ValueError as val_err:
        messagebox.showerror("Location Error", f"Location not found: {val_err}")
    except Exception as err:
        messagebox.showerror("Error", f"An error occurred: {err}")

# Function to handle enter key press in entry fields
def on_enter_key(event):
    if event.widget == city_entry:
        area_entry.focus()
    elif event.widget == area_entry:
        get_weather()

# Create the main window
root = tk.Tk()
root.title("Weather App")
root.geometry("400x400")

# Set a modern font
font = ("Helvetica", 14)

# Create and place widgets with improved styling
city_label = tk.Label(root, text="City Name:", font=font)
city_label.pack(pady=10)

city_entry = tk.Entry(root, font=font)
city_entry.pack(pady=5)
city_entry.bind("<Return>", on_enter_key)

area_label = tk.Label(root, text="Area Name (optional):", font=font)
area_label.pack(pady=5)

area_entry = tk.Entry(root, font=font)
area_entry.pack(pady=5)
area_entry.bind("<Return>", on_enter_key)

get_weather_button = tk.Button(root, text="Get Weather", font=font, command=get_weather, bg="skyblue", fg="black",bd=1)
get_weather_button.pack(pady=10)

result_label = tk.Label(root, text="", font=font)
result_label.pack(pady=10)

emoji_label = tk.Label(root, text="", font=("Segoe UI Emoji", 30))
emoji_label.pack(pady=10,anchor=tk.CENTER)

# Bind Enter key to the Get Weather button
# Bind the enter and leave events to the button
get_weather_button.bind("<Enter>", on_enter)
get_weather_button.bind("<Leave>", on_leave)
root.bind("<Return>", lambda event: get_weather())

# Run the Tkinter event loop
root.mainloop()
