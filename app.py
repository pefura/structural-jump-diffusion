import streamlit as st
import numpy as np
from scipy.stats import norm

# --- 1. OPTIMIZED STRUCTURAL PARAMETERS ---
PARAMS = {
    "mu_base": 3.0899, "beta_age": -0.0166, "sigma_base": 0.7373,
    "lambda_base": 0.3263, "K": 17.3290, "delta": 0.4349,
    "gamma_EPTB": -0.6465, "gamma_SNPTB": -0.6568,
    "coeff_VIH": 1.4463, "coeff_Hosp": 4.2626, "T_hor": 240 / 365
}

# --- 2. SCREEN CONFIGURATION ---
st.set_page_config(page_title="DtD-TB Tool", page_icon="🩺", layout="centered")

# --- 3. CUSTOM CSS FOR MOBILE TOUCH & LARGE FONTS ---
st.markdown("""
    <style>
    /* Full-width buttons for thumb accessibility */
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: bold; font-size: 1.2rem !important; background-color: #2c7bb6; color: white; margin-top: 10px; }
    
    /* Scale labels styling with large font */
    .scale-labels { display: flex; justify-content: space-between; font-weight: bold; margin-top: 10px; }
    .scale-labels span { font-size: 16px !important; }
    
    /* Triage Box fonts */
    .triage-lvl { font-size: 2.0rem !important; margin: 0; font-weight: bold; line-height: 1.1; }
    .triage-risk { font-size: 1.7rem !important; margin: 10px 0; font-weight: bold; }
    
    /* Responsive adjustment for small screens */
    @media (max-width: 600px) {
        .scale-labels span { font-size: 13px !important; }
        .triage-lvl { font-size: 1.6rem !important; }
        .triage-risk { font-size: 1.3rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP HEADER ---
st.title("🩺 Distance-to-Death (DtD)-TB: Individualized Mortality Risk Tool")
st.markdown("""
This application calculates a patient's **Distance-to-Death (DtD)** and 240-day mortality risk 
using a structural Merton Jump-Diffusion framework in tuberculosis (TB) patients.
""")

# --- 5. STEP 1: PATIENT DATA INPUT (CENTERED FOR MOBILE) ---
st.header("Step 1: Enter Patient Data")
with st.container(border=True):
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age (Years)", 15, 100, 33)
    with col_b:
        sex = st.radio("Sex", ["Male", "Female"], horizontal=True)
    
    weight = st.number_input("Admission Weight (kg)", 20.0, 150.0, 55.0, step=0.1, format="%.1f")
    
    hiv = st.radio("HIV Status", ["Negative", "Positive"], horizontal=True)
    tb = st.selectbox("TB Classification", ["Smear Positive Pulmonary (SPPTB)", "Smear Negative Pulmonary (SNPTB)", "Extra-pulmonary (EPTB)"])
    hosp = st.radio("Initial Management", ["Outpatient", "Hospitalized"], horizontal=True)
    
    calculate_btn = st.button("RUN RISK ASSESSMENT", type="primary")

# Adjusted BMI logic
height = 1.70 if sex == "Male" else 1.60
adj_bmi = weight / (height ** 2)

# --- 6. STEP 2: RESULTS (DISPLAYS UPON CALCULATION) ---
if calculate_btn:
    # A. Structural Math logic
    tb_eff = PARAMS["gamma_EPTB"] if "Extra" in tb else (PARAMS["gamma_SNPTB"] if "Negative" in tb else 0)
    mu_i = PARAMS["mu_base"] + (PARAMS["beta_age"] * age) + tb_eff
    sigma_i = PARAMS["sigma_base"] * (1.4463 if hiv == "Positive" else 1.0)
    lambda_i = PARAMS["lambda_base"] * (4.2626 if hosp == "Hospitalized" else 1.0)
    
    sigma_tot = np.sqrt(sigma_i**2 + lambda_i * PARAMS["delta"]**2)
    mu_adj = mu_i - lambda_i * (np.exp(PARAMS["delta"]**2 / 2) - 1)
    
    dtd_score = (np.log(adj_bmi / PARAMS["K"]) + (mu_adj - 0.5 * sigma_tot**2) * PARAMS["T_hor"]) / (sigma_tot * np.sqrt(PARAMS["T_hor"]))
    risk_of_death = norm.cdf(-dtd_score) * 100 

    # B. Triage Logic (Level 1 = Lowest Risk)
    if risk_of_death > 10.0:
        lvl, col, msg = "LEVEL 4: CRITICAL RISK", "#d9534f", "Urgent intensive intervention required."
    elif risk_of_death >= 5.0:
        lvl, col, msg = "LEVEL 3: HIGH RISK", "#f0ad4e", "Close clinical monitoring recommended."
    elif risk_of_death >= 2.5:
        lvl, col, msg = "LEVEL 2: MODERATE RISK", "#3498db", "Regular ward monitoring advised."
    else:
        lvl, col, msg = "LEVEL 1: STABLE / LOW RISK", "#5cb85c", "High biological solvency profile."

    st.header("Step 2: Results")
    
    # SECTION 1: Metrics
    st.markdown("### 1. Physiological Reserve")
    m_c1, m_c2 = st.columns(2)
    m_c1.metric("Adjusted BMI", f"{adj_bmi:.1f} kg/m²")
    m_c2.metric("DtD Score", f"{dtd_score:.2f}")

    # SECTION 2: Visual Scale
    st.markdown("### 2. Physiological Solvency Scale (DtD)")
    pos = min(max((dtd_score / 3.5) * 100, 0), 100)
    st.markdown(f"""
        <div style="width: 100%; background-color: #eee; border-radius: 12px; height: 40px; border: 1px solid #ccc; overflow: hidden; position: relative;">
          <div style="width: {pos}%; background-color: {col}; height: 100%; transition: width 1s; display: flex; align-items: center; justify-content: flex-end;">
            <span style="color: white; font-weight: bold; padding-right: 15px; font-size: 1.1rem;">{dtd_score:.2f}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # SECTION 3: Triage Box & Legend
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 3. Mortality Risk Stratification")
    st.markdown(f"""
        <div style="background-color:{col}; color:white; padding:25px; border-radius:15px; text-align:center;">
            <div class="triage-lvl">{lvl}</div>
            <div class="triage-risk">Risk of Death: {risk_of_death:.1f}%</div>
            <p style="font-size:1.1rem; opacity: 0.9; margin: 0;">{msg}</p>
        </div>
        <div class="scale-labels">
          <span style="color: #5cb85c;">Stable (<2.5%)</span>
          <span style="color: #3498db;">Moderate (2.5-5%)</span>
          <span style="color: #f0ad4e;">High (5-10%)</span>
          <span style="color: #d9534f;">Critical (>10%)</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    st.write(f"Survival Probability over 240 days: **{100-risk_of_death:.1f}%**")

# --- 7. FOOTNOTES ---
st.markdown("---")
st.markdown("""
<small style="color: #666;">
<b>Footnotes & Methodology:</b><br>
1. <b>Adjusted BMI (kg/m²):</b> Calculated as Admission Weight / Height², where Height is standardized at 1.70 m for men and 1.60 m for women per study protocol.<br>
2. <b>Distance-to-Death (DtD):</b> A standardized Z-score representing the number of standard deviations a patient's physiological trajectory lies from the biological failure threshold (K = 17.33 kg/m²).<br>
3. <b>Risk Stratification:</b> Levels are numbered 1 (Lowest Risk) to 4 (Highest Risk). Mortality probability calculated as P(Death) = Φ(-DtD).<br>
4. <b>Data Source:</b> Model parameters derived from a retrospective cohort of 15,182 patients at Jamot Hospital of Yaoundé (HJY), Cameroon.
</small>
""", unsafe_allow_html=True)
