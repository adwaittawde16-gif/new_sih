import os
import sys
import json
import pandas as pd
from intelligence_engine import IntelligenceEngine

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class ForensicTimelineGenerator:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def generate_timeline(self, suspect_name, output_file=None):
        """Build a unified chronological forensic timeline for a given suspect across all 8 datasets."""
        if output_file is None:
            output_file = os.path.join(self.engine.data_folder, f"timeline_{suspect_name.replace(' ', '_')}.html")

        events = []

        # 1. FIR events
        firs = self.engine.firs_df[self.engine.firs_df['accused_name'] == suspect_name]
        for _, f in firs.iterrows():
            events.append({
                "timestamp": str(f['date_time_fir']),
                "category": "FIR Filed",
                "color": "#ef4444",
                "title": f"FIR #{f['fir_number']} Registered",
                "description": f"Police Station: {f['police_station']} | Section: {f['act_and_sections']} | IO: {f['investigating_officer']}"
            })

        # 2. CDR Calls
        phone = self.engine.name_to_phone.get(suspect_name, '')
        cdrs = self.engine.cdrs_df[(self.engine.cdrs_df['caller_number'] == phone) | (self.engine.cdrs_df['receiver_number'] == phone)]
        for _, c in cdrs.iterrows():
            other_phone = c['receiver_number'] if c['caller_number'] == phone else c['caller_number']
            other_name = self.engine.phone_to_name.get(other_phone, other_phone)
            events.append({
                "timestamp": str(c['timestamp']),
                "category": "CDR Call Log",
                "color": "#38bdf8",
                "title": f"Call/SMS with {other_name}",
                "description": f"Type: {c['call_type']} | Duration: {c['duration_seconds']}s | Tower: {c['cell_tower_location']}"
            })

        # 3. CCTV Sightings
        cctv = self.engine.cctv_df[self.engine.cctv_df['suspect_name'] == suspect_name]
        for _, v in cctv.iterrows():
            events.append({
                "timestamp": str(v['sighting_timestamp']),
                "category": "CCTV Sighting",
                "color": "#f59e0b",
                "title": f"CCTV Camera {v['camera_id']} Sighting",
                "description": f"Location: {v['camera_location']} | Match Confidence: {v['match_confidence']*100}% | Status: {v['sighting_status']}"
            })

        # 4. Financial Transactions
        fin = self.engine.fin_df[self.engine.fin_df['account_holder'] == suspect_name]
        for _, t in fin.iterrows():
            events.append({
                "timestamp": str(t['timestamp']),
                "category": "Financial Transaction",
                "color": "#10b981",
                "title": f"Payment: INR {t['amount_inr']} ({t['status']})",
                "description": f"Mode: {t['payment_mode']} | Payee: {t['merchant_or_payee']}"
            })

        # Sort events by timestamp
        events.sort(key=lambda x: str(x['timestamp']))
        events_json = json.dumps(events)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forensic Timeline - {suspect_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .header {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 30px; }}
        h1 {{ margin: 0 0 5px 0; color: #38bdf8; }}
        .timeline {{ position: relative; max-width: 900px; margin: 0 auto; }}
        .timeline::after {{ content: ''; position: absolute; width: 4px; background-color: #334155; top: 0; bottom: 0; left: 50%; margin-left: -2px; }}
        .container {{ padding: 10px 40px; position: relative; background-color: inherit; width: 45%; }}
        .left {{ left: 0; }}
        .right {{ left: 50%; }}
        .container::after {{ content: ''; position: absolute; width: 16px; height: 16px; right: -8px; background-color: #38bdf8; border: 3px solid #0f172a; top: 15px; border-radius: 50%; z-index: 1; }}
        .right::after {{ left: -8px; }}
        .content {{ padding: 15px 20px; background-color: #1e293b; position: relative; border-radius: 10px; border: 1px solid #334155; }}
        .badge {{ display: inline-block; padding: 3px 8px; font-size: 11px; font-weight: bold; border-radius: 4px; color: #fff; margin-bottom: 8px; }}
        .timestamp {{ font-size: 12px; color: #94a3b8; font-weight: bold; margin-bottom: 4px; }}
        .title {{ font-size: 15px; font-weight: bold; margin-bottom: 6px; }}
        .desc {{ font-size: 13px; color: #cbd5e1; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🕵️ FORENSIC TIMELINE: {suspect_name.upper()}</h1>
        <p>Total Events Tracked: {len(events)} | Phone: {phone}</p>
    </div>

    <div class="timeline" id="timeline-body"></div>

    <script>
        const events = {events_json};
        const body = document.getElementById("timeline-body");

        events.forEach((ev, idx) => {{
            const container = document.createElement("div");
            container.className = "container " + (idx % 2 === 0 ? "left" : "right");

            container.innerHTML = `
                <div class="content">
                    <span class="badge" style="background-color: ${{ev.color}}">${{ev.category}}</span>
                    <div class="timestamp">⏰ ${{ev.timestamp}}</div>
                    <div class="title">${{ev.title}}</div>
                    <div class="desc">${{ev.description}}</div>
                </div>
            `;
            body.appendChild(container);
        }});
    </script>
</body>
</html>
"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_template)

        print(f"Generated Forensic Timeline HTML -> {output_file}")
        return output_file

if __name__ == "__main__":
    ftg = ForensicTimelineGenerator()
    scores = ftg.engine.calculate_threat_scores()
    top_suspect = scores.iloc[0]['suspect_name']
    ftg.generate_timeline(top_suspect)
