from pathlib import Path
import subprocess
import sys
import base64

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Urban Human Life Algorithm", layout="wide")

st.title("Urban Human Life Algorithm Simulator")
st.write("agent-based urban digital twin: routine / mobility / congestion / fatigue / satisfaction / energy / waste / policy counterfactuals")

def show_gif_html(path, width=1050, height=800):
    gif_path = Path(path)
    if gif_path.exists():
        encoded = base64.b64encode(gif_path.read_bytes()).decode()
        components.html(
            f"""
            <div style="display:flex; justify-content:center;">
              <img src="data:image/gif;base64,{encoded}" width="{width}">
            </div>
            """,
            height=height,
        )
    else:
        st.warning(f"{path} is not generated yet.")

tab1, tab2, tab3 = st.tabs(["Urban life animation", "Policy counterfactuals", "Reference data"])

with tab1:
    st.subheader("Synthetic city daily life simulation")
    if st.button("Generate urban simulation"):
        with st.spinner("Generating urban human life simulation..."):
            subprocess.run([sys.executable, "scripts/run_urban_life_sim.py"], check=True)
        st.success("Urban simulation generated.")

    show_gif_html("results/urban_human_life_algorithm.gif", width=1050, height=800)

    if Path("results/urban_life_timeline.png").exists():
        st.image("results/urban_life_timeline.png")

    if Path("results/urban_life_summary.csv").exists():
        df = pd.read_csv("results/urban_life_summary.csv")
        st.write("Key values")
        st.write({
            "final avg satisfaction": float(df["avg_satisfaction"].iloc[-1]),
            "final avg fatigue": float(df["avg_fatigue"].iloc[-1]),
            "peak congestion": float(df["max_congestion"].max()),
            "total energy demand": float(df["energy_demand"].sum()),
            "total spending": float(df["total_spending"].sum()),
            "total waste": float(df["waste_generated"].sum()),
        })
        st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Policy counterfactual causal analysis")
    if st.button("Run policy counterfactuals"):
        with st.spinner("Running policy counterfactuals..."):
            subprocess.run([sys.executable, "scripts/run_counterfactuals.py"], check=True)
        st.success("Counterfactuals complete.")

    if Path("results/urban_policy_counterfactuals.png").exists():
        st.image("results/urban_policy_counterfactuals.png")
    if Path("results/urban_policy_counterfactuals.csv").exists():
        st.dataframe(pd.read_csv("results/urban_policy_counterfactuals.csv"), use_container_width=True)

with tab3:
    st.subheader("Reference / model anchors")
    ref = Path("data/reference/model_reference.csv")
    if ref.exists():
        st.dataframe(pd.read_csv(ref), use_container_width=True)
