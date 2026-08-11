from django.test import TestCase

from .models import Fixture, League, Team, Venue

class GamesViewTestCases(TestCase):
    def setUp(self):
        pass

    def test_games_view_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class FilterTestCases(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            api_id=39,
            name='Premier League',
            country='England'
        )

        self.venue = Venue.objects.create(
            api_id=1,
            name='Old Trafford',
            city='Manchester',
            timezone_name='Europe/London'
        )

        self.home_team = Team.objects.create(
            api_id=33,
            name='Manchester United',
            country='England'
        )

        self.away_team = Team.objects.create(
            api_id=1,
            name='Arsenal',
            country='England'
        )
        self.fixture = Fixture.objects.create(
            api_id=100,
            date='2024-08-17T15:00:00Z',
            referee='John Doe',
            round='1',
            venue=self.venue,
            league=self.league,
            home_team=self.home_team,
            guest_team=self.away_team,
            status='NS'
        )

        self.second_league = League.objects.create(
            api_id=140,
            name='La Liga',
            country='Spain'
        )

        self.second_venue = Venue.objects.create(
            api_id=2,
            name='Santiago Bernabeu',
            city='Madrid',
            timezone_name='Europe/Madrid'
        )

        self.third_team = Team.objects.create(
            api_id=3,
            name='Real Madrid',
            country='Spain'
        )

        self.fourth_team = Team.objects.create(
            api_id=4,
            name='Barcelona',
            country='Spain'
        )

        self.second_fixture = Fixture.objects.create(
            api_id=200,
            date='2024-08-18T20:00:00Z',
            referee='Jane Doe',
            round='1',
            venue=self.second_venue,
            league=self.second_league,
            home_team=self.third_team,
            guest_team=self.fourth_team,
            status='NS'
        )

    def test_filter_by_multiple_leagues(self):
        response = self.client.get('/?leagues=39&leagues=140')
        self.assertContains(response, 'Manchester United')
        self.assertContains(response, 'Real Madrid')

    def test_reset_shows_all_fixtures(self):
        response = self.client.get('/')
        self.assertContains(response, 'Manchester United')
        self.assertContains(response, 'Real Madrid')

    def test_filter_by_city_Manchester(self):
        response = self.client.get('/?city=Manchester')
        self.assertContains(response, 'Manchester United')

    def test_filter_by_team(self):
        response = self.client.get('/?team=Arsenal')
        self.assertContains(response, 'Arsenal')

    def test_filter_by_date_range(self):
        response = self.client.get('/?fixture_localtime_from=2024-08-01T00:00&fixture_localtime_to=2024-08-31T23:59')
        self.assertContains(response, 'Manchester United')
