import streamlit as st
import random
import pandas as pd

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
    50: 2.20}

def get_baseline(distance):
    closest = min(sg_baseline.keys(), key=lambda x: abs(x - distance))
    return sg_baseline[closest]

def generate_putt(is_gir):
    return random.randint(5, 35) if is_gir else random.randint(3, 15)

st.set_page_config(page_title="SG Putting Practice", layout="centered")

st.title("SG Putting Practice Tracker")
st.markdown("Simulate a round and track your SG PUTT & Total Score.")

# Session state for holes
if "holes" not in st.session_state:
    st.session_state.holes = []

# Step 1: User input - GIRs
gir_count = st.number_input("Enter number of GIRs (Greens in Regulation):", min_value=0, max_value=18, value=9, step=1)
start_sim = st.button("🎯 Generate Putting Simulation")

# Step 2: Generate holes
if start_sim:
    st.session_state.holes = []

    # Build GIR/non-GIR flags and shuffle them
    gir_flags = [True] * gir_count + [False] * (18 - gir_count)
    random.shuffle(gir_flags)

    for i, is_gir in enumerate(gir_flags):
        distance = generate_putt(is_gir)
        st.session_state.holes.append({
            "hole": i + 1,
            "is_gir": is_gir,
            "distance": distance,
            "putts": None
        })

# Step 3: Input per hole
if st.session_state.holes:
    st.subheader("⛳ Enter Your Putts Per Hole")
    for hole in st.session_state.holes:
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.markdown(f"**Hole {hole['hole']}**")
        with col2:
            st.markdown(f"{'Birdie' if hole['is_gir'] else 'Par'} putt from **{hole['distance']} ft**")
        with col3:
            hole["putts"] = st.number_input(
                f"Putts (Hole {hole['hole']})",
                min_value=1,
                max_value=5,
                key=f"putts_{hole['hole']}"
            )

# Step 4: Calculate SG and Score to Par
if st.button("📊 Calculate SG Putting") and all(h["putts"] is not None for h in st.session_state.holes):
    results = []
    total_sg = 0
    total_score_to_par = 0

    for hole in st.session_state.holes:
        baseline = get_baseline(hole["distance"])
        sg = baseline - hole["putts"]
        total_sg += sg

        # Calculate score to par based on putt type
        if hole["is_gir"]:
            # Birdie putt: 1 = -1, 2 = 0, 3 = +1, etc.
            score_to_par = hole["putts"] - 2
        else:
            # Par putt: 1 = 0, 2 = +1, 3 = +2, etc.
            score_to_par = hole["putts"] - 1

        total_score_to_par += score_to_par

        results.append({
            "Hole": hole["hole"],
            "Distance (ft)": hole["distance"],
            "Putts": hole["putts"],
            "SG": round(sg, 2),
            "Score to Par": score_to_par
        })

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

    # Optional: Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results as CSV", csv, "sg_putting_results.csv", "text/csv")
