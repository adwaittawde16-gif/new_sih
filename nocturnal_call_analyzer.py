import os
import sys
import pandas as pd
from intelligence_engine import IntelligenceEngine

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class NocturnalCallAnalyzer:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def analyze_nocturnal_patterns(self):
        """Extract late night calls (12 AM - 6 AM) and analyze cell tower locations."""
        pair_df, cdrs_raw = self.engine.get_cdr_summary()
        
        # Filter CDRs by timestamp hour
        nocturnal_cdrs = []
        for idx, row in cdrs_raw.iterrows():
            try:
                hour = int(str(row['timestamp']).split()[1].split(':')[0])
                if 0 <= hour <= 6:
                    nocturnal_cdrs.append(row)
            except Exception:
                pass

        nocturnal_df = pd.DataFrame(nocturnal_cdrs)
        
        # Cell tower hotspot breakdown
        cell_tower_summary = pd.DataFrame()
        if not nocturnal_df.empty:
            cell_tower_summary = nocturnal_df['cell_tower_location'].value_counts().reset_index()
            cell_tower_summary.columns = ['cell_tower_location', 'nocturnal_call_count']

        return nocturnal_df, cell_tower_summary

if __name__ == "__main__":
    analyzer = NocturnalCallAnalyzer()
    noc_cdrs, tower_summary = analyzer.analyze_nocturnal_patterns()
    
    print("=== NOCTURNAL CALL ANOMALY ANALYSIS (12 AM - 6 AM) ===")
    print(f"Total Late-Night Communications Found: {len(noc_cdrs)}")
    print("\nCell Tower Hotspots during Late-Night Hours:")
    print(tower_summary.to_string(index=False))
