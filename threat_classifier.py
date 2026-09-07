import os
import pandas as pd
from intelligence_engine import IntelligenceEngine

class ThreatClassifier:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def classify_suspect_risks(self):
        """Classify suspects into 4 Risk Tiers with automated police protocol recommendations."""
        scores = self.engine.calculate_threat_scores()
        
        tiers = []
        for idx, row in scores.iterrows():
            score = row['total_threat_score']
            name = row['suspect_name']
            
            if score >= 70.0:
                tier = "CRITICAL RISK (RED ALERT)"
                action = "IMMEDIATE SURVEILLANCE & LOOKOUT NOTICE. Issue location tracking orders."
            elif score >= 50.0:
                tier = "HIGH RISK (AMBER ALERT)"
                action = "ENHANCED FIELD PATROL. Interrogate frequent CDR call contacts."
            elif score >= 30.0:
                tier = "MODERATE RISK (YELLOW)"
                action = "ROUTINE CHECK-IN. Monitor financial transactions and CCTV sightings."
            else:
                tier = "LOW RISK (GREEN)"
                action = "MONITORING ONLY. Standard background verification."

            tiers.append({
                'suspect_name': name,
                'phone_number': row['phone_number'],
                'total_threat_score': score,
                'risk_tier': tier,
                'recommended_action': action,
                'cctv_meeting_score': row['cctv_meeting_score'],
                'cdr_network_score': row['cdr_network_score']
            })

        tier_df = pd.DataFrame(tiers)
        return tier_df

if __name__ == "__main__":
    classifier = ThreatClassifier()
    tiered_df = classifier.classify_suspect_risks()
    
    print("=== SUSPECT RISK TIER DISTRIBUTION ===")
    print(tiered_df['risk_tier'].value_counts())
    
    print("\nTop Critical Risk Suspects:")
    critical = tiered_df[tiered_df['risk_tier'].str.contains('CRITICAL')]
    print(critical[['suspect_name', 'total_threat_score', 'risk_tier', 'recommended_action']].head(5))
