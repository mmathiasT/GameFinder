import time
import requests
from django.core.management.base import BaseCommand
from timezonefinder import TimezoneFinder

from games.models import Venue

base_url = "https://nominatim.openstreetmap.org/search"

MANUAL_COORDINATES = {
}

def geocode_city(city):
    query = f"{city}"

    response = requests.get(base_url, params={'q': query, 'format': 'json', "limit": 1},
        headers={'User-Agent': 'gamefinder-app'},
    )

    if response.status_code != 200:
        print(f"HTTP {response.status_code} for {venue.name} — stopping, try again later")
        return None
    
    geocode_result = response.json()

    if geocode_result is None:
        return  # Stop processing if there was an HTTP error
    
    if geocode_result:
        city_lat = float(geocode_result[0]['lat'])
        city_lon = float(geocode_result[0]['lon'])
        return city_lat, city_lon



def geocode_venue(venue, query):
    response = requests.get(base_url, params={'q': query, 'format': 'json', "limit": 1},
        headers={'User-Agent': 'gamefinder-app'},
    )

    if response.status_code != 200:
        print(f"HTTP {response.status_code} for {venue.name} — stopping, try again later")
        return None

    return response.json()
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        venues = Venue.objects.filter(latitude__isnull=True, longitude__isnull=True)
        for venue in venues:
            query1 = f"{venue.name}, {venue.city}"
            query2 = f"{venue.name}"
            query3 = f"{venue.city}"

            if venue.name in MANUAL_COORDINATES:
                venue.latitude = MANUAL_COORDINATES[venue.name][0]
                venue.longitude = MANUAL_COORDINATES[venue.name][1]
                venue.timezone_name = TimezoneFinder().timezone_at(lng=venue.longitude, lat=venue.latitude)
                
                venue.save()
                print(f"Manually geocoded venue: {venue.name}, {venue.city} to ({venue.latitude}, {venue.longitude})")
                continue

            queries = [
                f"{venue.name}, {venue.city}",
                f"{venue.name}",
                f"{venue.city}",
            ]

            geocode_result = None
            for query in queries:
                geocode_result = geocode_venue(venue, query)

                if geocode_result is None:
                    break  # HTTP error

                if geocode_result:
                    break  # found venue

                time.sleep(1) 

            if geocode_result:
                venue.latitude = float(geocode_result[0]['lat'])
                venue.longitude = float(geocode_result[0]['lon'])
                venue.timezone_name = TimezoneFinder().timezone_at(lng=venue.longitude, lat=venue.latitude)
                venue.save()
                print(f"Geocoded venue: {venue.name}, {venue.city} to ({venue.latitude}, {venue.longitude})")
            elif geocode_result is not None:
                print(f"No geocoding result for venue: {venue.name}, {venue.city}")
            time.sleep(1)   # Sleep for 1 second to avoid hitting the rate limit of the API

