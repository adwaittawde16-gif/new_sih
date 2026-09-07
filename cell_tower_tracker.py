import os
import sys
import pandas as pd
from intelligence_engine import IntelligenceEngine

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class CellTowerTracker:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def get_tower_trajectories(self, suspect_name):
        """Extract chronological cell tower movement locations for a suspect."""
        phone = self.engine.name_to_phone.get(suspect_name, '')
        cdrs = self.engine.cdrs_df[(self.engine.cdrs_df['caller_number'] == phone) | (self.engine.cdrs_df['receiver_number'] == phone)].copy()
        
        if cdrs.empty:
            return pd.DataFrame()
            
        cdrs['timestamp_dt'] = pd.to_datetime(cdrs['timestamp'], errors='coerce')
        trajectory = cdrs.sort_values(by='timestamp_dt')[['timestamp', 'cell_tower_location', 'caller_number', 'receiver_number', 'call_type', 'duration_seconds']]
        return trajectory

    def find_tower_co_locations(self, time_window_minutes=30):
        """Find suspect pairs who connected to the SAME cell tower within a given time window."""
        cdrs = self.engine.cdrs_df.copy()
        cdrs['timestamp_dt'] = pd.to_datetime(cdrs['timestamp'], errors='coerce')
        cdrs['suspect_name'] = cdrs['caller_number'].map(lambda p: self.engine.phone_to_name.get(p, p))
        
        tower_overlaps = []
        seen_keys = set()

        for i in range(len(cdrs)):
            r1 = cdrs.iloc[i]
            for j in range(i + 1, len(cdrs)):
                r2 = cdrs.iloc[j]
                
                if r1['cell_tower_location'] == r2['cell_tower_location'] and r1['suspect_name'] != r2['suspect_name']:
                    delta_min = abs((r1['timestamp_dt'] - r2['timestamp_dt']).total_seconds()) / 60.0
                    if delta_min <= time_window_minutes:
                        pair_key = tuple(sorted([r1['record_id'], r2['record_id']]))
                        if pair_key not in seen_keys:
                            seen_keys.add(pair_key)
                            tower_overlaps.append({
                                'suspect_1': r1['suspect_name'],
                                'suspect_2': r2['suspect_name'],
                                'cell_tower_location': r1['cell_tower_location'],
                                'time_s1': r1['timestamp'],
                                'time_s2': r2['timestamp'],
                                'time_gap_minutes': round(delta_min, 1)
                            })

        overlap_df = pd.DataFrame(tower_overlaps)
        if not overlap_df.empty:
            overlap_df = overlap_df.sort_values(by='time_gap_minutes')
        return overlap_df

if __name__ == "__main__":
    ctt = CellTowerTracker()
    scores = ctt.engine.calculate_threat_scores()
    top_suspect = scores.iloc[0]['suspect_name']
    
    print(f"=== CELL TOWER MOVEMENT TRAJECTORY FOR {top_suspect.upper()} ===")
    traj = ctt.get_tower_trajectories(top_suspect)
    print(traj.to_string(index=False))
    
    print("\n=== CELL TOWER CO-LOCATION OVERLAPS WITHIN 30 MINS ===")
    overlaps = ctt.find_tower_co_locations(time_window_minutes=30)
    print(f"Total Tower Overlaps Discovered: {len(overlaps)}")
    if not overlaps.empty:
        print(overlaps.head(5).to_string(index=False))
