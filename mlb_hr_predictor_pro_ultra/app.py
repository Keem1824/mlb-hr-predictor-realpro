
import streamlit as st
import pandas as pd
import numpy as np
from core import predict_hr
from data.live_roster import get_all_teams, get_current_roster
from data.insights import explain_player
from data.logger import log_event
from data.ask_gpt import ask_gpt
from data.dfs_optimizer import optimize_dfs
from data.salary_mapper import load_salary_csv
from data.leaderboard import load_leaderboard
import datetime

st.set_page_config(page_title="MLB HR Predictor Pro", layout="wide")
st.title("💣 MLB Home Run Predictor Pro")

with st.sidebar:
    st.markdown("### 📋 How to Use")
    st.markdown("1. Select a team")
    st.markdown("2. We pull the latest roster")
    st.markdown("3. Adjust pitcher/weather")
    st.markdown("4. Run prediction")
    st.markdown("5. GPT, DFS value, leaderboard, and download tools")

teams = get_all_teams()
team = st.selectbox("Select Team", teams)
opponent = st.selectbox("Select Opponent", [t for t in teams if t != team])
lineup_data = get_current_roster(team)
st.subheader(f"{team} Lineup (Auto-Populated)")
st.dataframe(lineup_data)

with st.expander("⚙️ Pitcher & Weather Context"):
    HR_per9 = st.slider("HR per 9 innings", 0.5, 2.0, 1.3)
    avg_velo = st.slider("Fastball Velocity", 88.0, 100.0, 94.0)
    slider_pct = st.slider("Slider %", 0, 50, 25)
    curve_pct = st.slider("Curve %", 0, 40, 12)
    fb_pct = st.slider("Fastball %", 20, 80, 60)
    weather = {
        'temp': st.slider("Temp °F", 50, 100, 78),
        'wind_speed': st.slider("Wind mph", 0, 20, 10),
        'wind_dir': st.selectbox("Wind Direction", [-1, 0, 1], format_func=lambda x: {1: 'Out', 0: 'Cross', -1: 'In'}[x]),
        'humidity': st.slider("Humidity %", 20, 100, 55)
    }

pitcher = {
    'HR_per9': HR_per9,
    'avg_pitch_speed': avg_velo,
    'slider_pct': slider_pct,
    'curve_pct': curve_pct,
    'fastball_pct': fb_pct
}

if st.button("Run Prediction"):
    result = predict_hr(lineup_data, pitcher, weather)
    result['Insights'] = result.apply(explain_player, axis=1)
    st.subheader(f"Top HR Threats for {team} vs {opponent}")
    st.dataframe(result.head(5))

    st.markdown("### 📥 Upload DFS Salaries (Optional)")
    uploaded = st.file_uploader("Upload CSV with columns: player,salary")
    if uploaded:
        with open("uploads/salaries.csv", "wb") as f:
            f.write(uploaded.read())
        st.success("Salaries uploaded!")

    salary_dict = load_salary_csv()
    if salary_dict:
        result['salary'] = result['player'].map(salary_dict).fillna(4000)
    else:
        result['salary'] = np.random.randint(3500, 6000, size=len(result))

    st.markdown("### 💸 DFS Value Rankings")
    dfs_df = optimize_dfs(result, salary_dict)
    st.dataframe(dfs_df)

    st.markdown("### 💾 Download Lineup CSV")
    st.download_button("Download Top 9 HR Picks", dfs_df.head(9).to_csv(index=False), "top_hr_lineup.csv", "text/csv")

    st.markdown("### 💬 Ask the Predictor (GPT-Ready)")
    question = st.text_input("Ask about HR threats or players today")
    if st.button("Get AI Insight"):
        gpt_context = result[['player', 'HR_probability', 'Insights']].to_string(index=False)
        st.info(ask_gpt(question, gpt_context))

    st.markdown("### 📋 Summary Report")
    summary = result.head(5).apply(lambda row: f"{row['player']}: {row['Insights']}", axis=1)
    report_text = f"🧠 Top HR Threats for {team} on {datetime.date.today()}\n" + "\n".join(summary)
    st.text_area("Copy your report below", report_text, height=180)

    log_event(team, opponent, len(result))

st.markdown("### 🏆 Leaderboard (Full Slate View)")
lb_path = st.text_input("Upload or paste multi-game CSV path", "simulated_hr_predictions_2025-06-16.csv")
lb_data = load_leaderboard(lb_path)
if not lb_data.empty:
    st.dataframe(lb_data.head(25))
