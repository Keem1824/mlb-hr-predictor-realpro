
# salary_mapper.py — maps uploaded salaries to players

import pandas as pd

def load_salary_csv(path='uploads/salaries.csv'):
    try:
        df = pd.read_csv(path)
        return dict(zip(df['player'], df['salary']))
    except:
        return {}
