"""
nlp_fir_analyzer.py
------------------
NLP & Modus Operandi (M.O.) Text Intelligence Analyzer.
Analyzes FIR narrative text, IPC sections, and surveillance notes:
  - Modus Operandi (M.O.) Tagging (Extortion, Smuggling, Cyber, Violent Crime, Financial Fraud)
  - Keyword Frequency & Threat Intensity Index
  - IPC Section Severity Extraction
  - Suspect Modus Operandi Fingerprinting

Part of: CDR & CCTV Intelligence & Threat Analysis System
For: Brihanmumbai Police Department — SIH 2026
"""

import sys
import os
import re
from collections import Counter
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Crime Category Keywords mapping for Modus Operandi detection
MO_CATEGORIES = {
    'Extortion & Protection Racket': [
        'extortion', 'ransom', 'threat', 'protection money', 'vasooli',
        'demanded', 'coercion', 'blackmail', 'intimidate'
    ],
    'Smuggling & Contraband': [
        'smuggling', 'contraband', 'drugs', 'narcotics', 'consignment',
        'hawala', 'customs', 'shipment', 'illegal goods'
    ],
    'Violent Crime & Firearm': [
        'firearm', 'weapon', 'assault', 'stabbing', 'murder', 'shooting',
        'grievous hurt', 'attempt to murder', 'pistol', 'knife', 'attack'
    ],
    'Financial & Wire Fraud': [
        'fraud', 'cheating', 'fake currency', 'forgery', 'laundering',
        'bank', 'atm', 'unauthorized transaction', 'shell company'
    ],
    'Cyber & Encrypted Operations': [
        'vpn', 'encrypted', 'darknet', 'spoofed', 'voip', 'phishing',
        'malware', 'hack', 'social media'
    ]
}


class NLPFIRAnalyzer:
    def __init__(self, engine=None, data_folder=None):
        if engine is None:
            from intelligence_engine import IntelligenceEngine
            folder = data_folder or os.path.dirname(os.path.abspath(__file__))
            engine = IntelligenceEngine(data_folder=folder)
            engine.load_data()
            engine.build_lookups()
        self.engine = engine
        self.fir_df = engine.firs_df
        self.surv_df = engine.surv_df

    def extract_mo_tags(self, text: str) -> list[str]:
        """Identify Modus Operandi tags present in narrative text."""
        if not text or not isinstance(text, str):
            return []
        text_lower = text.lower()
        matched_tags = []
        for category, keywords in MO_CATEGORIES.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in keywords):
                matched_tags.append(category)
        return matched_tags if matched_tags else ['General Crime / Unspecified']

    def calculate_text_threat_intensity(self, text: str) -> float:
        """Calculate threat intensity score (0.0 to 10.0) from narrative text."""
        if not text or not isinstance(text, str):
            return 0.0
        text_lower = text.lower()
        threat_terms = [
            'murder', 'firearm', 'pistol', 'bomb', 'explosive', 'extortion',
            'gang', 'syndicate', 'dacoity', 'kidnap', 'hawala', 'kill', 'threat'
        ]
        count = sum(1 for term in threat_terms if term in text_lower)
        return min(10.0, round(count * 2.5, 1))

    def analyze_suspect_mo(self, suspect_name: str) -> dict:
        """Fingerprint suspect's primary Modus Operandi across all FIRs & surveillance."""
        s_firs = self.fir_df[self.fir_df['accused_name'].str.strip().str.lower() == suspect_name.strip().lower()]
        
        fir_nums = set(s_firs['fir_number'].dropna().unique())
        s_surv = self.surv_df[self.surv_df['fir_number'].isin(fir_nums)] if 'fir_number' in self.surv_df.columns else pd.DataFrame()

        combined_text = []
        for _, row in s_firs.iterrows():
            for col in ['act_and_sections', 'physical_features', 'police_station']:
                if col in row and pd.notna(row[col]):
                    combined_text.append(str(row[col]))

        if not s_surv.empty:
            for _, row in s_surv.iterrows():
                for col in ['observation_details', 'spot_location']:
                    if col in row and pd.notna(row[col]):
                        combined_text.append(str(row[col]))

        full_narrative = " ".join(combined_text)
        tags = self.extract_mo_tags(full_narrative)
        threat_score = self.calculate_text_threat_intensity(full_narrative)

        ipc_counts = Counter()
        for _, row in s_firs.iterrows():
            if 'act_and_sections' in row and pd.notna(row['act_and_sections']):
                sections = re.findall(r'\b\d+[A-Z]?\b', str(row['act_and_sections']))
                ipc_counts.update(sections)

        return {
            'suspect_name': suspect_name,
            'total_fir_count': len(s_firs),
            'total_surveillance_count': len(s_surv),
            'modus_operandi_tags': tags,
            'narrative_threat_intensity': threat_score,
            'ipc_sections_charged': dict(ipc_counts)
        }

    def generate_mo_leaderboard(self) -> pd.DataFrame:
        """Build leaderboard of suspects by Modus Operandi threat intensity."""
        scores = self.engine.calculate_threat_scores()
        rows = []
        for _, row in scores.iterrows():
            name = row['suspect_name']
            mo_info = self.analyze_suspect_mo(name)
            rows.append({
                'suspect_name': name,
                'overall_threat_score': row['total_threat_score'],
                'mo_tags': ", ".join(mo_info['modus_operandi_tags']),
                'narrative_threat_intensity': mo_info['narrative_threat_intensity'],
                'fir_count': mo_info['total_fir_count'],
                'ipc_charged_count': len(mo_info['ipc_sections_charged'])
            })
        df = pd.DataFrame(rows)
        return df.sort_values(by=['narrative_threat_intensity', 'overall_threat_score'], ascending=False)


if __name__ == '__main__':
    analyzer = NLPFIRAnalyzer()
    print("--- TOP SUSPECTS BY MODUS OPERANDI THREAT INTENSITY ---")
    leaderboard = analyzer.generate_mo_leaderboard()
    print(leaderboard.head(10).to_string(index=False))
