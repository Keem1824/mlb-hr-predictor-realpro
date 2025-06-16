
# real_slate_predictor.py — full slate HR prediction using live data (when online)

# This script requires internet and the following packages:
# pip install pybaseball mlbstatsapi python-dotenv

from pybaseball import statcast_batter, playerid_lookup
from mlbstatsapi import MLBStatsAPI
from data.statcast_features import get_batter_features
from core import predict_hr
import pandas as pd
import numpy as np
import datetime
import os

api = MLBStatsAPI()
today = datetime.date.today().strftime('%Y-%m-%d')

def get_today_games():
    schedule = api.get_schedule(date=today)
    games = []
    for g in schedule['dates'][0]['games']:
        home = g['teams']['home']['team']['name']
        away = g['teams']['away']['team']['name']
        home_id = g['teams']['home']['team']['id']
        away_id = g['teams']['away']['team']['id']
        home_pitcher = g['teams']['away'].get('probablePitcher', {}).get('fullName', 'TBD')
        away_pitcher = g['teams']['home'].get('probablePitcher', {}).get('fullName', 'TBD')
        games.append({'home': home, 'away': away, 'home_pitcher': home_pitcher, 'away_pitcher': away_pitcher,
                      'home_id': home_id, 'away_id': away_id})
    return games

def build_lineup(team_id):
    roster = api.get_team_roster(team_id)
    players = roster['roster']
    result = []
    for p in players:
        name = p['person']['fullName']
        pid = p['person']['id']
        feats = get_batter_features(pid)
        if feats:
            feats['player'] = name
            feats['vs_LHP'] = 0  # stub
            result.append(feats)
    return pd.DataFrame(result)

def simulate_full_real_slate():
    games = get_today_games()
    all_results = []

    for game in games:
        for side, team_id, opp_pitcher in [('home', game['home_id'], game['away_pitcher']),
                                           ('away', game['away_id'], game['home_pitcher'])]:
            team_name = game[side]
            opponent = game['home'] if side == 'away' else game['away']
            lineup = build_lineup(team_id)

            # Mock pitcher stats
            pitcher = {
                'HR_per9': 1.2,
                'avg_pitch_speed': 94,
                'slider_pct': 25,
                'curve_pct': 12,
                'fastball_pct': 60
            }
            weather = {
                'temp': 78,
                'wind_speed': 10,
                'wind_dir': 1,
                'humidity': 50
            }

            result = predict_hr(lineup, pitcher, weather)
            result['team'] = team_name
            result['opponent'] = opponent
            result['pitcher'] = opp_pitcher
            all_results.append(result)

    df = pd.concat(all_results)
    df.to_csv(f"real_slate_hr_predictions_{today}.csv", index=False)
    print(f"✅ Real slate predictions saved: real_slate_hr_predictions_{today}.csv")

if __name__ == "__main__":
    simulate_full_real_slate()
