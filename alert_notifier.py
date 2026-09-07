import os
import sys
import pandas as pd
from intelligence_engine import IntelligenceEngine
from crime_ring_detector import CrimeRingDetector
from threat_classifier import ThreatClassifier

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def generate_police_alerts(output_file=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'\alert_feed.md"):
    """Generate real-time police alert notifications flagging critical threats."""
    engine = IntelligenceEngine()
    meetings = engine.get_cctv_meetings()
    classifier = ThreatClassifier(engine)
    detector = CrimeRingDetector(engine)
    
    tier_df = classifier.classify_suspect_risks()
    syndicates = detector.detect_syndicates()
    
    critical_suspects = tier_df[tier_df['risk_tier'].str.contains('CRITICAL')]
    
    alerts = []
    
    # 1. Alert for Critical Risk Suspects
    for idx, row in critical_suspects.iterrows():
        alerts.append({
            'level': 'CRITICAL (RED ALERT)',
            'title': f"HIGH THREAT SUSPECT: {row['suspect_name']}",
            'details': f"Threat Score {row['total_threat_score']}/100. Phone: {row['phone_number']}. Action: {row['recommended_action']}"
        })

    # 2. Alert for Physical Meetings
    if not meetings.empty:
        for idx, m in meetings.head(5).iterrows():
            alerts.append({
                'level': 'URGENT MEETING ALERT',
                'title': f"CONFIRMED PHYSICAL MEETING: {m['suspect_1']} & {m['suspect_2']}",
                'details': f"Sighted at camera {m['camera_id']} ({m['camera_location']}) with {m['cdr_call_count']} prior calls. Time gap: {m['time_delta_minutes']} min. Match Confidence: {m['avg_match_confidence']*100}%"
            })

    # 3. Alert for Top Crime Ring
    if not syndicates.empty:
        top_ring = syndicates.iloc[0]
        alerts.append({
            'level': 'CRIME RING ACTIVATION',
            'title': f"ACTIVE SYNDICATE {top_ring['syndicate_id']} (Leader: {top_ring['ring_leader']})",
            'details': f"{top_ring['ring_size']} members active. {top_ring['total_internal_calls']} calls & {top_ring['physical_meetings_count']} CCTV meetings recorded."
        })

    # Export markdown alert feed
    feed_md = f"# 🔔 REAL-TIME POLICE ALERT FEED\n**Generated:** 2026-09-07 | **Active Alerts:** {len(alerts)}\n\n---\n"
    
    for idx, a in enumerate(alerts, 1):
        feed_md += f"""
### [{a['level']}] {a['title']}
- **Details:** {a['details']}
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(feed_md)
        
    print(f"Generated Police Alert Feed -> {output_file}")
    return alerts, output_file

if __name__ == "__main__":
    generate_police_alerts()
