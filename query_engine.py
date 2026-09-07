import os
import pandas as pd
from intelligence_engine import IntelligenceEngine

class IntelligenceQueryEngine:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def search_suspect(self, query):
        """Search across all datasets by suspect name, alias, phone, or FIR number."""
        q = str(query).strip().lower()
        
        # 1. Search FIRs
        firs = self.engine.firs_df[
            self.engine.firs_df['accused_name'].str.lower().str.contains(q, na=False) |
            self.engine.firs_df['accused_phone'].str.lower().str.contains(q, na=False) |
            self.engine.firs_df['fir_number'].str.lower().str.contains(q, na=False) |
            self.engine.firs_df['police_station'].str.lower().str.contains(q, na=False) |
            self.engine.firs_df['act_and_sections'].str.lower().str.contains(q, na=False)
        ]
        
        # 2. Search CDRs
        cdrs = self.engine.cdrs_df[
            self.engine.cdrs_df['caller_number'].str.lower().str.contains(q, na=False) |
            self.engine.cdrs_df['receiver_number'].str.lower().str.contains(q, na=False) |
            self.engine.cdrs_df['cell_tower_location'].str.lower().str.contains(q, na=False)
        ]
        
        # 3. Search CCTV
        cctv = self.engine.cctv_df[
            self.engine.cctv_df['suspect_name'].str.lower().str.contains(q, na=False) |
            self.engine.cctv_df['camera_id'].str.lower().str.contains(q, na=False) |
            self.engine.cctv_df['camera_location'].str.lower().str.contains(q, na=False)
        ]
        
        # 4. Search Threat Scores
        scores = self.engine.calculate_threat_scores()
        matching_scores = scores[
            scores['suspect_name'].str.lower().str.contains(q, na=False) |
            scores['phone_number'].str.lower().str.contains(q, na=False)
        ]
        
        return {
            "query": query,
            "fir_matches": firs,
            "cdr_matches": cdrs,
            "cctv_matches": cctv,
            "threat_matches": matching_scores
        }

if __name__ == "__main__":
    q_engine = IntelligenceQueryEngine()
    results = q_engine.search_suspect("Ranbir")
    print(f"Search Results for '{results['query']}':")
    print(f"  FIR Matches: {len(results['fir_matches'])}")
    print(f"  CDR Matches: {len(results['cdr_matches'])}")
    print(f"  CCTV Matches: {len(results['cctv_matches'])}")
    print(f"  Threat Matches: {len(results['threat_matches'])}")
    if not results['threat_matches'].empty:
        print("\nMatched Threat Score:")
        print(results['threat_matches'][['suspect_name', 'phone_number', 'total_threat_score']])
