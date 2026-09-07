"""
api_server.py
------------
Zero-dependency REST API Server using Python standard library http.server.
Exposes JSON endpoints for external systems, police mobile apps, and dashboard integrations:
  - GET /api/health
  - GET /api/suspects
  - GET /api/suspect?name=<suspect_name>
  - GET /api/threat-scores
  - GET /api/crime-rings
  - GET /api/alerts
  - GET /api/cctv-meetings
  - GET /api/search?q=<query>

Part of: CDR & CCTV Intelligence & Threat Analysis System
For: Brihanmumbai Police Department — SIH 2026
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from intelligence_engine import IntelligenceEngine
from threat_classifier import ThreatClassifier
from crime_ring_detector import CrimeRingDetector
from alert_notifier import generate_police_alerts
from query_engine import IntelligenceQueryEngine

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Global engine instance
ENGINE = None


def get_engine():
    global ENGINE
    if ENGINE is None:
        ENGINE = IntelligenceEngine()
        ENGINE.load_data()
        ENGINE.build_lookups()
    return ENGINE


class IntelligenceAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message, status=400):
        self._send_json({'error': message, 'status': status}, status=status)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        engine = get_engine()

        try:
            if path == '/api/health':
                self._send_json({
                    'status': 'HEALTHY',
                    'system': 'Brihanmumbai Police Intelligence API',
                    'version': '1.0.0',
                    'total_suspects': len(engine.calculate_threat_scores())
                })

            elif path == '/api/suspects':
                classifier = ThreatClassifier(engine)
                tier_df = classifier.classify_suspect_risks()
                records = tier_df[['suspect_name', 'phone_number', 'total_threat_score', 'risk_tier', 'recommended_action']].to_dict(orient='records')
                self._send_json({'total': len(records), 'suspects': records})

            elif path == '/api/suspect':
                name = query.get('name', [''])[0].strip()
                if not name:
                    self._send_error("Query parameter 'name' is required. E.g. /api/suspect?name=Md.%20Ranbir%20Bhalla")
                    return
                scores = engine.calculate_threat_scores()
                sub = scores[scores['suspect_name'].str.strip().str.lower() == name.lower()]
                if sub.empty:
                    self._send_error(f"Suspect '{name}' not found.", status=404)
                    return

                row = sub.iloc[0].to_dict()
                q_engine = IntelligenceQueryEngine(engine)
                res = q_engine.search_suspect(name)
                
                row['details'] = {
                    'fir_records': len(res['fir_matches']),
                    'cctv_sightings': len(res['cctv_matches']),
                    'cdr_calls': len(res['cdr_matches']),
                }
                self._send_json(row)

            elif path == '/api/threat-scores':
                scores = engine.calculate_threat_scores()
                records = scores.to_dict(orient='records')
                self._send_json({'count': len(records), 'leaderboard': records})

            elif path == '/api/crime-rings':
                detector = CrimeRingDetector(engine)
                syndicates = detector.detect_syndicates()
                records = syndicates.to_dict(orient='records')
                self._send_json({'total_rings': len(records), 'rings': records})

            elif path == '/api/alerts':
                alerts, feed_file = generate_police_alerts()
                self._send_json({'alert_count': len(alerts), 'alerts': alerts})

            elif path == '/api/cctv-meetings':
                meetings = engine.get_cctv_meetings()
                records = meetings.to_dict(orient='records') if not meetings.empty else []
                self._send_json({'meeting_count': len(records), 'meetings': records})

            elif path == '/api/search':
                q = query.get('q', [''])[0].strip()
                if not q:
                    self._send_error("Query parameter 'q' is required. E.g. /api/search?q=Byculla")
                    return
                q_engine = IntelligenceQueryEngine(engine)
                res = q_engine.search_suspect(q)
                self._send_json({
                    'query': q,
                    'fir_matches': len(res['fir_matches']),
                    'cdr_matches': len(res['cdr_matches']),
                    'cctv_matches': len(res['cctv_matches']),
                })

            else:
                self._send_error(f"Endpoint '{path}' not found.", status=404)

        except Exception as e:
            self._send_error(str(e), status=500)


def run_server(port=8080):
    print(f"[*] Initializing Intelligence Engine...")
    get_engine()
    server_address = ('', port)
    httpd = HTTPServer(server_address, IntelligenceAPIHandler)
    print(f"[OK] Intelligence REST API server running on http://localhost:{port}")
    print(f"     Endpoints available:")
    print(f"       - GET http://localhost:{port}/api/health")
    print(f"       - GET http://localhost:{port}/api/suspects")
    print(f"       - GET http://localhost:{port}/api/suspect?name=Md.%20Ranbir%20Bhalla")
    print(f"       - GET http://localhost:{port}/api/threat-scores")
    print(f"       - GET http://localhost:{port}/api/crime-rings")
    print(f"       - GET http://localhost:{port}/api/alerts")
    print(f"       - GET http://localhost:{port}/api/cctv-meetings")
    print(f"       - GET http://localhost:{port}/api/search?q=Byculla")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Stopping server...")
        httpd.server_close()


if __name__ == '__main__':
    run_server(8080)
