import os
import pandas as pd
from intelligence_engine import IntelligenceEngine
from crime_ring_detector import CrimeRingDetector

def generate_executive_report(output_file=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'\Executive_Intelligence_Summary.md"):
    """Generate a high-level police executive intelligence summary report."""
    engine = IntelligenceEngine()
    detector = CrimeRingDetector(engine)
    
    pair_df, cdr_raw = engine.get_cdr_summary()
    meetings = engine.get_cctv_meetings()
    scores = engine.calculate_threat_scores()
    syndicates = detector.detect_syndicates()
    
    top_threats = scores.head(5)
    top_meetings = meetings.head(5) if not meetings.empty else pd.DataFrame()
    top_syndicate = syndicates.iloc[0] if not syndicates.empty else None

    report = f"""# 🛡️ EXECUTIVE INTELLIGENCE & THREAT ASSESSMENT REPORT
**Brihanmumbai Police Department — Special Crime Analysis Unit**  
**Date of Assessment:** 2026-09-07  
**Scope:** CDR Graph Analysis, CCTV Physical Meetings, 6-Parameter Threat Scoring Engine

---

## 📊 1. KEY THREAT METRICS OVERVIEW

- **Total FIR Records Analyzed:** `{len(engine.firs_df)} active FIRs`
- **Total Call Detail Logs (CDR):** `{len(cdr_raw)} calls/SMS logs`
- **Discovered Call Interaction Pairs:** `{len(pair_df)} suspect pairs`
- **Confirmed Physical Meetings (CCTV):** `{len(meetings)} co-location encounters`
- **Detected Crime Rings / Syndicates:** `{len(syndicates)} active cells`
- **Highest Threat Suspect:** **{top_threats.iloc[0]['suspect_name']}** (Score: `{top_threats.iloc[0]['total_threat_score']} / 100`)

---

## 🚨 2. TOP 5 HIGHEST THREAT SUSPECTS (OUT OF 100)

| Rank | Suspect Name | Phone Number | Composite Score | CCTV Meeting Pts (MAX 30) | CDR Network Pts (20) | FIR Severity Pts (15) | Criminal History Pts (15) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for rank, (_, row) in enumerate(top_threats.iterrows(), 1):
        report += f"| **#{rank}** | **{row['suspect_name']}** | `{row['phone_number']}` | **{row['total_threat_score']}** | {row['cctv_meeting_score']} | {row['cdr_network_score']} | {row['fir_severity_score']} | {row['criminal_history_score']} |\n"

    report += f"""
---

## 🤝 3. CONFIRMED PHYSICAL MEETING ENCOUNTERS (PART 2)

Key suspect pairs who communicate frequently **AND** were captured physically meeting near CCTV cameras:

| Meeting # | Suspect 1 | Suspect 2 | Calls Exchanged | Camera ID & Location | Match Confidence |
| :---: | :--- | :--- | :---: | :--- | :---: |
"""
    if not top_meetings.empty:
        for idx, (_, m) in enumerate(top_meetings.iterrows(), 1):
            report += f"| **#{idx}** | {m['suspect_1']} | {m['suspect_2']} | {m['cdr_call_count']} calls | `{m['camera_id']}` ({m['camera_location']}) | **{round(m['avg_match_confidence']*100, 1)}%** |\n"

    if top_syndicate is not None:
        report += f"""
---

## 🕸️ 4. PRIMARY ACTIVE CRIME RING DETECTED

- **Syndicate ID:** `{top_syndicate['syndicate_id']}`
- **Ring Leader:** **{top_syndicate['ring_leader']}** (Threat Score: `{top_syndicate['leader_threat_score']}`)
- **Total Network Members:** `{top_syndicate['ring_size']} suspects`
- **Internal Calls Exchanged:** `{top_syndicate['total_internal_calls']} calls`
- **Confirmed Physical Meetings:** `{top_syndicate['physical_meetings_count']} encounters`
- **Key Members:** {', '.join(top_syndicate['members'][:5])}
"""

    report += """
---

## 📌 5. RECOMMENDED POLICE ACTION ITEMS

1. **Issue Surveillance Orders**: Immediately deploy field surveillance teams targeting the primary meeting cameras (`MH-CCTV-9173` and `MH-CCTV-2466`).
2. **Interrogate Top Call Pairs**: Subpoena detailed call duration logs for **Md. Ranbir Bhalla** and **Md. Teerth Bhargava**.
3. **Inspect Financial Flow**: Audit UPI peer transfers and wine shop merchant payments linked to high-threat repeat offenders.
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Generated Executive Intelligence Report -> {output_file}")
    return output_file

if __name__ == "__main__":
    generate_executive_report()
