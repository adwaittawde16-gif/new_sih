import os
import sys
import pandas as pd
from intelligence_engine import IntelligenceEngine

# Ensure UTF-8 output formatting on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class FinancialAnalyzer:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def analyze_financial_trails(self):
        """Analyze transaction patterns, peer transfers, wine shop spending, and failed withdrawals."""
        fin = self.engine.fin_df.copy()
        threat_scores = self.engine.calculate_threat_scores()
        
        score_dict = dict(zip(threat_scores['suspect_name'], threat_scores['total_threat_score']))

        fin['is_wine_shop'] = fin['merchant_or_payee'].str.contains('Wine|Liquor', case=False, na=False)
        fin['is_peer_transfer'] = fin['merchant_or_payee'].str.contains('Peer', case=False, na=False)
        fin['is_large_amount'] = fin['amount_inr'] >= 5000.0

        suspect_fin = []
        for name in self.engine.all_suspects:
            s_txns = fin[fin['account_holder'] == name]
            if s_txns.empty:
                continue
                
            total_spent = s_txns['amount_inr'].sum()
            txn_count = len(s_txns)
            failed_txns = len(s_txns[s_txns['status'] == 'FAILED'])
            wine_spending = s_txns[s_txns['is_wine_shop']]['amount_inr'].sum()
            peer_transfers = len(s_txns[s_txns['is_peer_transfer']])

            suspect_fin.append({
                'suspect_name': name,
                'threat_score': score_dict.get(name, 0.0),
                'total_transactions': txn_count,
                'total_volume_inr': round(total_spent, 2),
                'failed_withdrawals': failed_txns,
                'wine_shop_spent_inr': round(wine_spending, 2),
                'peer_transfer_count': peer_transfers
            })

        fin_summary_df = pd.DataFrame(suspect_fin).sort_values(by=['wine_shop_spent_inr', 'total_volume_inr'], ascending=[False, False])
        return fin_summary_df, fin

if __name__ == "__main__":
    analyzer = FinancialAnalyzer()
    summary, raw = analyzer.analyze_financial_trails()
    
    print("=== FINANCIAL RISK ASSESSMENT ===")
    print(f"Total Transactions Logged: {len(raw)}")
    print(f"Total Volume Analyzed: INR {round(raw['amount_inr'].sum(), 2)}")
    print("\nTop 5 Suspects by Wine Shop & High Spending:")
    print(summary[['suspect_name', 'threat_score', 'total_volume_inr', 'wine_shop_spent_inr', 'failed_withdrawals']].head(5))
