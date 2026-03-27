# **Distance-to-Death (DtD)-TB: Individualized Mortality Risk Assessment Tool**

DtD-TB is an interactive clinical decision-support tool designed for real-time mortality risk assessment in tuberculosis (TB) patients at the time of admission.
Moving beyond traditional associative models, this tool utilizes a structural framework inspired by financial engineering and reliability theory. It conceptualizes a patient’s health trajectory as a dynamic system, calculating the "biological solvency" and physiological buffer separating an individual from a critical failure threshold.

## **Key Features**
- Individualized Risk Modeling: Generates a personalized prognostic profile by integrating age, weight, sex, HIV status, and clinical TB phenotype.
- Stochastic Logic: Simultaneously accounts for the steady health recovery trend (drift), underlying metabolic instability (volatility), and sudden clinical complications (jumps).
- Distance-to-Death (DtD) Metric: Provides a standardized Z-score that quantifies the patient’s physiological safety margin relative to a biological failure barrier (K=17.33 kg/m ²).
- Evidence-Based Triage: Instantly stratifies patients into four clinical priority tiers based on their 240-day probability of mortality.

## **Mortality Risk Stratification**

The application categorizes patients into four levels of risk based on the calculated probability of biological default:
🟢 Level 1: Stable / Low Risk (Risk < 2.5%)
High biological solvency. Patients in this tier typically require standard tuberculosis care protocols with minimal risk of early mortality.

🔵 Level 2: Moderate Risk (Risk 2.5–5%)
Adequate physiological buffer. Regular monitoring of health capital and nutritional progression is recommended.

🟠 Level 3: High Risk (Risk 5–10%)
Significant metabolic instability. Requires close clinical follow-up and frequent monitoring of physiological parameters.

🔴 Level 4: Critical Risk (Risk > 10%)
Imminent biological insolvency. This identifies the highest-priority phenotype requiring immediate intensive clinical support and nutritional intervention.

## **Why use DtD instead of BMI alone?**
While Body Mass Index is a key predictor of survival, it is a static measure. The DtD-TB tool adds critical granularity by determining how factors like age and HIV co-infection accelerate health depletion or increase volatility, identifying high-risk patients who might otherwise appear stable using weight measurements alone.
