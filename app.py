import streamlit as st
import numpy as np
from scipy.stats import norm

# --- OPTIMIZED STRUCTURAL PARAMETERS ---
PARAMS = {
    "mu_base": 3.0899, "beta_age": -0.0166, "sigma_base": 0.7373,
    "lambda_base": 0.3263, "K": 17.3290, "delta": 0.4349,
    "gamma_EPTB": -0.6465, "gamma_SNPTB": -0.6568,
    "coeff_VIH": 1.4463, "coeff_Hosp": 4.2626, "T_hor": 240 / 365
}

st.set_page_config(page_title="DtD-TB Risk Assessment", page_icon="🩺", layout="centered")

st.title("🩺 Distance-to-Death (DtD)-TB: Individualized Mortality Risk Tool")
st.markdown("""
This application calculates a patient's **Distance-to-Death (DtD)** and 240-day mortality risk 
using a structural Merton Jump-Diffusion framework.
""")

# --- SIDEBAR: PATIENT DATA INPUT ---
st.sidebar.header("Patient Admission Data")
age = st.sidebar.number_input("Age (Years)", min_value=15, max_value=100, value=33)

sex = st.sidebar.radio("Sex", ["Male", "Female"])
weight = st.sidebar.number_input("Admission Weight (kg)", 
                                 min_value=20.0, 
                                 max_value=150.0, 
                                 value=55.0, 
                                 step=0.1, 
                                 format="%.1f")

hiv_status = st.sidebar.radio("HIV Status", ["Negative", "Positive"])
tb_class = st.sidebar.selectbox("TB Classification", 
                                ["Smear Positive Pulmonary (SPPTB)", 
                                 "Smear Negative Pulmonary (SNPTB)", 
                                 "Extra-pulmonary (EPTB)"])
hosp_status = st.sidebar.radio("Initial Management", ["Outpatient", "Hospitalized"])

# --- ADJUSTED BMI CALCULATION LOGIC ---
height = 1.70 if sex == "Male" else 1.60
adjusted_bmi = weight / (height ** 2)

# --- EXECUTION ---
if st.sidebar.button("Run Risk Assessment", type="primary"):
    # 1. Structural Layer Calculation
    tb_effect = PARAMS["gamma_EPTB"] if "Extra" in tb_class else (PARAMS["gamma_SNPTB"] if "Negative" in tb_class else 0)
    mu_i = PARAMS["mu_base"] + (PARAMS["beta_age"] * age) + tb_effect
    sigma_i = PARAMS["sigma_base"] * (1.4463 if hiv_status == "Positive" else 1.0)
    lambda_i = PARAMS["lambda_base"] * (4.2626 if hosp_status == "Hospitalized" else 1.0)
    
    sigma_tot = np.sqrt(sigma_i**2 + lambda_i * PARAMS["delta"]**2)
    mu_adj = mu_i - lambda_i * (np.exp(PARAMS["delta"]**2 / 2) - 1)
    
    # 2. DtD and Risk % Computation
    dtd_score = (np.log(adjusted_bmi / PARAMS["K"]) + (mu_adj - 0.5 * sigma_tot**2) * PARAMS["T_hor"]) / \
                (sigma_tot * np.sqrt(PARAMS["T_hor"]))
    risk_pct = norm.cdf(-dtd_score) * 100 

    # 3. DETERMINE COLOR AND TRIAGE LEVEL
    if risk_pct > 10.0:
        level, color, msg = "LEVEL 1: CRITICAL RISK", "#d9534f", "Immediate intensive clinical and nutritional intervention required."
    elif risk_pct >= 5.0:
        level, color, msg = "LEVEL 2: HIGH RISK", "#f0ad4e", "Close monitoring of physiological parameters and follow-up recommended."
    elif risk_pct >= 2.5:
        level, color, msg = "LEVEL 3: MODERATE RISK", "#3498db", "Regular monitoring of health capital and BMI progression advised."
    else:
        level, color, msg = "LEVEL 4: STABLE / LOW RISK", "#5cb85c", "High biological solvency. Follow standard treatment protocols."

    # 4. TOP METRICS TILES
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Adjusted BMI (kg/m²)", f"{adjusted_bmi:.1f}")
    col2.metric("DtD Score", f"{dtd_score:.2f}")
    col3.metric("Death Risk", f"{risk_pct:.1f}%")
    col4.metric("Survival Prob.", f"{100-risk_pct:.1f}%")

    # --- VISUAL SCALE SECTION ---
    st.markdown("## Physiological Solvency Scale (DtD)")

    # The bar width maps 0-3.5 DtD range to 0-100%
    pos = min(max((dtd_score / 3.5) * 100, 0), 100)
    
    # DYNAMIC COLOR: The 'background-color' of the inner div now uses the 'color' variable
    st.markdown(f"""
    <div style="width: 100%; background-color: #eee; border-radius: 15px; height: 35px; border: 1px solid #ccc; overflow: hidden; position: relative;">
      <div style="width: {pos}%; background-color: {color}; height: 100%; border-radius: 15px; transition: width 1s; display: flex; align-items: center; justify-content: flex-end;">
        <span style="color: white; font-weight: bold; padding-right: 15px;">{dtd_score:.2f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## Mortality Risk Stratification")
    
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; font-size: 14px; margin-top: 5px; font-weight: bold;">
      <span style="color: #d9534f;">Critical (Risk >10%)</span>
      <span style="color: #f0ad4e;">High (5-10%)</span>
      <span style="color: #3498db;">Moderate (2.5-5%)</span>
      <span style="color: #5cb85c;">Stable (<2.5%)</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 5. TRIAGE BOX
    st.markdown(f"""
    <div style="background-color:{color}; color:white; padding:20px; border-radius:10px;">
        <h2 style="margin:0;">{level}</h2>
        <p style="font-size:18px; margin-top:10px;">Calculated risk is <b>{risk_pct:.1f}%</b>. {msg}</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info(f"👈 Enter patient weight and data. Adjusted BMI will be calculated using height = {height}m.")

# --- FOOTNOTES ---
st.markdown("---")
st.markdown("""
<small>
<b>Footnotes & Methodology:</b><br>
1. <b>Adjusted BMI (kg/m²):</b> Calculated as Admission Weight / Height², where Height is standardized at 1.70 m for men and 1.60 m for women per study protocol.<br>
2. <b>Distance-to-Death (DtD):</b> A standardized Z-score representing the number of standard deviations a patient's physiological trajectory lies from the biological failure threshold (K = 17.33 kg/m²).<br>
3. <b>Risk Stratification:</b> Levels are based on the probability of biological default within 240 days: P(Death) = Φ(-DtD).<br>
4. <b>Data Source:</b> Model parameters derived from a retrospective cohort of 15,182 patients at Jamot Hospital of Yaoundé (HJY), Cameroon.
</small>
""", unsafe_allow_html=True)
