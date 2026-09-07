"""
surveillance_heatmap.py
-----------------------
Generates an HTML heatmap from surveillance report observations.
Uses surveillance_reports.csv (engine.surv_df) to:
  - Count observations per location
  - Map suspect sightings to a Leaflet.js heatmap layer
  - Export location-frequency analytics as a table

Part of: CDR & CCTV Intelligence & Threat Analysis System
For: Brihanmumbai Police Department — SIH 2026
"""

import sys
import os
import json
import pandas as pd
from collections import defaultdict, Counter
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Mumbai area location → approximate lat/lon mapping
MUMBAI_GEOCODES = {
    'byculla':               (18.9804, 72.8368),
    'dharavi':               (19.0440, 72.8568),
    'wadala':                (19.0178, 72.8478),
    'kurla':                 (19.0726, 72.8795),
    'chembur':               (19.0520, 72.8990),
    'sion':                  (19.0397, 72.8606),
    'matunga':               (19.0244, 72.8418),
    'parel':                 (18.9958, 72.8363),
    'lalbaug':               (18.9996, 72.8346),
    'worli':                 (18.9988, 72.8180),
    'dadar':                 (19.0178, 72.8478),
    'mahim':                 (19.0388, 72.8441),
    'bandra':                (19.0596, 72.8295),
    'andheri':               (19.1136, 72.8697),
    'malad':                 (19.1872, 72.8481),
    'borivali':              (19.2307, 72.8567),
    'goregaon':              (19.1663, 72.8526),
    'kandivali':             (19.2046, 72.8472),
    'ghatkopar':             (19.0858, 72.9081),
    'vikhroli':              (19.1035, 72.9254),
    'mulund':                (19.1727, 72.9564),
    'thane':                 (19.2183, 72.9781),
    'navi mumbai':           (19.0330, 73.0297),
    'colaba':                (18.9067, 72.8147),
    'fort':                  (18.9340, 72.8340),
    'churchgate':            (18.9322, 72.8264),
    'nariman point':         (18.9247, 72.8238),
    'grant road':            (18.9637, 72.8221),
    'mumbai central':        (18.9696, 72.8205),
    'lower parel':           (18.9947, 72.8258),
    'agripada':              (18.9717, 72.8239),
    'kalachowki':            (18.9793, 72.8319),
    'sewri':                 (18.9980, 72.8537),
    'cotton green':          (18.9890, 72.8497),
    'dockyard road':         (18.9876, 72.8482),
    'reay road':             (18.9851, 72.8450),
    'chinchpokli':           (18.9751, 72.8338),
    'mazgaon':               (18.9650, 72.8406),
    'sandhurst road':        (18.9607, 72.8363),
    'bhendi bazar':          (18.9547, 72.8348),
    'crawford market':       (18.9478, 72.8339),
    'nagpada':               (18.9589, 72.8256),
    'dongri':                (18.9505, 72.8350),
    'bhuleshwar':            (18.9462, 72.8286),
    'n.m. joshi marg':       (18.9750, 72.8296),
}


def geocode_location(location_str: str):
    if not location_str:
        return None
    loc_lower = location_str.lower()
    for key, coords in MUMBAI_GEOCODES.items():
        if key in loc_lower:
            return coords
    for key, coords in MUMBAI_GEOCODES.items():
        if any(word in loc_lower for word in key.split()):
            return coords
    return (19.0760, 72.8777)  # Fallback to Mumbai center


class SurveillanceHeatmap:
    def __init__(self, engine=None, data_folder=None):
        if engine is None:
            from intelligence_engine import IntelligenceEngine
            folder = data_folder or os.path.dirname(os.path.abspath(__file__))
            engine = IntelligenceEngine(data_folder=folder)
            engine.load_data()
            engine.build_lookups()
        self.engine = engine
        self.surv_df = engine.surv_df
        self.fir_df = engine.firs_df
        self._analyse()

    def _analyse(self):
        self.loc_counts = Counter()
        self.loc_suspects = defaultdict(set)
        self.loc_firs = defaultdict(set)
        self.heatmap_points = []

        # Build fir_number -> list of accused_name
        fir_to_accused = defaultdict(list)
        for _, r in self.fir_df.iterrows():
            fir = str(r.get('fir_number', '')).strip()
            name = str(r.get('accused_name', '')).strip()
            if fir and name:
                fir_to_accused[fir].append(name)

        for _, row in self.surv_df.iterrows():
            loc = str(row.get('spot_location', '')).strip()
            fir = str(row.get('fir_number', '')).strip()

            if not loc or loc.lower() in ('nan', ''):
                continue

            self.loc_counts[loc] += 1
            if fir:
                self.loc_firs[loc].add(fir)
                for name in fir_to_accused.get(fir, []):
                    self.loc_suspects[loc].add(name)

        for loc, count in self.loc_counts.items():
            coords = geocode_location(loc)
            if coords:
                import random
                jitter = lambda: (random.random() - 0.5) * 0.002
                lat, lon = coords[0] + jitter(), coords[1] + jitter()
                self.heatmap_points.append([lat, lon, count])

    def generate_heatmap(self, output_folder: str = None) -> str:
        output_folder = output_folder or os.path.dirname(os.path.abspath(__file__))

        table_rows = ''
        for rank, (loc, cnt) in enumerate(self.loc_counts.most_common(20), 1):
            suspects_list = ', '.join(sorted(self.loc_suspects[loc])[:3])
            if len(self.loc_suspects[loc]) > 3:
                suspects_list += f' +{len(self.loc_suspects[loc])-3}'
            table_rows += f"""<tr>
              <td>{rank}</td>
              <td>{loc}</td>
              <td><strong>{cnt}</strong></td>
              <td>{len(self.loc_suspects[loc])}</td>
              <td style="font-size:0.75rem">{suspects_list}</td>
            </tr>"""

        heatmap_json = json.dumps(self.heatmap_points)
        total_obs = len(self.surv_df)
        total_locs = len(self.loc_counts)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Surveillance Heatmap — Mumbai Intelligence</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Segoe UI',Arial,sans-serif; background:#0d1117; color:#e6edf3; display:flex; flex-direction:column; height:100vh; }}
  #header {{ background:#161b22; border-bottom:2px solid #f85149; padding:12px 20px; display:flex; align-items:center; gap:16px; flex-wrap:wrap; }}
  #header h1 {{ color:#f85149; font-size:1.1rem; }}
  .stat-pill {{ background:#21262d; border:1px solid #30363d; border-radius:20px; padding:4px 14px; font-size:0.8rem; }}
  .stat-pill strong {{ color:#58a6ff; }}
  #main {{ display:flex; flex:1; overflow:hidden; }}
  #map {{ flex:1; }}
  #sidebar {{
    width:420px; background:#161b22; border-left:1px solid #30363d;
    overflow-y:auto; padding:16px;
  }}
  #sidebar h2 {{ color:#58a6ff; font-size:0.95rem; margin-bottom:12px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.75rem; }}
  th {{ background:#21262d; color:#8b949e; padding:6px 8px; text-align:left; position:sticky; top:0; }}
  td {{ padding:5px 8px; border-bottom:1px solid #21262d; color:#c9d1d9; vertical-align:top; }}
  tr:hover td {{ background:#1c2128; }}
  td:nth-child(3) {{ color:#f0883e; text-align:center; }}
</style>
</head>
<body>
<div id="header">
  <h1>&#x1F525; Surveillance Heatmap — Brihanmumbai Police</h1>
  <div class="stat-pill">Observations: <strong>{total_obs}</strong></div>
  <div class="stat-pill">Locations: <strong>{total_locs}</strong></div>
  <div class="stat-pill">Geocoded: <strong>{len(self.heatmap_points)}</strong></div>
  <div class="stat-pill">Generated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</strong></div>
</div>
<div id="main">
  <div id="map"></div>
  <div id="sidebar">
    <h2>&#x1F4CA; Top 20 Surveilled Locations</h2>
    <table>
      <tr><th>#</th><th>Location</th><th>Obs.</th><th>Suspects</th><th>Top Suspects</th></tr>
      {table_rows}
    </table>
  </div>
</div>
<script>
const map = L.map('map').setView([19.0760, 72.8777], 13);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  maxZoom: 19
}}).addTo(map);

const points = {heatmap_json};
if (points.length > 0) {{
  L.heatLayer(points, {{
    radius: 35,
    blur: 25,
    maxZoom: 18,
    max: Math.max(...points.map(p => p[2])),
    gradient: {{0.2:'#1a237e', 0.4:'#0d47a1', 0.6:'#f9a825', 0.8:'#e65100', 1.0:'#b71c1c'}}
  }}).addTo(map);
}}

const topLocs = {json.dumps([
    {'lat': geocode_location(loc)[0], 'lon': geocode_location(loc)[1],
     'loc': loc, 'cnt': cnt,
     'suspects': len(self.loc_suspects[loc])}
    for loc, cnt in self.loc_counts.most_common(20)
    if geocode_location(loc)
])};

topLocs.forEach(l => {{
  L.circleMarker([l.lat, l.lon], {{
    radius: 6 + Math.min(l.cnt * 1.5, 18),
    fillColor: '#f85149', color: '#fff', weight: 1.5,
    fillOpacity: 0.85
  }}).addTo(map)
   .bindPopup(`<strong>${{l.loc}}</strong><br>Observations: ${{l.cnt}}<br>Suspects: ${{l.suspects}}`);
}});
</script>
</body>
</html>"""

        out_path = os.path.join(output_folder, 'surveillance_heatmap.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return out_path
