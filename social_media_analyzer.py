import os
import sys
import pandas as pd
from intelligence_engine import IntelligenceEngine

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class SocialMediaAnalyzer:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def analyze_digital_footprint(self):
        """Analyze social media platforms, digital locations, device types, and platform co-occurrences."""
        soc_intel = self.engine.soc_intel_df.copy()
        soc_login = self.engine.soc_login_df.copy()

        location_overlaps = []
        if not soc_login.empty:
            loc_groups = soc_login.groupby('approximate_location')
            for loc, group in loc_groups:
                suspects = group['suspect_name'].unique().tolist()
                if len(suspects) > 1:
                    location_overlaps.append({
                        'approximate_location': loc,
                        'suspect_count': len(suspects),
                        'platforms_used': ", ".join(group['platform'].unique().tolist()),
                        'devices_used': ", ".join(group['device_type'].unique().tolist()),
                        'suspects': ", ".join(suspects[:5])
                    })

        overlap_df = pd.DataFrame(location_overlaps)
        if not overlap_df.empty:
            overlap_df = overlap_df.sort_values(by='suspect_count', ascending=False)

        return overlap_df, soc_intel, soc_login

if __name__ == "__main__":
    sma = SocialMediaAnalyzer()
    overlaps, intel, logins = sma.analyze_digital_footprint()
    
    print("=== DIGITAL FOOTPRINT & SOCIAL MEDIA ANALYSIS ===")
    print(f"Total Digital Login Records: {len(logins)}")
    print(f"Digital Location Clusters Found: {len(overlaps)}")
    if not overlaps.empty:
        print("\nTop Digital Login Hotspots:")
        print(overlaps.head(5).to_string(index=False))
