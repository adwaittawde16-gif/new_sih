import os
import json
import pandas as pd
from intelligence_engine import IntelligenceEngine

def generate_suspect_dossier(suspect_name, output_folder=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'", data_folder=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'"):
    """Generate a comprehensive text & markdown intelligence dossier for a given suspect."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    engine = IntelligenceEngine(data_folder=data_folder)
    
    scores = engine.calculate_threat_scores()
    s_score_df = scores[scores['suspect_name'] == suspect_name]
    
    if s_score_df.empty:
        print(f"Suspect '{suspect_name}' not found.")
        return None
        
    s_score = s_score_df.iloc[0]
    
    # 1. FIR Records
    firs = engine.firs_df[engine.firs_df['accused_name'] == suspect_name]
    
    # 2. CDR Calls
    phone = engine.name_to_phone.get(suspect_name, '')
    cdrs = engine.cdrs_df[(engine.cdrs_df['caller_number'] == phone) | (engine.cdrs_df['receiver_number'] == phone)]
    
    # 3. CCTV Sightings
    cctv = engine.cctv_df[engine.cctv_df['suspect_name'] == suspect_name]
    
    # 4. CCTV Meetings
    meetings = engine.get_cctv_meetings()
    m_sub = meetings[(meetings['suspect_1'] == suspect_name) | (meetings['suspect_2'] == suspect_name)] if not meetings.empty else pd.DataFrame()
    
    # 5. Criminal History
    crim = engine.crim_df[engine.crim_df['suspect_name'] == suspect_name]
    
    # 6. Financial Transactions
    fin = engine.fin_df[engine.fin_df['account_holder'] == suspect_name]
    
    # 7. Surveillance Reports
    user_firs = firs['fir_number'].tolist() if not firs.empty else []
    surv = engine.surv_df[engine.surv_df['fir_number'].isin(user_firs)]
    
    filename = os.path.join(output_folder, f"dossier_{suspect_name.replace(' ', '_')}.md")
    
    dossier_content = f"""# 🚨 INTELLIGENCE DOSSIER: {suspect_name.upper()}

**Phone Number:** `{phone}`  
**Overall Threat Score:** `{s_score['total_threat_score']} / 100`  
**Threat Status:** `{"CRITICAL HIGH RISK" if s_score['total_threat_score'] >= 70 else ("MODERATE RISK" if s_score['total_threat_score'] >= 40 else "LOW RISK")}`

---

## 📊 6-Parameter Intelligence Score Breakdown

| Intelligence Parameter | Score Earned | Max Weight |
| :--- | :---: | :---: |
| 1. CCTV Co-location & Physical Meetings | **{s_score['cctv_meeting_score']} pts** | 30 pts (MAX) |
| 2. CDR Interaction Network Risk | **{s_score['cdr_network_score']} pts** | 20 pts |
| 3. FIR Severity & Active Cases | **{s_score['fir_severity_score']} pts** | 15 pts |
| 4. Criminal History & Prior Convictions | **{s_score['criminal_history_score']} pts** | 15 pts |
| 5. Financial Risk & Spending Patterns | **{s_score['financial_risk_score']} pts** | 10 pts |
| 6. Field Surveillance Observations | **{s_score['surveillance_score']} pts** | 10 pts |
| **TOTAL COMPOSITE THREAT SCORE** | **{s_score['total_threat_score']} pts** | **100 pts** |

---

## 📄 Active FIR & Police Reports ({len(firs)} FIRs)
"""
    for _, f in firs.iterrows():
        dossier_content += f"""
- **FIR Number:** `{f['fir_number']}`
  - **Police Station:** {f['police_station']}
  - **Act & Sections:** `{f['act_and_sections']}`
  - **Incident Date/Time:** {f['date_time_incident']}
  - **Investigating Officer:** {f['investigating_officer']} ({f['io_rank']})
  - **Hospital Reference:** {f['hospital_reference']}
"""

    dossier_content += f"""
---

## 📹 Confirmed CCTV Physical Meetings ({len(m_sub)} Meetings)
"""
    if m_sub.empty:
        dossier_content += "\nNo physical meetings recorded.\n"
    else:
        for _, m in m_sub.iterrows():
            other_suspect = m['suspect_2'] if m['suspect_1'] == suspect_name else m['suspect_1']
            dossier_content += f"""
- **Meeting with:** `{other_suspect}`
  - **Calls Exchanged:** {m['cdr_call_count']} calls
  - **Camera ID & Location:** `{m['camera_id']}` ({m['camera_location']})
  - **Timestamps:** S1: `{m['sighting_time_s1']}` | S2: `{m['sighting_time_s2']}`
  - **Match Confidence:** {m['avg_match_confidence'] * 100}%
"""

    dossier_content += f"""
---

## ⚖️ Criminal History & Prior Convictions
"""
    if crim.empty:
        dossier_content += "\nNo prior criminal record on file.\n"
    else:
        c = crim.iloc[0]
        dossier_content += f"""
- **Prior Convictions Count:** {c['prior_convictions_count']}
- **Previous Offence:** {c['previous_offence']}
- **Previous Police Station:** {c['previous_ps_name']}
- **Current Case Status:** `{c['case_status']}`
"""

    dossier_content += f"""
---

## 💳 Financial Transactions Log ({len(fin)} Transactions)
"""
    if fin.empty:
        dossier_content += "\nNo financial records logged.\n"
    else:
        for _, t in fin.iterrows():
            dossier_content += f"- `{t['timestamp']}` | Mode: `{t['payment_mode']}` | Payee: `{t['merchant_or_payee']}` | Amount: ₹{t['amount_inr']} | Status: **{t['status']}**\n"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(dossier_content)
        
    print(f"Generated Dossier for {suspect_name} -> {filename}")
    return filename

if __name__ == "__main__":
    engine = IntelligenceEngine()
    scores = engine.calculate_threat_scores()
    top_suspect_name = scores.iloc[0]['suspect_name']
    generate_suspect_dossier(top_suspect_name)
