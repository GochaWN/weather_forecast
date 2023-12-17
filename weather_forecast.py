import requests
import json
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

def get_coordinates(city):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    else:
        print("Podane miasto nie istnieje. Sprobuj ponownie.")
        return None, None


def get_weather_data(latitude, longitude, timezone, searched_date):
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=rain&daily=rain_sum&timezone={timezone}&start_date={searched_date}&end_date={searched_date}"
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Nie udalo sie pobrac danych. Kod bledu: {response.status_code}")
        return None

def check_rainfall(weather_data):
    if "hourly" in weather_data and "rain" in weather_data["hourly"]:
        rainfall_sum = sum(weather_data["hourly"]["rain"])
        if rainfall_sum > 0.0:
            return "Bedzie padac"
        elif rainfall_sum == 0.0:
            return "Nie bedzie padac"
    return "Nie wiem"

def save_to_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

def load_from_file(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def main():
    print("Witaj w programie prognozy pogody.")

    city = input("Podaj miasto: ").strip()

    latitude, longitude = get_coordinates(city)
    if latitude is None or longitude is None:
        return

    user_date_input = input("Podaj date w formacie YYYY-MM-DD: ").strip()

    if not user_date_input:
        search_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        search_date = user_date_input

    filename = "opady.json"
    stored_data = load_from_file(filename)

    if city in stored_data and search_date in stored_data[city]:
        result = stored_data[city][search_date]
    else:
        weather_data = get_weather_data(latitude, longitude, "Europe%2FLondon", search_date)

        if weather_data:
            result = check_rainfall(weather_data)


            if city not in stored_data:
                stored_data[city] = {}
            stored_data[city][search_date] = result
            save_to_file(stored_data, filename)

    print(f"Prognoza opadow na {search_date} w {city}: {result}")

if __name__ == "__main__":
    main()