from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Fixture, League, Venue
from .management.commands.geocode import geocode_city
from math import cos, radians
from haversine import haversine, Unit

KM_PER_DEGREE = 112

def filters(fixtures, venue, home_team, guest_team, status, city, radius_km, leagues_id, team, fixture_localtime_from, fixture_localtime_to):

    if venue:
        fixtures = fixtures.filter(venue__name__icontains=venue)

    if home_team:
        fixtures = fixtures.filter(home_team__name__icontains=home_team)

    if guest_team:
        fixtures = fixtures.filter(guest_team__name__icontains=guest_team)

    if status:
        fixtures = fixtures.filter(status=status)

    # "city" alone does a plain text search on the venue's city name; once a
    # radius is also given, "city" instead becomes the center point to
    # geocode below, so the plain text search is skipped in that case.
    if city and not radius_km:
        fixtures = fixtures.filter(venue__city__icontains=city)

    if leagues_id:
        fixtures = fixtures.filter(league__api_id__in=leagues_id)

    if team:
        fixtures = fixtures.filter(home_team__name__icontains=team) | fixtures.filter(guest_team__name__icontains=team)

    if city and radius_km:
        radius_km = float(radius_km)
        city_coordinates = geocode_city(city)

        delta_lat = radius_km / KM_PER_DEGREE
        delta_lon = radius_km / (KM_PER_DEGREE * cos(radians(city_coordinates[0])))

        min_lat = city_coordinates[0] - delta_lat
        max_lat = city_coordinates[0] + delta_lat
        min_lon = city_coordinates[1] - delta_lon
        max_lon = city_coordinates[1] + delta_lon

        candidate_venues = Venue.objects.filter(
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lon,
            longitude__lte=max_lon,
        )

        venues_in_range = []
        for candidate_venue in candidate_venues:
            distance = haversine((candidate_venue.latitude, candidate_venue.longitude), city_coordinates, Unit.KILOMETERS, normalize=True, check=True)
            if distance < radius_km:
                venues_in_range.append(candidate_venue)

        fixtures = fixtures.filter(venue__in=venues_in_range)

    if fixture_localtime_from:
        date_from_parsed = datetime.fromisoformat(fixture_localtime_from)
        fixtures = fixtures.filter(date__gte=date_from_parsed - timedelta(days=1))

    if fixture_localtime_to:
        date_to_parsed = datetime.fromisoformat(fixture_localtime_to)
        fixtures = fixtures.filter(date__lte=date_to_parsed + timedelta(days=1))

    fixtures = list(fixtures)
    if fixture_localtime_from:
        fixtures = [f for f in fixtures if f.fixture_localtime >= date_from_parsed]
    if fixture_localtime_to:
        fixtures = [f for f in fixtures if f.fixture_localtime <= date_to_parsed]

    return fixtures


def matches(request):
    fixtures = Fixture.objects.select_related('venue', 'league', 'home_team', 'guest_team').order_by('date')

    venue = request.GET.get('venue')
    home_team = request.GET.get('home_team')
    guest_team = request.GET.get('guest_team')
    fixture_localtime_from = request.GET.get('fixture_localtime_from')
    fixture_localtime_to = request.GET.get('fixture_localtime_to')
    status = request.GET.get('status')
    city = request.GET.get('city')
    radius_km = request.GET.get('range')
    team = request.GET.get('team')
    leagues_id = request.GET.getlist('leagues')

    fixtures = filters(fixtures, venue, home_team, guest_team, status, city, radius_km, leagues_id, team, fixture_localtime_from, fixture_localtime_to)

    paginator = Paginator(fixtures, 100)
    page_number = request.GET.get('page')
    fixtures = paginator.get_page(page_number)

    context = {
        'fixtures': fixtures,
        'selected_venue': venue,
        'selected_home_team': home_team,
        'selected_guest_team': guest_team,
        'fixture_localtime_from': fixture_localtime_from,
        'fixture_localtime_to': fixture_localtime_to,
        'selected_status': status,
        'selected_city': city,
        'selected_team': team,
        'selected_leagues': leagues_id,
        'selected_range': radius_km,
        'leagues': League.objects.all(),
    }
    return render(request, 'games/games.html', context)
