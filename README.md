# GameFinder

A Django app for finding football matches by city, distance, team, league and date.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Then open `http://localhost:8000`.

## About the included database

`db.sqlite3` is checked into this repo **as sample data**, so the app works out of the box without needing your own API key — it's a snapshot of real fixtures fetched at some point in time, not live, constantly updated data.

## Refreshing the data yourself

If you want current fixtures instead of the bundled snapshot, you'll need your own [API-Sports](https://www.api-football.com/) key:

1. Create a `.env` file in the project root with:
   ```
   API_SPORTS_KEY=your_key_here
   ```
2. Run:
   ```bash
   python3 manage.py fetch_data
   python3 manage.py geocode
   ```

`fetch_data` pulls fixtures, teams, leagues and venues from the API. `geocode` looks up coordinates and timezones for venues that don't have them yet (used for the distance-based city search).

By default `fetch_data` pulls the 2024 season. To fetch a different season instead:
```bash
python3 manage.py fetch_data --season 2025
```
