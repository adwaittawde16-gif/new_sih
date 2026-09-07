"""
social_media_timeline.py
------------------------
Cross-platform social media event timeline for a suspect.
Shows login/logout events across all platforms in chronological order
and generates an interactive HTML timeline.

Part of: CDR & CCTV Intelligence & Threat Analysis System
For: Brihanmumbai Police Department — SIH 2026
"""

import sys
import os
import pandas as pd
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class SocialMediaTimeline:
    def __init__(self, engine=None, data_folder=None):
        if engine is None:
            from intelligence_engine import IntelligenceEngine
            folder = data_folder or os.path.dirname(os.path.abspath(__file__))
            engine = IntelligenceEngine(data_folder=folder)
            engine.load_data()
            engine.build_lookups()
        self.engine = engine
        self.sm_logins = engine.soc_login_df  # social_media_login_tracking.csv
        self.sm_intel = engine.soc_intel_df   # social_media_intelligence.csv

    # ------------------------------------------------------------------
    # Core: Build timeline events for a suspect
    # ------------------------------------------------------------------
    def build_timeline(self, suspect_name: str) -> list[dict]:
        """Return chronologically sorted events for the suspect."""
        events = []

        # --- Login/logout events from social_media_login_tracking ---
        login_df = self.sm_logins[
            self.sm_logins['suspect_name'].str.strip().str.lower()
            == suspect_name.strip().lower()
        ]
        for _, row in login_df.iterrows():
            ts_raw = str(row.get('timestamp', '')).strip()
            ts = self._parse_ts(ts_raw)
            events.append({
                'timestamp': ts,
                'timestamp_str': ts_raw,
                'source': 'Login Tracker',
                'platform': str(row.get('platform', 'Unknown')),
                'event_type': str(row.get('event_type', 'Unknown')),
                'location': str(row.get('approximate_location', 'Unknown')),
                'device': str(row.get('device_type', 'Unknown')),
                'network': str(row.get('network_type', 'Unknown')),
                'fir': str(row.get('fir_number', '')),
                'detail': (
                    f"{row.get('event_type','?')} on {row.get('platform','?')} "
                    f"from {row.get('approximate_location','?')} via {row.get('device_type','?')}"
                ),
            })

        # --- Intelligence profile events from social_media_intelligence ---
        intel_row = self.sm_intel[
            self.sm_intel['suspect_name'].str.strip().str.lower()
            == suspect_name.strip().lower()
        ]
        for _, r in intel_row.iterrows():
            last_act = str(r.get('timestamp', '')).strip()
            ts = self._parse_ts(last_act)
            events.append({
                'timestamp': ts,
                'timestamp_str': last_act,
                'source': 'Intel Profile',
                'platform': str(r.get('platform', 'Unknown')),
                'event_type': 'Social Post',
                'location': str(r.get('check_in_location', 'Unknown')),
                'device': 'N/A',
                'network': 'N/A',
                'fir': str(r.get('fir_number', '')),
                'detail': (
                    f"Post on {r.get('platform','?')} — @{r.get('handle_username','?')} "
                    f"('{r.get('caption_snippet','')}') at {r.get('check_in_location','?')}"
                ),
            })

        # Sort chronologically (unknowns go to end)
        events.sort(key=lambda e: e['timestamp'] or datetime.max)
        return events

    def _parse_ts(self, ts_str: str):
        """Try multiple datetime formats; return None on failure."""
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y %H:%M', '%d/%m/%Y'):
            try:
                return datetime.strptime(ts_str, fmt)
            except (ValueError, TypeError):
                continue
        return None

    # ------------------------------------------------------------------
    # Terminal display
    # ------------------------------------------------------------------
    def print_timeline(self, suspect_name: str):
        events = self.build_timeline(suspect_name)
        if not events:
            print(f"[!] No social media events found for: {suspect_name}")
            return

        print(f"\n{'='*70}")
        print(f"  SOCIAL MEDIA TIMELINE — {suspect_name}")
        print(f"{'='*70}")
        print(f"  Total events: {len(events)}")
        print(f"{'='*70}\n")

        for i, ev in enumerate(events, 1):
            ts_display = ev['timestamp'].strftime('%Y-%m-%d %H:%M') if ev['timestamp'] else ev['timestamp_str']
            tag = {
                'Login': '[LOGIN ]',
                'Logout': '[LOGOUT]',
                'Post': '[POST  ]',
                'Social Post': '[POST  ]',
            }.get(ev['event_type'], '[EVENT ]')

            print(f"  {i:>3}. {tag} {ts_display}")
            print(f"       Platform : {ev['platform']}")
            print(f"       Detail   : {ev['detail']}")
            if ev['fir']:
                print(f"       FIR      : {ev['fir']}")
            print()

    # ------------------------------------------------------------------
    # HTML Timeline Generator
    # ------------------------------------------------------------------
    def generate_html_timeline(self, suspect_name: str, output_folder: str = None) -> str:
        events = self.build_timeline(suspect_name)
        output_folder = output_folder or os.path.dirname(os.path.abspath(__file__))

        platform_colors = {
            'WhatsApp': '#25D366',
            'Instagram': '#E1306C',
            'Facebook': '#1877F2',
            'Twitter': '#1DA1F2',
            'X': '#000000',
            'Telegram': '#0088CC',
            'YouTube': '#FF0000',
        }

        event_icons = {
            'Login': '&#x25B6;',
            'Logout': '&#x25A0;',
            'Post': '&#x270F;',
            'Social Post': '&#x270F;',
        }

        rows_html = ''
        for ev in events:
            ts_display = (ev['timestamp'].strftime('%Y-%m-%d %H:%M')
                          if ev['timestamp'] else ev['timestamp_str'] or 'Unknown time')
            color = platform_colors.get(ev['platform'], '#607D8B')
            icon = event_icons.get(ev['event_type'], '&#x25CF;')
            fir_badge = (f'<span class="fir-badge">FIR: {ev["fir"]}</span>'
                         if ev['fir'] else '')
            rows_html += f"""
            <div class="event-card">
                <div class="event-dot" style="background:{color}">{icon}</div>
                <div class="event-body">
                    <div class="event-header">
                        <span class="platform-tag" style="background:{color}">{ev['platform']}</span>
                        <span class="event-time">{ts_display}</span>
                        {fir_badge}
                    </div>
                    <div class="event-type">{ev['event_type']}</div>
                    <div class="event-detail">{ev['detail']}</div>
                    <div class="event-meta">
                        <span>&#x1F4CD; {ev['location']}</span>
                        <span>&#x1F4F1; {ev['device']}</span>
                        <span>&#x1F4E1; {ev['network']}</span>
                    </div>
                </div>
            </div>"""

        if not rows_html:
            rows_html = '<p style="color:#888;text-align:center;padding:40px;">No social media events found for this suspect.</p>'

        safe_name = suspect_name.replace(' ', '_').replace('.', '')
        filename = f"sm_timeline_{safe_name}.html"
        out_path = os.path.join(output_folder, filename)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Social Media Timeline — {suspect_name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #0d1117; color: #e6edf3;
    padding: 30px;
  }}
  h1 {{
    color: #58a6ff; font-size: 1.6rem; margin-bottom: 6px;
    border-bottom: 2px solid #21262d; padding-bottom: 10px;
  }}
  .meta {{ color: #8b949e; font-size: 0.85rem; margin-bottom: 30px; }}
  .timeline {{
    position: relative;
    padding-left: 60px;
    border-left: 3px solid #21262d;
    margin-left: 20px;
  }}
  .event-card {{
    display: flex;
    align-items: flex-start;
    margin-bottom: 28px;
    position: relative;
  }}
  .event-dot {{
    position: absolute;
    left: -72px;
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; color: #fff;
    border: 3px solid #0d1117;
    flex-shrink: 0;
  }}
  .event-body {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px 18px;
    width: 100%;
  }}
  .event-header {{
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    margin-bottom: 8px;
  }}
  .platform-tag {{
    padding: 2px 10px; border-radius: 12px;
    color: #fff; font-size: 0.78rem; font-weight: 600;
  }}
  .event-time {{
    color: #8b949e; font-size: 0.82rem;
  }}
  .fir-badge {{
    background: #f85149; color: #fff;
    padding: 2px 8px; border-radius: 8px; font-size: 0.75rem;
  }}
  .event-type {{
    font-weight: 600; font-size: 0.95rem; color: #e6edf3;
    margin-bottom: 6px;
  }}
  .event-detail {{
    color: #c9d1d9; font-size: 0.87rem; margin-bottom: 8px;
    line-height: 1.5;
  }}
  .event-meta {{
    display: flex; gap: 16px; flex-wrap: wrap;
    color: #6e7681; font-size: 0.78rem;
  }}
  .header-bar {{
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 16px 20px; margin-bottom: 28px;
    display: flex; gap: 30px; flex-wrap: wrap;
  }}
  .stat {{ text-align: center; }}
  .stat-num {{ font-size: 1.5rem; font-weight: 700; color: #58a6ff; }}
  .stat-lbl {{ font-size: 0.75rem; color: #8b949e; }}
</style>
</head>
<body>
<h1>&#x1F4F1; Social Media Intelligence Timeline</h1>
<div class="meta">Suspect: <strong>{suspect_name}</strong> &nbsp;|&nbsp; Total Events: <strong>{len(events)}</strong> &nbsp;|&nbsp; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
<div class="header-bar">
  <div class="stat"><div class="stat-num">{len(events)}</div><div class="stat-lbl">Total Events</div></div>
  <div class="stat"><div class="stat-num">{len(set(e['platform'] for e in events))}</div><div class="stat-lbl">Platforms</div></div>
  <div class="stat"><div class="stat-num">{sum(1 for e in events if e['event_type']=='Login')}</div><div class="stat-lbl">Logins</div></div>
  <div class="stat"><div class="stat-num">{sum(1 for e in events if e['event_type']=='Logout')}</div><div class="stat-lbl">Logouts</div></div>
  <div class="stat"><div class="stat-num">{len(set(e['location'] for e in events if e['location'] not in ('Unknown','N/A','')))}</div><div class="stat-lbl">Unique Locations</div></div>
</div>
<div class="timeline">
{rows_html}
</div>
</body>
</html>"""

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return out_path
