
# leaderboard.py — loads multi-game slate predictions and displays leaderboard

import pandas as pd

def load_leaderboard(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df = df.sort_values(by='HR_probability', ascending=False)
        return df[['player', 'team', 'opponent', 'HR_probability']]
    except Exception as e:
        return pd.DataFrame()
