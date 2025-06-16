
# slate_optimizer.py — selects best HR threats by value (prob/salary)

def optimize_lineup(df, top_n=9):
    df = df.copy()
    df['salary'] = df.get('salary', 4000)
    df['value'] = df['HR_probability'] / df['salary']
    lineup = df.sort_values(by='value', ascending=False).head(top_n)
    return lineup[['player', 'team', 'opponent', 'HR_probability', 'salary', 'value']]
