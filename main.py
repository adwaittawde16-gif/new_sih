import os
import sys
import pandas as pd
from intelligence_engine import IntelligenceEngine
from graph_visualizer import GraphVisualizer
from generate_dossier import generate_suspect_dossier
from crime_ring_detector import CrimeRingDetector
from batch_dossiers import generate_all_top_dossiers
from geo_map_generator import GeoMapGenerator
from executive_report_generator import generate_executive_report
from query_engine import IntelligenceQueryEngine
from threat_classifier import ThreatClassifier
from financial_analyzer import FinancialAnalyzer
from nocturnal_call_analyzer import NocturnalCallAnalyzer
from alert_notifier import generate_police_alerts
from score_simulator import CustomScoreSimulator
from ring_visualizer import RingVisualizer
from timeline_generator import ForensicTimelineGenerator
from cell_tower_tracker import CellTowerTracker
from social_media_timeline import SocialMediaTimeline
from co_accused_network import CoAccusedNetwork
from surveillance_heatmap import SurveillanceHeatmap


# Ensure UTF-8 output formatting on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_banner():
    print("=" * 70)
    print("        INTELLIGENCE & THREAT ANALYSIS SYSTEM")
    print("  (CDR Call Graph | CCTV Meetings | 6-Param Threat Score)")
    print("=" * 70)

def show_menu():
    print("\nPlease choose an option:")
    print("  [1] See the call history (CDR Graph & Network)")
    print("  [2] CCTV sighting together (Physical Meetings)")
    print("  [3] Final score (Ranked list out of 100 with breakdown)")
    print("  [4] Detect Crime Rings & Syndicate Cells")
    print("  [5] Suspect Risk Tier Classification (Red/Amber/Yellow/Green)")
    print("  [6] Financial Money Trail & Wine Shop Spending")
    print("  [7] Nocturnal Call Anomaly Analysis (12 AM - 6 AM)")
    print("  [8] Cell Tower Trajectories & Co-Location Overlaps")
    print("  [9] Generate Forensic Chronological Timeline HTML")
    print("  [10] Real-Time Police Alerts Feed (.md)")
    print("  [11] Custom Weight Threat Score Simulator")
    print("  [12] Generate Crime Ring Subgraph HTML (e.g. RING-01)")
    print("  [13] Intelligence Search Engine (Cross-Dataset Search)")
    print("  [14] Generate Interactive HTML Network Graph")
    print("  [15] Generate CCTV Co-Location Map HTML")
    print("  [16] Export Executive Intelligence Summary (.md)")
    print("  [17] Export Top 10 Suspect Dossiers (.md)")
    print("  [18] Social Media Timeline (HTML)")
    print("  [19] Co-Accused FIR Network (HTML)")
    print("  [20] Surveillance Heatmap (HTML)")
    print("  [21] Exit")

def option_1_call_history(engine):
    print("\n" + "=" * 60)
    print("OPTION 1: CALL HISTORY & CDR NETWORK ANALYSIS")
    print("=" * 60)
    pair_df, cdr_raw = engine.get_cdr_summary()
    
    print(f"\nTotal Call Detail Records Loaded: {len(cdr_raw)}")
    print(f"Total Interacting Pairs Discovered: {len(pair_df)}")
    
    print("\n--- TOP FREQUENT CALLING SUSPECT PAIRS ---")
    top_pairs = pair_df.head(15)
    for idx, row in top_pairs.iterrows():
        print(f" * {row['suspect_1']} <---> {row['suspect_2']}")
        print(f"   Calls: {row['total_calls']} | Talk Time: {row['total_duration_min']} mins | Nocturnal Calls (12am-6am): {row['nocturnal_calls']} | SMS: {row['sms_count']}")
        print("-" * 55)

def option_2_cctv_meetings(engine):
    print("\n" + "=" * 60)
    print("OPTION 2: CCTV SIGHTINGS TOGETHER (PHYSICAL MEETINGS)")
    print("=" * 60)
    meetings = engine.get_cctv_meetings()
    
    if meetings.empty:
        print("\nNo physical CCTV co-location meetings detected between callers.")
        return
        
    print(f"\nTotal Confirmed Physical Meetings Detected: {len(meetings)}")
    print("\n--- SUSPECT PAIRS CALLING AND MEETING IN PERSON ---")
    
    for idx, row in meetings.iterrows():
        print(f"\n[MEETING ENCOUNTER #{idx + 1}]")
        print(f"   Suspect 1: {row['suspect_1']}")
        print(f"   Suspect 2: {row['suspect_2']}")
        print(f"   CDR Call Count: {row['cdr_call_count']} calls exchanged")
        print(f"   Camera ID: {row['camera_id']} ({row['camera_location']})")
        print(f"   Sighting Time S1: {row['sighting_time_s1']}")
        print(f"   Sighting Time S2: {row['sighting_time_s2']}")
        print(f"   Time Gap: {row['time_delta_minutes']} minutes apart")
        print(f"   Match Confidence: {row['avg_match_confidence'] * 100}% | Status: {row['sighting_status']}")
        print("-" * 55)

def option_3_final_scores(engine):
    print("\n" + "=" * 60)
    print("OPTION 3: FINAL THREAT SCORE LEADERBOARD (OUT OF 100)")
    print("=" * 60)
    scores = engine.calculate_threat_scores()
    
    print("\n--- TOP 10 HIGHEST THREAT SUSPECTS ---")
    top_10 = scores.head(10)
    
    for idx, row in top_10.iterrows():
        print(f"\n[RANK #{idx + 1}] {row['suspect_name']} ({row['phone_number']})")
        print(f"   OVERALL THREAT SCORE: {row['total_threat_score']} / 100")
        print(f"   Breakdown of 6 Intelligence Parameters:")
        print(f"      1. CCTV Physical Meetings Score (MAX: 30 pts) : {row['cctv_meeting_score']} pts")
        print(f"      2. CDR Interaction Network Score (20 pts)    : {row['cdr_network_score']} pts")
        print(f"      3. FIR & Section Severity Score (15 pts)      : {row['fir_severity_score']} pts")
        print(f"      4. Criminal History Score (15 pts)            : {row['criminal_history_score']} pts")
        print(f"      5. Financial Risk Score (10 pts)               : {row['financial_risk_score']} pts")
        print(f"      6. Surveillance Observation Score (10 pts)     : {row['surveillance_score']} pts")
        print("-" * 55)

def option_4_crime_rings(engine):
    print("\n" + "=" * 60)
    print("OPTION 4: CRIME RINGS & SYNDICATE CELL DETECTION")
    print("=" * 60)
    detector = CrimeRingDetector(engine)
    syndicates = detector.detect_syndicates()
    
    print(f"\nTotal Crime Rings / Syndicate Cells Discovered: {len(syndicates)}")
    print("\n--- TOP DETECTED CRIME RINGS ---")
    
    for idx, row in syndicates.head(10).iterrows():
        print(f"\n[CRIME RING #{row['syndicate_id']}]")
        print(f"   Ring Leader: {row['ring_leader']} (Leader Threat Score: {row['leader_threat_score']} / 100)")
        print(f"   Ring Size: {row['ring_size']} members")
        print(f"   Internal Calls Exchanged: {row['total_internal_calls']} calls")
        print(f"   Confirmed CCTV Meetings: {row['physical_meetings_count']} encounters")
        print(f"   Key Members: {', '.join(row['members'][:5])}")
        print("-" * 55)

def option_5_risk_tiers(engine):
    print("\n" + "=" * 60)
    print("OPTION 5: SUSPECT RISK TIER CLASSIFICATION")
    print("=" * 60)
    classifier = ThreatClassifier(engine)
    tier_df = classifier.classify_suspect_risks()
    
    print("\n--- RISK TIER DISTRIBUTION ---")
    print(tier_df['risk_tier'].value_counts().to_string())
    
    print("\n--- TOP CRITICAL & HIGH RISK SUSPECTS ---")
    crit_high = tier_df[tier_df['risk_tier'].str.contains('CRITICAL|HIGH')]
    for idx, row in crit_high.iterrows():
        print(f"\n[{row['risk_tier']}] {row['suspect_name']} (Score: {row['total_threat_score']}/100)")
        print(f"   Action Protocol: {row['recommended_action']}")
        print("-" * 55)

def option_6_financial(engine):
    print("\n" + "=" * 60)
    print("OPTION 6: FINANCIAL MONEY TRAIL & WINE SHOP SPENDING")
    print("=" * 60)
    fa = FinancialAnalyzer(engine)
    summary, raw = fa.analyze_financial_trails()
    print(f"\nTotal Transactions Logged: {len(raw)}")
    print(f"Total Financial Volume Analyzed: INR {round(raw['amount_inr'].sum(), 2)}")
    print("\n--- TOP SUSPECTS BY WINE SHOP SPENDING & VOLUME ---")
    for idx, row in summary.head(10).iterrows():
        print(f" * {row['suspect_name']} | Threat Score: {row['threat_score']}/100")
        print(f"   Total Spent: INR {row['total_volume_inr']} | Wine Shop Spent: INR {row['wine_shop_spent_inr']} | Failed ATMs: {row['failed_withdrawals']}")
        print("-" * 55)

def option_7_nocturnal(engine):
    print("\n" + "=" * 60)
    print("OPTION 7: NOCTURNAL CALL ANOMALY ANALYSIS (12 AM - 6 AM)")
    print("=" * 60)
    na = NocturnalCallAnalyzer(engine)
    noc_cdrs, towers = na.analyze_nocturnal_patterns()
    print(f"\nTotal Late-Night Communications Discovered: {len(noc_cdrs)}")
    print("\n--- LATE-NIGHT CELL TOWER HOTSPOTS ---")
    for idx, row in towers.iterrows():
        print(f" * {row['cell_tower_location']}: {row['nocturnal_call_count']} late-night calls")
        print("-" * 55)

def option_8_cell_tower(engine):
    print("\n" + "=" * 60)
    print("OPTION 8: CELL TOWER TRAJECTORIES & CO-LOCATION OVERLAPS")
    print("=" * 60)
    ctt = CellTowerTracker(engine)
    scores = engine.calculate_threat_scores()
    top_suspect = scores.iloc[0]['suspect_name']
    
    print(f"\n--- MOVEMENT TRAJECTORY FOR {top_suspect.upper()} ---")
    traj = ctt.get_tower_trajectories(top_suspect)
    print(traj.head(10).to_string(index=False))
    
    print("\n--- CELL TOWER CO-LOCATION OVERLAPS WITHIN 30 MINS ---")
    overlaps = ctt.find_tower_co_locations(time_window_minutes=30)
    if not overlaps.empty:
        print(overlaps.head(5).to_string(index=False))

def option_9_timeline(engine):
    print("\n" + "=" * 60)
    print("OPTION 9: FORENSIC CHRONOLOGICAL TIMELINE HTML GENERATOR")
    print("=" * 60)
    ftg = ForensicTimelineGenerator(engine)
    scores = engine.calculate_threat_scores()
    top_name = scores.iloc[0]['suspect_name']
    
    s_name = input(f"\nEnter suspect name (press Enter for '{top_name}'): ").strip()
    if not s_name:
        s_name = top_name
    outfile = ftg.generate_timeline(s_name)
    print(f"\nSUCCESS: Generated Forensic Timeline HTML -> {outfile}")

def option_10_alerts(engine):
    print("\n" + "=" * 60)
    print("OPTION 10: REAL-TIME POLICE ALERT FEED")
    print("=" * 60)
    outfile = os.path.join(engine.data_folder, "alert_feed.md")
    alerts, _ = generate_police_alerts(outfile)
    print(f"\nSUCCESS: Generated {len(alerts)} alerts -> {outfile}")

def option_11_simulator(engine):
    print("\n" + "=" * 60)
    print("OPTION 11: CUSTOM WEIGHT THREAT SCORE SIMULATOR")
    print("=" * 60)
    sim = CustomScoreSimulator(engine)
    custom_w = {'cctv_max': 40.0, 'cdr_max': 15.0, 'fir_max': 10.0, 'crim_max': 20.0, 'fin_max': 7.5, 'surv_max': 7.5}
    res = sim.simulate_scores(custom_w)
    print("\n--- TOP SUSPECTS UNDER CUSTOM WEIGHTING ---")
    for idx, row in res.head(5).iterrows():
        print(f" * {row['suspect_name']}: New Score = {row['simulated_threat_score']} / 100 (Original: {row['original_threat_score']})")

def option_12_ring_graph(engine):
    print("\n" + "=" * 60)
    print("OPTION 12: CRIME RING SUBGRAPH GENERATOR")
    print("=" * 60)
    rv = RingVisualizer(engine)
    r_id = input("\nEnter Crime Ring ID (press Enter for RING-01): ").strip()
    if not r_id:
        r_id = "RING-01"
    outfile = rv.generate_ring_html(r_id, engine.data_folder)
    if outfile:
        print(f"\nSUCCESS: Generated Crime Ring graph HTML -> {outfile}")

def option_13_search(engine):
    print("\n" + "=" * 60)
    print("OPTION 13: INTELLIGENCE CROSS-DATASET SEARCH")
    print("=" * 60)
    q_engine = IntelligenceQueryEngine(engine)
    query = input("\nEnter search query (name, phone, FIR #, station, section): ").strip()
    if query:
        res = q_engine.search_suspect(query)
        print(f"\n--- SEARCH RESULTS FOR '{query}' ---")
        print(f"  Active FIR Matches     : {len(res['fir_matches'])}")
        print(f"  Call Detail Logs       : {len(res['cdr_matches'])}")
        print(f"  CCTV Sighting Records  : {len(res['cctv_matches'])}")

def option_14_generate_graph(engine):
    print("\n" + "=" * 60)
    print("OPTION 14: GENERATING INTERACTIVE NETWORK GRAPH HTML")
    print("=" * 60)
    viz = GraphVisualizer(engine)
    outfile = viz.generate_interactive_html_graph()
    print(f"\nSUCCESS: Open file in your browser to view physics-directed graph:")
    print(f"  {outfile}")

def option_15_generate_map(engine):
    print("\n" + "=" * 60)
    print("OPTION 15: GENERATING CCTV CO-LOCATION MAP HTML")
    print("=" * 60)
    geo = GeoMapGenerator(engine)
    outfile = geo.generate_interactive_map()
    print(f"\nSUCCESS: Open map in browser:")
    print(f"  {outfile}")

def option_16_export_summary(engine):
    print("\n" + "=" * 60)
    print("OPTION 16: EXPORT EXECUTIVE INTELLIGENCE SUMMARY")
    print("=" * 60)
    outfile = os.path.join(engine.data_folder, "Executive_Intelligence_Summary.md")
    generate_executive_report(outfile)

def option_17_export_dossiers(engine):
    print("\n" + "=" * 60)
    print("OPTION 17: EXPORT TOP 10 SUSPECT DOSSIERS")
    print("=" * 60)
    out_dir = os.path.join(engine.data_folder, "dossiers")
    generate_all_top_dossiers(top_n=10, output_folder=out_dir)

def option_18_social_media(engine):
    print("\n" + "=" * 60)
    print("OPTION 18: SOCIAL MEDIA TIMELINE")
    print("=" * 60)
    smt = SocialMediaTimeline(engine)
    suspects = smt.sm_logins['suspect_name'].dropna().unique().tolist()
    if not suspects:
        print("No social media data.")
        return
    s_name = input(f"\nEnter suspect name (press Enter for '{suspects[0]}'): ").strip()
    if not s_name:
        s_name = suspects[0]
    smt.print_timeline(s_name)
    outfile = smt.generate_html_timeline(s_name)
    print(f"\nSUCCESS: Timeline HTML -> {outfile}")

def option_19_co_accused(engine):
    print("\n" + "=" * 60)
    print("OPTION 19: CO-ACCUSED FIR NETWORK")
    print("=" * 60)
    net = CoAccusedNetwork(engine)
    net.print_top_connected(5)
    outfile = net.generate_html_graph(max_nodes=60)
    print(f"\nSUCCESS: Co-Accused Graph HTML -> {outfile}")

def option_20_heatmap(engine):
    print("\n" + "=" * 60)
    print("OPTION 20: SURVEILLANCE HEATMAP")
    print("=" * 60)
    shm = SurveillanceHeatmap(engine)
    shm.print_summary(top_n=5)
    outfile = shm.generate_heatmap()
    print(f"\nSUCCESS: Surveillance Heatmap HTML -> {outfile}")

def main():
    print_banner()
    print("Initializing Intelligence Engine & loading datasets...")
    engine = IntelligenceEngine()
    print("Data loaded successfully!")
    
    while True:
        show_menu()
        try:
            choice = input("\nEnter choice [1-21]: ").strip()
        except EOFError:
            break
            
        if choice == '1':
            option_1_call_history(engine)
        elif choice == '2':
            option_2_cctv_meetings(engine)
        elif choice == '3':
            option_3_final_scores(engine)
        elif choice == '4':
            option_4_crime_rings(engine)
        elif choice == '5':
            option_5_risk_tiers(engine)
        elif choice == '6':
            option_6_financial(engine)
        elif choice == '7':
            option_7_nocturnal(engine)
        elif choice == '8':
            option_8_cell_tower(engine)
        elif choice == '9':
            option_9_timeline(engine)
        elif choice == '10':
            option_10_alerts(engine)
        elif choice == '11':
            option_11_simulator(engine)
        elif choice == '12':
            option_12_ring_graph(engine)
        elif choice == '13':
            option_13_search(engine)
        elif choice == '14':
            option_14_generate_graph(engine)
        elif choice == '15':
            option_15_generate_map(engine)
        elif choice == '16':
            option_16_export_summary(engine)
        elif choice == '17':
            option_17_export_dossiers(engine)
        elif choice == '18':
            option_18_social_media(engine)
        elif choice == '19':
            option_19_co_accused(engine)
        elif choice == '20':
            option_20_heatmap(engine)
        elif choice == '21':
            print("\nExiting Intelligence Analysis Tool. Stay safe!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 21.")

if __name__ == "__main__":
    main()
