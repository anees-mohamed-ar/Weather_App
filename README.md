# Weather App

This is a simple weather application that shows the current weather for a given city and area. It includes two versions: one using Tkinter and one using PyQt5.

## Prerequisites

Make sure you have the following packages installed:

- `requests`
- `PyQt5` (for the PyQt5 version)
- `tkinter` (usually included with Python)

You can install `requests` and `PyQt5` using pip:

```bash
pip install requests
pip install PyQt5
```

## Usage

### 1. Tkinter Version

The Tkinter version of the weather app is in the `weather_TK.py` file.

#### Running the Tkinter App

1. Make sure you have an OpenWeatherMap API key.
2. Run the Tkinter app:

   ```bash
   python weather_TK.py
   ```

3. Enter the city name and area name (optional).
4. Click the "Get Weather" button to see the weather information.

### 2. PyQt5 Version

The PyQt5 version of the weather app is in the `weather_QT.py` file.

#### Running the PyQt5 App

1. Make sure you have an OpenWeatherMap API key.
2. Run the PyQt5 app:

   ```bash
   python weather_QT.py
   ```

3. Enter the city name and area name (optional).
4. Click the "Get Weather" button to see the weather information.

## API Key

The app will ask for your OpenWeatherMap API key the first time you run it. It will save the key in a file called `api_key.txt`. If you need to update the API key, delete the `api_key.txt` file and run the app again to enter a new key.

## Dependencies

- requests
- PyQt5
- tkinter (usually included with Python)

## Notes

- Make sure you have a stable internet connection to fetch weather data.
- The app fetches weather data from OpenWeatherMap API, so ensure your API key is active and valid.

That's it! Enjoy using your weather app. If you have any questions or issues, feel free to ask.
