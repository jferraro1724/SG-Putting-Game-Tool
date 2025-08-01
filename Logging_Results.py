import streamlit as st
import pandas as pd
import os

st.title("📊 Putting Session History & Analysis")

file = "sessions.csv"

if os.path.exists(file):
    df = pd.read_csv(file)
    df["date"] = pd.to_datetime(df["date"])

    st.subheader("🗓 Session Log")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True, hide_index=True)

    st.subheader("📈 Performance Over Time")
    if len(df) >= 2:
        chart_data = df.set_index("date")[["total_sg", "score_to_par"]].dropna()
        st.line_chart(chart_data)
    else:
        st.info("Add at least 2 sessions to see performance trends.")

    st.subheader("🏅 Overall Stats")
    st.metric("Average SG Putting", f"{df['total_sg'].mean():+.2f}")
    st.metric("Average Score to Par", f"{df['score_to_par'].mean():+.2f}")

    if st.button("🗑 Clear All History"):
        os.remove(file)
        st.warning("All history deleted. Please refresh the page.")
else:
    st.info("No session data found yet. Play some rounds and save your sessions!")
