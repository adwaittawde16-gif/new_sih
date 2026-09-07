import sys
import os

try:
    import streamlit as st
    import streamlit.components.v1 as components
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

import pandas as pd
from intelligence_engine import IntelligenceEngine
from graph_visualizer import GraphVisualizer
from crime_ring_detector import CrimeRingDetector
from geo_map_generator import GeoMapGenerator
from financial_analyzer import FinancialAnalyzer
from nocturnal_call_analyzer import NocturnalCallAnalyzer
from social_media_timeline import SocialMediaTimeline
from co_accused_network import CoAccusedNetwork
from surveillance_heatmap import SurveillanceHeatmap


if HAS_STREAMLIT:
    st.set_page_config(
        page_title="Intelligence & Threat Analysis System",
        page_icon="🕵️",
        layout="wide"
    )

    st.title("🕵️ Intelligence & Threat Analysis Dashboard")
    st.caption("CDR Network Analysis | CCTV Physical Co-Location | 6-Parameter Threat Scoring (0-100)")

    @st.cache_resource
    def load_engine():
        return IntelligenceEngine()

    engine = load_engine()

    st.sidebar.header("📌 Navigation Menu")
    option = st.sidebar.radio(
        "Choose Option:",
        [
            "1. See Call History (CDR Graph)",
            "2. CCTV Sightings Together (Physical Meetings)",
            "3. Final Threat Score (out of 100)",
            "4. Crime Rings & Syndicate Cells",
            "5. Financial Money Trail & Wine Shop Spending",
            "6. Nocturnal Call Anomaly Analysis",
            "7. Geospatial CCTV Meeting Map",
            "8. Interactive D3 Network Graph",
            "9. Social Media Timeline",
            "10. Co-Accused FIR Network",
            "11. Surveillance Heatmap"
        ]
    )

    if option == "1. See Call History (CDR Graph)":
        st.header("📞 Part 1: Call Detail Record (CDR) Interaction Network")
        pair_df, cdr_raw = engine.get_cdr_summary()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total CDR Logs", len(cdr_raw))
        col2.metric("Interacting Suspect Pairs", len(pair_df))
        col3.metric("Frequent Call Pairs (≥3 calls)", len(pair_df[pair_df['total_calls'] >= 3]))
        
        st.subheader("Top Frequent Calling Suspect Pairs")
        st.dataframe(
            pair_df[['suspect_1', 'suspect_2', 'total_calls', 'total_duration_min', 'nocturnal_calls', 'sms_count', 'incoming_count', 'outgoing_count']],
            use_container_width=True
        )
        
        st.subheader("Raw Call Detail Records Search")
        search_suspect = st.text_input("Filter call logs by suspect name or phone:")
        if search_suspect:
            filtered_cdr = cdr_raw[
                cdr_raw['caller_name'].str.contains(search_suspect, case=False, na=False) |
                cdr_raw['receiver_name'].str.contains(search_suspect, case=False, na=False) |
                cdr_raw['caller_number'].str.contains(search_suspect, case=False, na=False) |
                cdr_raw['receiver_number'].str.contains(search_suspect, case=False, na=False)
            ]
            st.dataframe(filtered_cdr, use_container_width=True)
        else:
            st.dataframe(cdr_raw.head(30), use_container_width=True)

    elif option == "2. CCTV Sightings Together (Physical Meetings)":
        st.header("📹 Part 2: CCTV Physical Meetings & Co-Location Detection")
        st.markdown("Identifies suspect pairs who **frequently call each other** AND were **sighted at the same camera location around similar timestamps**.")
        
        meetings = engine.get_cctv_meetings()
        
        if meetings.empty:
            st.warning("No physical CCTV meetings detected.")
        else:
            st.success(f"Detected {len(meetings)} Physical Meeting Encounters between frequent callers!")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Meeting Encounters", len(meetings))
            col2.metric("Avg Match Confidence", f"{round(meetings['avg_match_confidence'].mean() * 100, 1)}%")
            col3.metric("Avg Distance to Incident", f"{round(meetings['avg_distance_meters'].mean(), 1)} m")
            
            st.subheader("Meeting Encounters List")
            st.dataframe(
                meetings[['suspect_1', 'suspect_2', 'cdr_call_count', 'camera_id', 'camera_location', 'sighting_time_s1', 'sighting_time_s2', 'time_delta_minutes', 'avg_match_confidence']],
                use_container_width=True
            )

    elif option == "3. Final Threat Score (out of 100)":
        st.header("🎯 Part 3: Overall Threat Score Leaderboard (out of 100)")
        st.markdown("Comprehensive score evaluating **all 6 intelligence parameters** with hierarchical priorities (**CCTV Meetings = MAX 30 pts**).")
        
        scores = engine.calculate_threat_scores()
        
        top_suspect = scores.iloc[0]
        st.info(f"🚨 **Highest Threat Suspect**: **{top_suspect['suspect_name']}** ({top_suspect['phone_number']}) — **Score: {top_suspect['total_threat_score']} / 100**")
        
        st.subheader("Ranked Suspect Threat Scores")
        st.dataframe(
            scores[['suspect_name', 'phone_number', 'total_threat_score', 'cctv_meeting_score', 'cdr_network_score', 'fir_severity_score', 'criminal_history_score', 'financial_risk_score', 'surveillance_score']],
            use_container_width=True
        )
        
        st.subheader("Detailed Parameter Breakdown for Selected Suspect")
        selected_name = st.selectbox("Select Suspect to inspect detailed breakdown:", scores['suspect_name'].tolist())
        
        s_row = scores[scores['suspect_name'] == selected_name].iloc[0]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Total Threat Score", f"{s_row['total_threat_score']} / 100")
            st.write(f"**Phone Number:** {s_row['phone_number']}")
        
        with col2:
            breakdown_data = pd.DataFrame({
                'Intelligence Parameter': [
                    '1. CCTV Physical Meetings (MAX 30 pts)',
                    '2. CDR Network Interaction (20 pts)',
                    '3. FIR Severity (15 pts)',
                    '4. Criminal History (15 pts)',
                    '5. Financial Risk (10 pts)',
                    '6. Surveillance Observations (10 pts)'
                ],
                'Points Earned': [
                    s_row['cctv_meeting_score'],
                    s_row['cdr_network_score'],
                    s_row['fir_severity_score'],
                    s_row['criminal_history_score'],
                    s_row['financial_risk_score'],
                    s_row['surveillance_score']
                ]
            })
            st.bar_chart(breakdown_data.set_index('Intelligence Parameter'))

    elif option == "4. Crime Rings & Syndicate Cells":
        st.header("🚨 Part 4: Crime Rings & Syndicate Cell Analysis")
        st.markdown("Groups suspects into connected crime rings based on frequent call networks and physical meeting clusters.")
        
        detector = CrimeRingDetector(engine)
        syndicates = detector.detect_syndicates()
        
        st.success(f"Detected {len(syndicates)} Active Crime Rings / Syndicate Clusters!")
        
        top_ring = syndicates.iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Largest Ring Leader", top_ring['ring_leader'])
        col2.metric("Ring Size", f"{top_ring['ring_size']} members")
        col3.metric("Physical Meetings", f"{top_ring['physical_meetings_count']} encounters")
        
        st.subheader("Detected Crime Rings Overview")
        display_rings = syndicates.copy()
        display_rings['members'] = display_rings['members'].apply(lambda m: ", ".join(m[:5]))
        st.dataframe(
            display_rings[['syndicate_id', 'ring_leader', 'leader_threat_score', 'ring_size', 'total_internal_calls', 'physical_meetings_count', 'members']],
            use_container_width=True
        )

    elif option == "5. Financial Money Trail & Wine Shop Spending":
        st.header("💳 Part 5: Financial Risk & Money Trail Analysis")
        fa = FinancialAnalyzer(engine)
        summary, raw = fa.analyze_financial_trails()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Transactions Logged", len(raw))
        col2.metric("Total Financial Volume", f"₹{round(raw['amount_inr'].sum(), 2):,}")
        
        st.subheader("Top Suspect Financial Risk Leaderboard")
        st.dataframe(
            summary[['suspect_name', 'threat_score', 'total_transactions', 'total_volume_inr', 'wine_shop_spent_inr', 'failed_withdrawals', 'peer_transfer_count']],
            use_container_width=True
        )

    elif option == "6. Nocturnal Call Anomaly Analysis":
        st.header("🌙 Part 6: Nocturnal Call Anomaly Analysis (12 AM - 6 AM)")
        na = NocturnalCallAnalyzer(engine)
        noc_cdrs, towers = na.analyze_nocturnal_patterns()
        
        st.info(f"Discovered **{len(noc_cdrs)} late-night communications** between midnight and 6:00 AM.")
        
        st.subheader("Late-Night Cell Tower Hotspots")
        st.bar_chart(towers.set_index('cell_tower_location'))
        
        st.subheader("Nocturnal Call Detail Records")
        st.dataframe(noc_cdrs[['record_id', 'caller_number', 'receiver_number', 'call_type', 'duration_seconds', 'timestamp', 'cell_tower_location']], use_container_width=True)

    elif option == "7. Geospatial CCTV Meeting Map":
        st.header("📍 Part 7: Geospatial CCTV Meeting Hotspots Map")
        st.markdown("Interactive Leaflet map displaying CCTV camera locations and confirmed physical meeting circles across Mumbai.")
        
        geo = GeoMapGenerator(engine)
        map_file = geo.generate_interactive_map()
        
        with open(map_file, "r", encoding="utf-8") as f:
            map_html = f.read()
            
        components.html(map_html, height=750, scrolling=False)

    elif option == "8. Interactive D3 Network Graph":
        st.header("🕸️ Part 8: Physics-Directed Interactive Network Graph")
        st.markdown("Red dashed lines represent **CCTV Physical Meetings**. Node colors represent **Threat Scores**.")
        
        viz = GraphVisualizer(engine)
        html_file = viz.generate_interactive_html_graph()
        
        with open(html_file, "r", encoding="utf-8") as f:
            html_code = f.read()
            
        components.html(html_code, height=750, scrolling=False)

    elif option == "9. Social Media Timeline":
        st.header("📱 Part 9: Social Media Timeline")
        st.markdown("Chronological footprint of suspect social media logins and platform activity.")
        smt = SocialMediaTimeline(engine)
        suspects = smt.sm_logins['suspect_name'].dropna().unique().tolist()
        if suspects:
            selected_name = st.selectbox("Select Suspect:", sorted(suspects))
            html_file = smt.generate_html_timeline(selected_name)
            with open(html_file, "r", encoding="utf-8") as f:
                html_code = f.read()
            components.html(html_code, height=750, scrolling=True)
        else:
            st.warning("No social media events found.")

    elif option == "10. Co-Accused FIR Network":
        st.header("🔗 Part 10: Co-Accused FIR Network")
        st.markdown("Network graph of suspects sharing the same FIRs.")
        net = CoAccusedNetwork(engine)
        html_file = net.generate_html_graph(max_nodes=60)
        with open(html_file, "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=750, scrolling=True)

    elif option == "11. Surveillance Heatmap":
        st.header("🔥 Part 11: Surveillance Observations Heatmap")
        st.markdown("Geospatial heatmap showing frequency of physical surveillance sightings.")
        shm = SurveillanceHeatmap(engine)
        html_file = shm.generate_heatmap()
        with open(html_file, "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=750, scrolling=True)
