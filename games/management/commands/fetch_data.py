import requests
import os
import json
import time
import django
from datetime import datetime
from django.core.management.base import BaseCommand


from games.models import League, Venue, Team, Fixture

base_url =  "https://v3.football.api-sports.io/fixtures"
api_key = os.environ.get('API_SPORTS_KEY')

leagues = [6, 39, 40, 41, 42, 45, 46, 47, 48, 61, 62, 63, 64, 66, 78, 79, 80, 81, 88, 89, 94, 96, 106, 135, 140, 144, 145, 146, 203, 204, 206, 208, 218, 220, 345, 346, ]
DEFAULT_SEASON = 2024

payload={}
headers = {
  'x-apisports-key': api_key
}

def save_league(league_data):
    league, created = League.objects.update_or_create(
        api_id = league_data['id'],
        defaults = {
            'name': league_data['name'],
            'country': league_data['country'],
            'logo': league_data['logo'],
        }
    )
    return league

def save_venue(venue_data):
    if venue_data.get('id') is None:
        return None

    venue, created = Venue.objects.update_or_create(
        api_id = venue_data['id'],
        defaults = {
            'name': venue_data['name'],
            'city': venue_data['city'],
        }
    )
    return venue

def save_team(team_data):                     
    team, created = Team.objects.update_or_create(
        api_id = team_data['id'],
        defaults = {
            'name': team_data['name'],
            'logo': team_data['logo'],
        }
    )
    return team


def save_fixture(fixture):
    try:
        league = save_league(fixture['league'])
        venue = save_venue(fixture['fixture']['venue'])
        home_team = save_team(fixture['teams']['home'])
        guest_team = save_team(fixture['teams']['away'])

        fixture, created = Fixture.objects.update_or_create(
            api_id = fixture['fixture']['id'],
            defaults = {
                'date': fixture['fixture']['date'],
                'referee': fixture['fixture']['referee'],
                'round': fixture['league'].get('round', 'N/A'),
                'venue': venue,
                'league': league,
                'home_team': home_team,
                'guest_team': guest_team,
                'home_goals': fixture['goals']['home'] or 0,
                'away_goals': fixture['goals']['away'] or 0,
                'status': fixture['fixture']['status']['short'],
            }
        )
    except Exception as e:
        print(f"Error saving fixture: {e}")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--season', type=int, default=DEFAULT_SEASON)

    def handle(self, *args, **options):
        season = options['season']

        for league in leagues:
            url = base_url + "?" + f"league={league}" + "&" + f"season={season}"
            try:
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    print(f"Error fetching data for league {league}: {response.status_code}")
                    time.sleep(7)  # avoid hitting the 10 requests/minute rate limit
                    continue

                data = response.json()

                for fixture in data['response']:
                    save_fixture(fixture)

                print(f"Fetched league {league}: {len(data['response'])} fixtures")
            except Exception as e:
                print(f"Error fetching data for league {league}: {e}")

            time.sleep(7)  # avoid hitting the 10 requests/minute rate limit

