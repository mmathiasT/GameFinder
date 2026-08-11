from zoneinfo import ZoneInfo

from django.db import models
from django.core.validators import MinLengthValidator

class League(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    logo = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name + ", " + self.country

class Venue(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    timezone_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name + ", "  + self.city
    
class Team(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    code = models.CharField(max_length=3, blank=True)
    logo = models.URLField(blank=True, null=True)
  
    def __str__(self):
        return self.name

class Fixture(models.Model):
    api_id = models.IntegerField(unique=True)
    date = models.DateTimeField()
    referee = models.CharField(max_length=100, null=True)
    round = models.CharField(max_length=100, null=True)

    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    league = models.ForeignKey(League, on_delete=models.SET_NULL, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='home_fixtures')
    guest_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='guest_fixtures')

    home_goals = models.IntegerField(default=0)
    away_goals = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='NS')

    @property
    def fixture_localtime(self):
        if self.venue is None or self.venue.timezone_name is None:
            return self.date.replace(tzinfo=None)
        else:
            return self.date.astimezone(ZoneInfo(self.venue.timezone_name)).replace(tzinfo=None)

    def __str__(self):
        return self.home_team.name + " vs " + self.guest_team.name
