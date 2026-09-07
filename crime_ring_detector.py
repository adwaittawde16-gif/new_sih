import os
import sys
import networkx as nx
import pandas as pd
from intelligence_engine import IntelligenceEngine

# Ensure UTF-8 formatting on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class CrimeRingDetector:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def detect_syndicates(self):
        """Analyze CDR interactions and CCTV meetings to detect crime rings / syndicate cells."""
        pair_df, _ = self.engine.get_cdr_summary()
        cctv_meetings = self.engine.get_cctv_meetings()
        threat_scores = self.engine.calculate_threat_scores()
        
        score_dict = dict(zip(threat_scores['suspect_name'], threat_scores['total_threat_score']))

        G = nx.Graph()
        
        for _, row in pair_df.iterrows():
            u, v = str(row['suspect_1']), str(row['suspect_2'])
            calls = int(row['total_calls'])
            if calls >= 1:
                G.add_edge(u, v, weight=calls)

        components = list(nx.connected_components(G))
        
        syndicates = []
        for idx, comp in enumerate(components, 1):
            members = list(comp)
            if len(members) < 2:
                continue
                
            cluster_scores = {m: score_dict.get(m, 0.0) for m in members}
            leader = max(cluster_scores, key=cluster_scores.get)
            leader_score = cluster_scores[leader]
            
            sub_G = G.subgraph(members)
            total_internal_calls = sum(d['weight'] for u, v, d in sub_G.edges(data=True))
            
            sub_meetings = 0
            if not cctv_meetings.empty:
                m_sub = cctv_meetings[
                    (cctv_meetings['suspect_1'].isin(members)) & 
                    (cctv_meetings['suspect_2'].isin(members))
                ]
                sub_meetings = len(m_sub)

            syndicates.append({
                'syndicate_id': f"RING-{idx:02d}",
                'ring_size': len(members),
                'ring_leader': leader,
                'leader_threat_score': leader_score,
                'total_internal_calls': total_internal_calls,
                'physical_meetings_count': sub_meetings,
                'members': sorted(members, key=lambda m: score_dict.get(m, 0.0), reverse=True)
            })

        syndicate_df = pd.DataFrame(syndicates).sort_values(by=['physical_meetings_count', 'ring_size'], ascending=[False, False])
        return syndicate_df

if __name__ == "__main__":
    detector = CrimeRingDetector()
    syndicates = detector.detect_syndicates()
    print("Detected Crime Rings / Syndicate Cells:", len(syndicates))
    print("\nTop 5 Crime Rings:")
    for idx, row in syndicates.head(5).iterrows():
        print(f"\n[CRIME RING #{row['syndicate_id']}] Leader: {row['ring_leader']} (Score: {row['leader_threat_score']}) | Members: {row['ring_size']}")
        print(f"   Internal Calls: {row['total_internal_calls']} | CCTV Meetings: {row['physical_meetings_count']}")
        print(f"   Key Members: {', '.join(row['members'][:5])}")
