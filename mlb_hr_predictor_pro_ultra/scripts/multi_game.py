
# multi_game.py — Simulates full MLB slate HR predictions with optimizer

from data.live_roster import get_all_teams, get_current_roster
from data.slate_optimizer import optimize_lineup
from core import predict_hr
import pandas as pd
import numpy as np
import datetime

def simulate_full_slate():
    teams = get_all_teams()
    all_results = []

    for team in teams:
        opponent = np.random.choice([t for t in teams if t != team])
        lineup = get_current_roster(team)

        pitcher = {
            'HR_per9': np.random.uniform(0.9, 1.5),
            'avg_pitch_speed': np.random.uniform(91, 96),
            'slider_pct': np.random.uniform(15, 35),
            'curve_pct': np.random.uniform(5, 20),
            'fastball_pct': np.random.uniform(50, 70)
        }

        weather = {
            'temp': np.random.randint(65, 95),
            'wind_speed': np.random.randint(0, 15),
            'wind_dir': np.random.choice([-1, 0, 1]),
            'humidity': np.random.randint(40, 80)
        }

        result = predict_hr(lineup, pitcher, weather)
        result['team'] = team
        result['opponent'] = opponent
        result['salary'] = [np.random.randint(3000, 6000) for _ in range(len(result))]
        all_results.append(result)

    df = pd.concat(all_results)
    today = datetime.date.today().strftime('%Y-%m-%d')
    outfile = f'simulated_hr_predictions_{today}.csv'
    df.to_csv(outfile, index=False)

    # Optimize slate
    top_lineup = optimize_lineup(df, top_n=9)
    top_lineup.to_csv(f'optimal_lineup_{today}.csv', index=False)
    print(f"✅ Full slate predictions: {outfile}")
    print(f"✅ Optimal HR lineup: optimal_lineup_{today}.csv")

if __name__ == "__main__":
    simulate_full_slate()
