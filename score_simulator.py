import os
import sys
import pandas as pd
from intelligence_engine import IntelligenceEngine

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class CustomScoreSimulator:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def simulate_scores(self, weights=None):
        """
        Recalculate threat scores with custom user-defined weights.
        Default weights:
          - cctv_max: 30.0
          - cdr_max: 20.0
          - fir_max: 15.0
          - crim_max: 15.0
          - fin_max: 10.0
          - surv_max: 10.0
        """
        if weights is None:
            weights = {
                'cctv_max': 30.0,
                'cdr_max': 20.0,
                'fir_max': 15.0,
                'crim_max': 15.0,
                'fin_max': 10.0,
                'surv_max': 10.0
            }

        cctv_w = weights.get('cctv_max', 30.0)
        cdr_w = weights.get('cdr_max', 20.0)
        fir_w = weights.get('fir_max', 15.0)
        crim_w = weights.get('crim_max', 15.0)
        fin_w = weights.get('fin_max', 10.0)
        surv_w = weights.get('surv_max', 10.0)

        # Baseline scores
        base_df = self.engine.calculate_threat_scores()
        
        simulated_scores = []
        for idx, row in base_df.iterrows():
            # Scale each sub-score proportionally to the new weight limits
            cctv_pts = min(cctv_w, (row['cctv_meeting_score'] / 30.0) * cctv_w)
            cdr_pts = min(cdr_w, (row['cdr_network_score'] / 20.0) * cdr_w)
            fir_pts = min(fir_w, (row['fir_severity_score'] / 15.0) * fir_w)
            crim_pts = min(crim_w, (row['criminal_history_score'] / 15.0) * crim_w)
            fin_pts = min(fin_w, (row['financial_risk_score'] / 10.0) * fin_w)
            surv_pts = min(surv_w, (row['surveillance_score'] / 10.0) * surv_w)

            total_sim = round(cctv_pts + cdr_pts + fir_pts + crim_pts + fin_pts + surv_pts, 1)

            simulated_scores.append({
                'suspect_name': row['suspect_name'],
                'phone_number': row['phone_number'],
                'simulated_threat_score': total_sim,
                'original_threat_score': row['total_threat_score'],
                'cctv_pts': round(cctv_pts, 1),
                'cdr_pts': round(cdr_pts, 1),
                'fir_pts': round(fir_pts, 1),
                'crim_pts': round(crim_pts, 1),
                'fin_pts': round(fin_pts, 1),
                'surv_pts': round(surv_pts, 1)
            })

        sim_df = pd.DataFrame(simulated_scores).sort_values(by='simulated_threat_score', ascending=False)
        return sim_df

if __name__ == "__main__":
    sim = CustomScoreSimulator()
    # Test custom weighting: CCTV = 40, Criminal History = 20
    custom_weights = {
        'cctv_max': 40.0,
        'cdr_max': 15.0,
        'fir_max': 10.0,
        'crim_max': 20.0,
        'fin_max': 7.5,
        'surv_max': 7.5
    }
    res = sim.simulate_scores(custom_weights)
    print("=== CUSTOM WEIGHT THREAT SCORE SIMULATION ===")
    print("Custom Weights:", custom_weights)
    print("\nTop 5 Suspects under Custom Weighting:")
    print(res[['suspect_name', 'simulated_threat_score', 'original_threat_score', 'cctv_pts', 'crim_pts']].head(5))
