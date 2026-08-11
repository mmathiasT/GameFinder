from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Fixture, League

def matches(request):
    fixtures = Fixture.objects.select_related('venue', 'league', 'home_team', 'guest_team')

    league_id = request.GET.get('league')
    venue = request.GET.get('venue')
    home_team = request.GET.get('home_team')
    guest_team = request.GET.get('guest_team')
    fixture_localtime_from = request.GET.get('fixture_localtime_from')
    fixture_localtime_to = request.GET.get('fixture_localtime_to')
    status = request.GET.get('status')
    city = request.GET.get('city')
    team = request.GET.get('team')
    leagues_id = request.GET.getlist('leagues')

    if league_id:
        fixtures = fixtures.filter(league__api_id=league_id)

    if venue:
        fixtures = fixtures.filter(venue__name__icontains=venue)

    if home_team:
        fixtures = fixtures.filter(home_team__name__icontains=home_team)

    if guest_team:
        fixtures = fixtures.filter(guest_team__name__icontains=guest_team)

    if status:
        fixtures = fixtures.filter(status=status)

    if city:
        fixtures = fixtures.filter(venue__city__icontains=city)

    if leagues_id:
       fixtures = fixtures.filter(league__api_id__in=leagues_id)

    if team:
        fixtures = fixtures.filter(home_team__name__icontains=team) | fixtures.filter(guest_team__name__icontains=team)

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

    paginator = Paginator(fixtures, 100)
    page_number = request.GET.get('page')
    fixtures = paginator.get_page(page_number)

    context = {
        'fixtures': fixtures,
        'selected_league': league_id,
        'selected_venue': venue,
        'selected_home_team': home_team,
        'selected_guest_team': guest_team,
        'fixture_localtime_from': fixture_localtime_from,
        'fixture_localtime_to': fixture_localtime_to,
        'selected_status': status,
        'selected_city': city,
        'selected_team': team,
        'selected_leagues': leagues_id,
        'leagues': League.objects.all(),
    }
    return render(request, 'games/games.html', context)
