import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import time

# ==========================================
# 1. EXTENSIVE MEDICAL KNOWLEDGE BASE (EAU/AUA GUIDELINES)
# ==========================================

MEDICAL_DB = {
    "English": {
        "params": {
            "booi": "Bladder Outlet Obstruction Index (BOOI = Pdet - 2*Qmax)",
            "bci": "Bladder Contractility Index (BCI = Pdet + 5*Qmax)",
            "compliance": "Compliance (ΔV / ΔPdet)",
            "dlpp": "Detrusor Leak Point Pressure (DLPP)",
            "alpp": "Abdominal Leak Point Pressure (ALPP/VLPP)"
        },
        "diagnoses": {
            "normal": "Normal Study / Normale Urodynamik",
            "boo": "Bladder Outlet Obstruction (BOO)",
            "du": "Detrusor Underactivity (DU)",
            "do_phasic": "Phasic Detrusor Overactivity (DO)",
            "do_terminal": "Terminal Detrusor Overactivity",
            "low_comp": "Low Compliance / Poor Distensibility",
            "sui_hyper": "Stress Incontinence (Urethral Hypermobility)",
            "sui_isd": "Stress Incontinence (Intrinsic Sphincter Deficiency)",
            "dsd": "Detrusor Sphincter Dyssynergia (DSD)",
            "dysfunctional": "Dysfunctional Voiding (Staccato Flow)"
        },
        "therapies": {
            "boo": {
                "1_Conservative": ["Watchful Waiting (IPSS < 7)", "Lifestyle changes (fluid management)"],
                "2_Medical": ["Alpha-Blockers (Tamsulosin 0.4mg, Alfuzosin 10mg)", "5-Alpha Reductase Inhibitors (Finasteride) if prostate >40cc", "PDE5-Inhibitors (Tadalafil 5mg daily)"],
                "3_Interventional": ["Rezum (Water Vapor Therapy)", "UroLift (Prostatic Urethral Lift)", "TIND (Temporary Nitinol Device)"],
                "4_Surgical": ["TURP (Monopolar/Bipolar)", "HoLEP/ThuLEP (Enucleation - Gold Std for >80cc)", "Greenlight Laser Vaporization", "Open/Robotic Simple Prostatectomy"]
            },
            "du": {
                "1_Conservative": ["Timed Voiding (every 3-4 hours)", "Double Voiding", "Credé Maneuver (Contraindicated if reflux exists)"],
                "2_Medical": ["Cholinergics (Bethanechol) - *Poor efficacy/High side effects*", "Alpha-blockers (to reduce outlet resistance)"],
                "3_Management": ["Clean Intermittent Catheterization (CIC) - *Gold Standard*", "Indwelling suprapubic catheter"],
                "4_Surgical": ["Sacral Neuromodulation (SNM) - *Select cases*", "Reduction of outflow resistance (TURP) - *Only if concomitant obstruction*"]
            },
            "do_phasic": {
                "1_Conservative": ["Bladder Training", "PFMT (Pelvic Floor Muscle Training)", "Weight Loss", "Caffeine reduction"],
                "2_Medical": ["Anticholinergics (Solifenacin 5-10mg, Fesoterodine 4-8mg)", "Beta-3 Agonists (Mirabegron 50mg, Vibegron 75mg)"],
                "3_Interventional": ["Intravesical OnabotulinumtoxinA (Botox) 100U", "PTNS (Percutaneous Tibial Nerve Stimulation)"],
                "4_Surgical": ["Sacral Neuromodulation (SNM)", "Clam Cystoplasty (Augmentation)", "Urinary Diversion (Ileal Conduit)"]
            },
            "do_terminal": {
                "Note": "Terminal DO often triggers voiding. Treatment focuses on suppressing the contraction and ensuring complete emptying.",
                "Therapy": ["Treat as Phasic DO (Anticholinergics/Botox)", "Ensure no obstruction (BOO) is triggering the reflex"]
            },
            "low_comp": {
                "Risk": "**CRITICAL:** Risk of upper urinary tract deterioration (Hydronephrosis).",
                "1_Medical": ["High-dose Anticholinergics", "Beta-3 Agonists (Adjunct)"],
                "2_Management": ["CIC (Catheterization) to keep volume below threshold", "Night-time drainage"],
                "3_Surgical": ["Botox Detrusor Injection (200U-300U)", "Augmentation Cystoplasty (Ileum)", "Auto-augmentation"]
            },
            "sui_hyper": {
                "Definition": "ALPP > 90 cmH2O. Support defect.",
                "1_Conservative": ["Intensive PFMT (Physiotherapy)", "Biofeedback", "Weight Loss"],
                "2_Surgical (Female)": ["Mid-urethral Sling (Retropubic TVT or Transobturator TOT)", "Colposuspension (Burch)"],
                "3_Surgical (Male)": ["Male Sling (Advance XP)", "ProACT balloons"]
            },
            "sui_isd": {
                "Definition": "ALPP < 60 cmH2O. Open bladder neck.",
                "1_Conservative": ["Pessary / Vaginal inserts"],
                "2_Interventional": ["Urethral Bulking Agents (Bulkamid)"],
                "3_Surgical": ["Retropubic TVT (more effective than TOT for ISD)", "Pubovaginal Fascial Sling (Gold Std for complex cases)", "Artificial Urinary Sphincter (AMS 800)"]
            },
            "dsd": {
                "Context": "Common in Spinal Cord Injury (Suprasacral). Risk of high pressure storage.",
                "1_Goal": "PROTECT KIDNEYS. Maintain Pdet < 40 cmH2O.",
                "2_Medical": ["Alpha-blockers", "Antimuscarinics (for storage)"],
                "3_Interventional": ["Botox to External Sphincter", "CIC (Catheterization)"],
                "4_Surgical": ["Sphincterotomy (NDO/DSD)", "Urethral Stent (Permanent - rarely used now)"]
            },
            "dysfunctional": {
                "Context": "Learned voiding dysfunction. Active EMG during void.",
                "1_Conservative": ["Biofeedback Uroflowmetry (EMG-Flow)", "Relaxation techniques"],
                "2_Medical": ["Alpha-blockers (off-label)", "Muscle relaxants (Diazepam - rare)"],
                "3_Avoid": "Avoid instrumentation/dilatation (often makes it worse)."
            }
        }
    },
    "Deutsch": {
        "params": {
            "booi": "Blasenhalsobstruktionsindex (BOOI)",
            "bci": "Blasenkontraktilitätsindex (BCI)",
            "compliance": "Compliance (Dehnbarkeit)",
            "dlpp": "Detrusor Leak Point Pressure (DLPP)",
            "alpp": "Abdominal Leak Point Pressure (ALPP/VLPP)"
        },
        "diagnoses": {
            "normal": "Normalbefund",
            "boo": "Blasenhalsobstruktion (BOO)",
            "du": "Detrusorunteraktivität (Hypokontraktil)",
            "do_phasic": "Phasische Detrusorüberaktivität (DO)",
            "do_terminal": "Terminale Detrusorüberaktivität",
            "low_comp": "Niedrige Compliance (Low Compliance)",
            "sui_hyper": "Belastungsinkontinenz (Urethrale Hypermmobilität)",
            "sui_isd": "Belastungsinkontinenz (Sphinkterdefizienz / ISD)",
            "dsd": "Detrusor-Sphinkter-Dyssynergie (DSD)",
            "dysfunctional": "Dysfunktionale Miktion (Stakkato-Miktion)"
        },
        "therapies": {
            "boo": {
                "1_Konservativ": ["Watchful Waiting", "Flüssigkeitsmanagement"],
                "2_Medikamentös": ["Alpha-Blocker (Tamsulosin)", "5-ARI (Finasterid) bei Prostata >40ml", "PDE5-Hemmer (Tadalafil)"],
                "3_Interventionell": ["Rezum (Wasserdampf)", "UroLift", "TIND"],
                "4_Operativ": ["TUR-P (Mono/Bipolar)", "HoLEP (Enukleation)", "Greenlight-Laser", "Offene Prostatektomie"]
            },
            "du": {
                "1_Konservativ": ["Doppel-Miktion", "Zeitmiktion (alle 3h)", "Credé-Handgriff (Vorsicht Reflux)"],
                "2_Medikamentös": ["Cholinergika (Bethanechol) - *Kaum wirksam*", "Alpha-Blocker"],
                "3_Management": ["Intermittierender Selbstkatheterismus (ISK) - *Goldstandard*"],
                "4_Operativ": ["Sakrale Neuromodulation (SNM)", "TUR-P (nur bei gleichzeitiger Obstruktion)"]
            },
            "do_phasic": {
                "1_Konservativ": ["Blasentraining", "Beckenbodentraining", "Gewichtsreduktion"],
                "2_Medikamentös": ["Anticholinergika (Solifenacin, Fesoterodin)", "Beta-3-Agonisten (Mirabegron, Vibegron)"],
                "3_Interventionell": ["Intravesikales Botox (100E)", "PTNS"],
                "4_Operativ": ["Sakrale Neuromodulation (SNM)", "Blasenaugmentation"]
            },
            "do_terminal": {
                "Note": "Terminale DO löst oft die Miktion aus. Ziel ist Dämpfung.",
                "Therapy": ["Behandlung wie phasische DO", "Ausschluss einer Obstruktion (BOO)"]
            },
            "low_comp": {
                "Risk": "**KRITISCH:** Risiko für Nierenschädigung (Hochdrucksystem).",
                "1_Medikamentös": ["Hochdosis Anticholinergika"],
                "2_Management": ["ISK (Konsequente Entleerung)", "Dauerableitung (Suprapubisch)"],
                "3_Operativ": ["Botox (200-300E)", "Blasenaugmentation (Ileum)", "Conduit"]
            },
            "sui_hyper": {
                "Definition": "ALPP > 90 cmH2O. Defekt des Halteapparats.",
                "1_Konservativ": ["Intensives Beckenbodentraining", "Biofeedback"],
                "2_Operativ (Frau)": ["Mittelhohlsystem-Schlinge (TVT/TOT)", "Colposuspension"],
                "3_Operativ (Mann)": ["Bänder (Male Sling)", "ProACT"]
            },
            "sui_isd": {
                "Definition": "ALPP < 60 cmH2O. Offener Blasenals/Sphinkter.",
                "1_Konservativ": ["Pessare"],
                "2_Interventionell": ["Bulking Agents (Bulkamid)"],
                "3_Operativ": ["Retropubisches TVT", "Faszienzügelplastik", "Artifizieller Sphinkter (AMS 800)"]
            },
            "dsd": {
                "Context": "Häufig bei Rückenmarksverletzung (Suprasakral).",
                "1_Goal": "NIERENSCHUTZ vor Kontinenz.",
                "2_Medikamentös": ["Alpha-Blocker", "Anticholinergika"],
                "3_Interventionell": ["Botox in den Sphinkter", "ISK"],
                "4_Operativ": ["Sphinkterotomie"]
            },
            "dysfunctional": {
                "Context": "Erlerntes Fehlverhalten. Aktives EMG während Miktion.",
                "1_Konservativ": ["Biofeedback-Uroflow", "Entspannungstraining"],
                "2_Medikamentös": ["Alpha-Blocker", "Muskelrelaxantien"],
                "3_Avoid": "Keine Bougierung/Schlitzung!"
            }
        }
    }
}

# ==========================================
# 2. SOPHISTICATED CLINICAL SCENARIO ENGINE
# ==========================================

def generate_clinical_scenario(scenario_type):
    """
    Generates high-fidelity simulation data for specific pathologies.
    """
    # 600s filling, 60s voiding
    t_fill = np.linspace(0, 600, 600)
    t_void = np.linspace(600, 660, 600)
    t = np.concatenate([t_fill, t_void])
    
    # Init arrays
    total = len(t)
    p_abd = 20 + np.random.normal(0, 0.5, total)
    p_det = np.zeros(total)
    flow = np.zeros(total)
    emg = np.random.normal(2, 1, total)

    # --- PATHOLOGY LOGIC ---

    if scenario_type == "Normal":
        # Linear fill to 10cmH2O
        p_det[:600] = 5 + (t_fill/600)*5
        # Void: Good contraction, good flow
        p_det[600:] = 10 + 40 * np.exp(-0.5 * ((t_void-630)/10)**2)
        flow[600:] = 25 * np.exp(-0.5 * ((t_void-632)/8)**2)

    elif scenario_type == "Obstructed (BOO)":
        # Fill: Stable
        p_det[:600] = 5 + (t_fill/600)*8
        # Void: HIGH Pressure (>100), LOW Flow (<10), Prolonged
        p_det[600:] = 13 + 110 * np.exp(-0.5 * ((t_void-630)/20)**2) # High Pdet
        flow[600:] = 8 * np.exp(-0.5 * ((t_void-635)/20)**2) # Flat curve

    elif scenario_type == "Detrusor Underactivity (DU)":
        p_det[:600] = 5 + (t_fill/600)*5
        # Void: Minimal contraction
        p_det[600:] = 8 + 5 * np.sin((t_void-600)/10)
        # Flow: Driven by abdominal straining (Valsalva)
        strain_wave = 30 * np.abs(np.sin((t_void-600)/8))
        p_abd[600:] += strain_wave
        flow[600:] = 0.3 * strain_wave # Flow follows abdominal pressure

    elif scenario_type == "Phasic Detrusor Overactivity (DO)":
        base = 5 + (t_fill/600)*5
        # Add 3 distinct contractions during filling
        spikes = np.zeros(600)
        for loc in [200, 350, 500]:
            spikes += 45 * np.exp(-0.5 * ((t_fill-loc)/8)**2)
        p_det[:600] = base + spikes
        # Void normal
        p_det[600:] = 10 + 35 * np.exp(-0.5 * ((t_void-630)/10)**2)
        flow[600:] = 20 * np.exp(-0.5 * ((t_void-632)/8)**2)

    elif scenario_type == "Terminal Detrusor Overactivity":
        # Stable until end of filling
        base = 5 + (t_fill/600)*5
        # Huge spike at end of filling that merges into voiding
        terminal_spike = 60 * np.exp(-0.5 * ((t_fill-600)/15)**2)
        p_det[:600] = base + terminal_spike
        # Voiding continues the spike
        p_det[600:] = 60 * np.exp(-0.5 * ((t_void-600)/15)**2)
        flow[600:] = 30 * np.exp(-0.5 * ((t_void-605)/8)**2) # Urgency void

    elif scenario_type == "Low Compliance":
        # Linear rise to dangerous levels (>40)
        p_det[:600] = 5 + (t_fill/600)*45 # Ends at 50 cmH2O
        p_det[600:] = 50 + 20 * np.exp(-0.5 * ((t_void-630)/10)**2)
        flow[600:] = 15 * np.exp(-0.5 * ((t_void-632)/8)**2)

    elif scenario_type == "SUI (Intrinsic Sphincter Deficiency)":
        p_det[:600] = 5 + (t_fill/600)*5
        # Coughs
        cough_idx = [150, 300, 450]
        for c in cough_idx:
            # Moderate cough (Pabd rise ~40-50)
            p_abd[c:c+10] += 50 * np.exp(-0.5 * (np.arange(10)-5)**2)
            # LEAKAGE: Significant flow spike despite moderate pressure
            flow[c:c+10] += 10 * np.exp(-0.5 * (np.arange(10)-5)**2)
        # Normal void
        p_det[600:] = 10 + 30 * np.exp(-0.5 * ((t_void-630)/10)**2)
        flow[600:] += 20 * np.exp(-0.5 * ((t_void-632)/8)**2)

    elif scenario_type == "Dysfunctional Voiding (Staccato)":
        p_det[:600] = 5 + (t_fill/600)*5
        # High Pressure
        p_det[600:] = 15 + 60 * np.exp(-0.5 * ((t_void-630)/20)**2)
        # EMG Active during void
        emg[600:] += 10 * np.abs(np.sin((t_void-600)/2))
        # Flow Staccato (Choppy)
        smooth_flow = 15 * np.exp(-0.5 * ((t_void-630)/20)**2)
        chop = (np.sin((t_void-600)/2) + 1) / 2
        flow[600:] = smooth_flow * chop

    # Calc Pves
    p_ves = p_abd + p_det
    
    return pd.DataFrame({
        "Time": t, "Pves": p_ves, "Pabd": p_abd, "Pdet": p_det, "Flow": flow, "EMG": emg
    })

# ==========================================
# 3. ANALYSIS LOGIC (GUIDELINE COMPLIANT)
# ==========================================

def perform_clinical_analysis(df, gender):
    results = {}
    findings = []
    
    # 1. Phase Detection
    is_flowing = df['Flow'] > 1.0
    if is_flowing.sum() < 5: # Retention or minimal flow
        filling = df
        voiding = df.iloc[-1:] # Dummy
        qmax = 0
    else:
        # Find main void (largest contiguous flow area)
        # Simplified: Cut at first sustained flow
        start = is_flowing.idxmax()
        # Backtrack 30s to catch pre-void events
        split_idx = max(0, start - 300) 
        filling = df.iloc[:split_idx]
        voiding = df.iloc[split_idx:]
        qmax = voiding['Flow'].max()

    # 2. Key Metrics
    idx_qmax = voiding['Flow'].idxmax() if qmax > 0 else 0
    pdet_qmax = df.loc[idx_qmax, 'Pdet'] if qmax > 0 else 0
    pdet_max = voiding['Pdet'].max() if qmax > 0 else 0
    
    # 3. BOOI / BCI (Male only standard, but calc for all)
    booi = pdet_qmax - 2*qmax
    bci = pdet_qmax + 5*qmax
    
    # --- DIAGNOSTIC ALGORITHMS ---
    
    # A. OBSTRUCTION
    if gender == "Male":
        if booi > 40: findings.append("boo")
        elif 20 <= booi <= 40: findings.append("equivocal")
    else:
        # Blaivas-Groutz / Solomon Greenwell
        if qmax < 12 and pdet_qmax > 20: findings.append("boo")

    # B. CONTRACTILITY
    if bci < 100 and qmax > 0: findings.append("du")
    
    # C. STORAGE (DO)
    # Scan filling phase for Pdet spikes > 5cmH2O (ICS definition is any rise, usually >5 or >15 is significant)
    if len(filling) > 100:
        base = filling['Pdet'].rolling(100).min()
        det_rise = filling['Pdet'] - base
        # Check for Phasic (Ups and Downs)
        peaks = det_rise[det_rise > 15]
        if not peaks.empty:
            # Check if it happens at end only
            if peaks.index.max() > (len(filling) - 50):
                findings.append("do_terminal")
            else:
                findings.append("do_phasic")

    # D. COMPLIANCE
    # Rise in Pdet from start to end of filling
    pdet_start = filling['Pdet'].iloc[0]
    pdet_end = filling['Pdet'].iloc[-1]
    if (pdet_end - pdet_start) > 15: # Arbitrary danger threshold, typically <40ml/cmH2O is bad
        findings.append("low_comp")

    # E. STRESS INCONTINENCE (ALPP)
    # Look for flow during filling (leaks)
    leaks = filling[filling['Flow'] > 1.0]
    if not leaks.empty:
        # Check Pabd at leak moment
        leak_idx = leaks.index[0]
        alpp = filling.loc[leak_idx, 'Pabd']
        pdet_at_leak = filling.loc[leak_idx, 'Pdet']
        
        # Only SUI if Pdet is stable (no DO)
        if pdet_at_leak < 15: 
            if alpp < 60: findings.append("sui_isd")
            else: findings.append("sui_hyper")
            results['ALPP'] = alpp

    # F. DYSFUNCTIONAL VOIDING
    # Check EMG/Flow correlation
    if 'EMG' in df.columns:
        emg_void_mean = voiding['EMG'].mean()
        emg_fill_mean = filling['EMG'].mean()
        if emg_void_mean > (emg_fill_mean * 1.5) and qmax < 15:
            findings.append("dysfunctional")

    if not findings: findings.append("normal")
    
    results.update({
        "Qmax": qmax, "PdetQmax": pdet_qmax, "PdetMax": pdet_max,
        "BOOI": booi, "BCI": bci, "Findings": list(set(findings))
    })
    return results

def generate_text_report(res, gender, lang="English"):
    """
    Generates a professional medical text block.
    """
    t = MEDICAL_DB[lang]
    txt = f"**URODYNAMIC REPORT**\n\n"
    txt += f"**Patient:** {gender} | **Qmax:** {res['Qmax']:.1f} ml/s | **Pdet@Qmax:** {res['PdetQmax']:.1f} cmH2O\n"
    if gender == "Male":
        txt += f"**Indices:** BOOI: {res['BOOI']:.1f} ({'Obstructed' if res['BOOI']>40 else 'Non-obstructed'}), BCI: {res['BCI']:.1f}\n\n"
    
    txt += "**Observations:**\n"
    for f in res['Findings']:
        txt += f"- {t['diagnoses'][f]}\n"
    
    if 'ALPP' in res:
        txt += f"- Leak Point Pressure (ALPP) observed at {res['ALPP']:.0f} cmH2O.\n"
        
    txt += "\n**Interpretation & Plan:**\n"
    for f in res['Findings']:
        if f in t['therapies']:
            therapies = t['therapies'][f]
            txt += f"\n*Management for {t['diagnoses'][f]}:*\n"
            if isinstance(therapies, dict):
                for line, options in therapies.items():
                    # Format: "1_Conservative" -> "Conservative"
                    clean_line = line.split('_')[-1]
                    opts = ", ".join(options)
                    txt += f"  - **{clean_line}:** {opts}\n"
            else:
                # Fallback for simpler structures
                txt += f"  - {therapies}\n"
                
    return txt

# ==========================================
# 4. PHOTO RECONSTRUCTION ENGINE
# ==========================================
def reconstruct_from_points(points):
    """
    Creates a synthetic dataframe from user-entered points 
    so we can use the main analysis engine.
    """
    t = np.linspace(0, 100, 1000)
    
    # Flow: Gaussian centered at 50
    qmax = points['qmax']
    flow = qmax * np.exp(-0.5 * ((t-50)/5)**2)
    
    # Pdet: Gaussian centered at 50 (if obstruction) or delayed
    pdet_max = points['pdet_max']
    pdet_qmax = points['pdet_qmax']
    
    # Construct Pdet curve
    # Base fill
    pdet = 5 + (t/100)*5
    # Voiding contraction
    # Adjust peak to match PdetQmax at t=50
    contraction = (pdet_max - 10) * np.exp(-0.5 * ((t-50)/10)**2)
    pdet += contraction
    
    return pd.DataFrame({
        "Time": t, "Flow": flow, "Pdet": pdet, "Pves": pdet+20, "Pabd": np.full(1000, 20), "EMG": np.random.normal(2,1,1000)
    })

# ==========================================
# 5. MAIN APP
# ==========================================

def main():
    st.set_page_config(page_title="UroClinical Suite", layout="wide", page_icon="🏥")
    st.title("🏥 Urodynamics Clinical Suite")
    
    # Sidebar
    st.sidebar.header("Configuration")
    lang = st.sidebar.selectbox("Language", ["English", "Deutsch"])
    gender = st.sidebar.radio("Patient Gender", ["Male", "Female"])
    
    st.sidebar.markdown("---")
    mode = st.sidebar.radio("Mode", ["📂 Upload CSV", "📸 Photo Digitizer", "🧬 Case Simulation"])
    
    df = None
    
    # --- INPUT ---
    if mode == "📂 Upload CSV":
        f = st.sidebar.file_uploader("CSV File", type=["csv", "txt"])
        if f:
            try:
                df = pd.read_csv(f)
                # Normalization
                df.columns = [c.strip() for c in df.columns]
                col_map = {}
                for c in df.columns:
                    cl = c.lower()
                    if 'det' in cl: col_map[c] = 'Pdet'
                    elif 'flow' in cl: col_map[c] = 'Flow'
                    elif 'ves' in cl: col_map[c] = 'Pves'
                    elif 'abd' in cl: col_map[c] = 'Pabd'
                    elif 'time' in cl: col_map[c] = 'Time'
                    elif 'emg' in cl: col_map[c] = 'EMG'
                df = df.rename(columns=col_map)
                if 'Time' not in df: df['Time'] = np.arange(len(df))
                if 'Pdet' not in df and 'Pves' in df: df['Pdet'] = df['Pves'] - df['Pabd']
            except Exception as e:
                st.error(f"File Error: {e}")

    elif mode == "📸 Photo Digitizer":
        st.info("Input key metrics visible on the image to generate a clinical report.")
        c1, c2 = st.columns(2)
        with c1:
            val_qmax = st.number_input("Qmax (ml/s)", value=15.0)
            val_vol = st.number_input("Voided Volume (ml)", value=250.0)
        with c2:
            val_pqmax = st.number_input("Pdet @ Qmax (cmH2O)", value=40.0)
            val_pmax = st.number_input("Pdet Max (cmH2O)", value=50.0)
        
        if st.button("Generate Analysis"):
            df = reconstruct_from_points({'qmax': val_qmax, 'pdet_qmax': val_pqmax, 'pdet_max': val_pmax})

    elif mode == "🧬 Case Simulation":
        scenarios = [
            "Normal", "Obstructed (BOO)", "Detrusor Underactivity (DU)", 
            "Phasic Detrusor Overactivity (DO)", "Terminal Detrusor Overactivity",
            "Low Compliance", "SUI (Intrinsic Sphincter Deficiency)",
            "Dysfunctional Voiding (Staccato)"
        ]
        sel = st.sidebar.selectbox("Select Pathology", scenarios)
        if st.sidebar.button("Load Case"):
            df = generate_clinical_scenario(sel)
            st.success(f"Loaded: {sel}")

    # --- OUTPUT ---
    if df is not None:
        res = perform_clinical_analysis(df, gender)
        
        t1, t2, t3 = st.tabs(["📊 Dashboard & Guidelines", "📝 Medical Report", "📈 High-Res Curves"])
        
        with t1:
            # KPIS
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Qmax", f"{res['Qmax']:.1f}", "ml/s")
            k2.metric("Pdet@Qmax", f"{res['PdetQmax']:.1f}", "cmH2O")
            k3.metric("BOOI", f"{res['BOOI']:.0f}", delta="Obstruction" if res['BOOI']>40 else "Normal", delta_color="inverse")
            k4.metric("Diagnosis", ", ".join(res['Findings']))
            
            st.markdown("---")
            
            # Therapy Accordion
            for f in res['Findings']:
                name = MEDICAL_DB[lang]['diagnoses'][f]
                with st.expander(f"📌 {name} - Management Guidelines", expanded=True):
                    therapies = MEDICAL_DB[lang]['therapies'].get(f, {})
                    if 'Context' in therapies:
                        st.info(therapies['Context'])
                    
                    # Sort keys to ensure 1_Conservative comes before 2_Medical
                    for step in sorted(therapies.keys()):
                        if step in ['Context', 'Note', 'Risk', 'Goal', 'Avoid', 'Definition']: continue # Handle separately
                        
                        clean_step = step.split('_')[-1] # Remove "1_"
                        st.markdown(f"**{clean_step}:**")
                        for opt in therapies[step]:
                            st.markdown(f"- {opt}")
                    
                    # Warnings
                    if 'Risk' in therapies: st.error(therapies['Risk'])
                    if 'Avoid' in therapies: st.warning(f"⚠️ {therapies['Avoid']}")

        with t2:
            st.subheader("Generated Medical Text")
            report_text = generate_text_report(res, gender, lang)
            st.text_area("Copy for EMR/Arztbrief", report_text, height=400)
            
        with t3:
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                subplot_titles=("Flow (ml/s)", "Pressures (cmH2O)", "EMG (uV)"))
            
            # Use dictionary syntax for line props to avoid Plotly errors
            fig.add_trace(go.Scatter(x=df['Time'], y=df['Flow'], name="Flow", fill='tozeroy', line=dict(color='#2196F3', width=2)), row=1, col=1)
            
            if 'Pves' in df:
                fig.add_trace(go.Scatter(x=df['Time'], y=df['Pves'], name="Pves", line=dict(color='#F44336', width=1)), row=2, col=1)
            if 'Pabd' in df:
                fig.add_trace(go.Scatter(x=df['Time'], y=df['Pabd'], name="Pabd", line=dict(color='#9E9E9E', dash='dot')), row=2, col=1)
            
            fig.add_trace(go.Scatter(x=df['Time'], y=df['Pdet'], name="Pdet", line=dict(color='#4CAF50', width=3)), row=2, col=1)
            
            if 'EMG' in df:
                fig.add_trace(go.Scatter(x=df['Time'], y=df['EMG'], name="EMG", line=dict(color='#FF9800', width=1)), row=3, col=1)

            fig.update_layout(height=800, template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
