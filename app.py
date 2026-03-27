import streamlit as st
import numpy as np
from scipy.stats import norm

# --- OPTIMIZED PARAMETERS (HJY Model 1) ---
PARAMS = {
    "mu_base": 3.0899, "beta_age": -0.0166, "sigma_base": 0.7373,
    "lambda_base": 0.3263, "K": 17.3290, "delta": 0.4349,
    "gamma_EPTB": -0.6465, "gamma_SNPTB": -0.6568,
    "coeff_VIH": 1.4463, "coeff_Hosp": 4.2626, "T_hor": 240 / 365
}

st.set_page_config(page_title="DtD-TB Triage", page_icon="🩺", layout="centered")

# --- ADVANCED CSS FOR MOBILE RESPONSIVENESS & LARGE FONTS ---
st.markdown("""
    <style>
    /* Make buttons and inputs large for mobile touch */
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; font-size: 1.2rem !important; }
    
    /* Responsive font for the Scale Labels */
    .scale-labels {
        display: flex; 
        justify-content: space-between; 
        font-weight: bold; 
        margin-top: 10px;
    }
    .scale-labels span {
        font-size: 16px !important; /* Increased font size */
    }
    
    /* Media Query for even larger text on small screens */
    @media (max-width: 600px) {
        .scale-labels span { font-size: 14px !important; }
        [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🩺 Distance-to-Death (DtD)-TB: Individualized Mortality Risk Tool")
st.markdown("""
This application calculates a patient's **Distance-to-Death (DtD)** and 240-day mortality risk 
using a structural Merton Jump-Diffusion framework in tuberculosis (TB) patients.
""")

# --- INPUT SECTION (Sidebar is native responsive: stays on left on PC, hides in menu on Mobile) ---
st.sidebar.header("Patient Admission Data")
age = st.sidebar.number_input("Age (Years)", 15, 100, 33)
sex = st.sidebar.radio("Sex", ["Male", "Female"], horizontal=True)
weight = st.sidebar.number_input("Admission Weight (kg)", 20.0, 150.0, 55.0, step=0.1, format="%.1f")
hiv = st.sidebar.radio("HIV Status", ["Negative", "Positive"], horizontal=True)
tb = st.sidebar.selectbox("TB Classification", ["Smear Positive (SPPTB)", "Smear Negative (SNPTB)", "Extra-pulmonary (EPTB)"])
hosp = st.sidebar.radio("Initial Management", ["Outpatient", "Hospitalized"], horizontal=True)

# Calculation of Adjusted BMI
height = 1.70 if sex == "Male" else 1.60
adj_bmi = weight / (height ** 2)

if st.sidebar.button("RUN RISK ASSESSMENT", type="primary"):
    # 1. Structural Math
    tb_eff = PARAMS["gamma_EPTB"] if "Extra" in tb else (PARAMS["gamma_SNPTB"] if "Negative" in tb else 0)
    mu_i = PARAMS["mu_base"] + (PARAMS["beta_age"] * age) + tb_eff
    sigma_i = PARAMS["sigma_base"] * (1.4463 if hiv == "Positive" else 1.0)
    lambda_i = PARAMS["lambda_base"] * (4.2626 if hosp == "Hospitalized" else 1.0)
    
    sigma_tot = np.sqrt(sigma_i**2 + lambda_i * PARAMS["delta"]**2)
    mu_adj = mu_i - lambda_i * (np.exp(PARAMS["delta"]**2 / 2) - 1)
    
    dtd = (np.log(adj_bmi / PARAMS["K"]) + (mu_adj - 0.5 * sigma_tot**2) * PARAMS["T_hor"]) / \
          (sigma_tot * np.sqrt(PARAMS["T_hor"]))
    risk = norm.cdf(-dtd) * 100 

    # 2. Top Metrics
    st.markdown("### 1. Physiological Reserve")
    m1, m2 = st.columns(2)
    m1.metric("Adjusted BMI", f"{adj_bmi:.1f} kg/m²")
    m2.metric("DtD Score", f"{dtd:.2f}")

    # 3. PHYSIOLOGICAL SOLVENCY SCALE (Placed BEFORE triage box)
    st.markdown("### 2. Physiological Solvency Scale (DtD)")
    
    if risk > 10.0:
        lvl, col, msg = "LEVEL 4: CRITICAL RISK", "#d9534f", "Immediate intensive intervention required."
    elif risk >= 5.0:
        lvl, col, msg = "LEVEL 3: HIGH RISK", "#f0ad4e", "Close monitoring of physiological parameters recommended."
    elif risk >= 2.5:
        lvl, col, msg = "LEVEL 2: MODERATE RISK", "#3498db", "Regular monitoring of health capital advised."
    else:
        lvl, col, msg = "LEVEL 1: STABLE / LOW RISK", "#5cb85c", "High biological solvency profile."

    pos = min(max((dtd / 3.5) * 100, 0), 100)
    st.markdown(f"""
        <div style="width: 100%; background-color: #eee; border-radius: 12px; height: 40px; border: 1px solid #ccc; overflow: hidden; position: relative;">
          <div style="width: {pos}%; background-color: {col}; height: 100%; transition: width 1s; display: flex; align-items: center; justify-content: flex-end;">
            <span style="color: white; font-weight: bold; padding-right: 15px; font-size: 1.1rem;">{dtd:.2f}</span>
          </div>
        </div>
        <div class="scale-labels">
          <span style="color: #d9534f;">Crit (>10%)</span>
          <span style="color: #f0ad4e;">High</span>
          <span style="color: #3498db;">Moderate</span>
          <span style="color: #5cb85c;">Stable (<2.5%)</span>
        </div>
        """, unsafe_allow_html=True)

    # 4. TRIAGE BOX
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background-color:{col}; color:white; padding:25px; border-radius:15px; text-align:center;">
            <h1 style="margin:0; font-size: 2.2rem;">{lvl}</h1>
            <h2 style="margin:10px 0;">Calculated Risk: <b>{risk:.1f}%</b></h2>
            <p style="font-size:1.2rem; opacity: 0.9;">{msg}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write(f"Survival Probability over 240 days: **{100-risk:.1f}%**")

else:
    st.info("👈 **Welcome.** Adjust patient data in the sidebar and click **'RUN RISK ASSESSMENT'** to view the results.")

# --- FOOTNOTES ---
st.markdown("---")
st.markdown("""
<small style="color: #666;">
<b>Footnotes & Methodology:</b><br>
1. <b>Adjusted BMI (kg/m²):</b> Calculated as Admission Weight / Height², where Height is standardized at 1.70 m for men and 1.60 m for women per study protocol.<br>
2. <b>Distance-to-Death (DtD):</b> A standardized Z-score representing the number of standard deviations a patient's physiological trajectory lies from the biological failure threshold (K = 17.33 kg/m²).<br>
3. <b>Risk Stratification:</b> Levels are numbered 1 (Lowest Risk) to 4 (Highest Risk). Thresholds are based on biological default probability within 240 days: P(Death) = Φ(-DtD).<br>
4. <b>Data Source:</b> Model parameters derived from a retrospective cohort of 15,182 patients at Jamot Hospital of Yaoundé (HJY), Cameroon.
</small>
""", unsafe_allow_html=True)
