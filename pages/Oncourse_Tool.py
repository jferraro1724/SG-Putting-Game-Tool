import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SG Baseline Table ---
sg_baseline = {
    1: 1.00,
    3: 1.05,
    5: 1.15,
    7: 1.30,
    9: 1.45,
    11: 1.50,
    13: 1.55,
    15: 1.65,
    17: 1.75,
    19: 1.85,
    21: 2.00,
    23: 2.00,
    25: 2.05,
    27: 2.05,
    30: 2.10,
    35: 2.10,
    40: 2.15,
    45: 2.15,
    50: 2.20
}

def get_baseline(distance):
    closest = min(sg_baseline.keys(), key=lambda x: abs(x - distance))
    return sg_baseline[closest]

def score_to_par(putt_for, putts):
    putt_for_offset = {
        "Eagle": -2,
        "Birdie": -1,
        "Par": 0,
        "Bogey": 1,
        "Double Bogey": 2
    }
    # Score to par = (putts taken - 1) + offset based on what putt was for
    return putts - 1 + putt_for_offset[putt_for]

st.set_page_config(page_title="On-Course Putting Tracker", layout="centered")

st.title("On-Course Putting Tracker")
st.markdown("Enter your real on-course putting data hole-by-hole to track SG Putting and Score to Par.")

holes = 18
putt_options = ["Eagle", "Birdie", "Par", "Bogey", "Double Bogey"]

# Store hole data in session state
if "hole_data" not in st.session_state:
    st.session_state.hole_data = [{"hole": i+1, "distance": 10, "putts": 2, "putt_for": "Par"} for i in range(holes)]

st.subheader("⛳ Enter Your On-Course Putting Data")

for i in range(holes):
    col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
    with col1:
        st.markdown(f"**Hole {i+1}**")
    with col2:
        putt_for = st.selectbox(
            "Initial putt for",
            putt_options,
            index=putt_options.index(st.session_state.hole_data[i]["putt_for"]),
            key=f"putt_for_{i}"
        )
        st.session_state.hole_data[i]["putt_for"] = putt_for
    with col3:
        dist = st.number_input(
            f"Distance to hole (ft)",
            min_value=1,
            max_value=100,
            value=st.session_state.hole_data[i]["distance"],
            step=1,
            key=f"distance_{i}"
        )
        st.session_state.hole_data[i]["distance"] = dist
    with col4:
        putts = st.number_input(
            f"Putts taken",
            min_value=1,
            max_value=10,
            value=st.session_state.hole_data[i]["putts"],
            step=1,
            key=f"putts_{i}"
        )
        st.session_state.hole_data[i]["putts"] = putts

def calculate_results():
    results = []
    total_sg = 0
    total_score_to_par = 0

    for hole in st.session_state.hole_data:
        dist = hole["distance"]
        putts = hole["putts"]
        putt_for = hole["putt_for"]
        baseline = get_baseline(dist)
        sg = baseline - putts
        total_sg += sg

        score = score_to_par(putt_for, putts)
        total_score_to_par += score

        results.append({
            "Hole": hole["hole"],
            "Distance (ft)": dist,
            "Putts": putts,
            "Initial Putt For": putt_for,
            "SG": round(sg, 2),
            "Score to Par": score
        })

    return results, total_sg, total_score_to_par

if st.button("📊 Calculate SG Putting"):
    if any(h["distance"] is None or h["putts"] is None or h["putt_for"] is None for h in st.session_state.hole_data):
        st.warning("Please fill in all distances, putts, and initial putt for.")
    else:
        results, total_sg, total_score_to_par = calculate_results()
        st.subheader("📋 Results Summary")
        df = pd.DataFrame(results)
        st.dataframe(df.style.format({
            "SG": "{:+.2f}",
            "Score to Par": "{:+}"
        }), use_container_width=True,
        hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📈 Total SG Putting", f"{total_sg:+.2f}")
        with col2:
            st.metric("🏁 Score to Par", f"{total_score_to_par:+}")

        if st.button("💾 Save This Session"):
            session = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_sg": round(total_sg, 2),
                "score_to_par": total_score_to_par,
                "type": "oncourse"
            }
            file = "sessions.csv"
            df_session = pd.DataFrame([session])
            if os.path.exists(file):
                df_session.to_csv(file, mode='a', header=False, index=False)
            else:
                df_session.to_csv(file, index=False)
            st.success("✅ On-course session saved!")
