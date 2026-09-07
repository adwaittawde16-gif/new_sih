import os
import json
import pandas as pd
from intelligence_engine import IntelligenceEngine

# Coordinates map for Mumbai police station/CCTV zones
LOCATION_COORDS = {
    "Byculla West, Mumbai": (18.9780, 72.8300),
    "Metro Access Road, Byculla West, Mumbai": (18.9792, 72.8315),
    "Market Entrance, Byculla West, Mumbai": (18.9775, 72.8290),
    "Agripada, Mumbai": (18.9750, 72.8250),
    "Main Road Traffic Signal, Agripada, Mumbai": (18.9758, 72.8262),
    "Public Footpath Corner, Agripada, Mumbai": (18.9745, 72.8240),
    "Lower Parel, Mumbai": (18.9950, 72.8300),
    "Flyover Service Road, Lower Parel, Mumbai": (18.9962, 72.8318),
    "Public Footpath Corner, Lower Parel, Mumbai": (18.9940, 72.8288),
    "Market Entrance, Lower Parel, Mumbai": (18.9955, 72.8305),
    "Worli, Mumbai": (19.0150, 72.8180),
    "Main Road Traffic Signal, Worli, Mumbai": (19.0162, 72.8195),
    "Public Footpath Corner, Worli, Mumbai": (19.0140, 72.8170),
    "Grant Road, Mumbai": (18.9630, 72.8160),
    "Main Road Traffic Signal, Grant Road, Mumbai": (18.9642, 72.8175),
    "Bhadakamkar Marg, Lamington Road, Grant Road": (18.9625, 72.8155),
    "Dadar, Mumbai": (19.0180, 72.8430),
    "Station Road Junction, Dadar, Mumbai": (19.0192, 72.8445),
    "Market Entrance, Dadar, Mumbai": (19.0175, 72.8420),
    "Kalachowki, Mumbai": (18.9880, 72.8450),
    "Main Road Traffic Signal, Kalachowki, Mumbai": (18.9892, 72.8465),
    "Bus Stop Junction, Kalachowki, Mumbai": (18.9875, 72.8440),
    "Nagpada, Mumbai": (18.9680, 72.8280),
    "Shopping Lane Entrance, Nagpada, Mumbai": (18.9692, 72.8295)
}

class GeoMapGenerator:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def generate_interactive_map(self, output_file=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'\cctv_co_location_map.html"):
        """Generate a standalone Leaflet.js HTML map displaying CCTV locations and meeting encounters."""
        meetings = self.engine.get_cctv_meetings()
        cctv_df = self.engine.cctv_df.copy()

        # Prepare markers data
        markers = []
        for idx, row in cctv_df.iterrows():
            loc = row['camera_location']
            lat, lon = LOCATION_COORDS.get(loc, (18.9780 + (idx % 10)*0.005, 72.8300 + (idx % 10)*0.005))
            
            markers.append({
                "camera_id": str(row['camera_id']),
                "location": str(loc),
                "suspect": str(row['suspect_name']),
                "timestamp": str(row['sighting_timestamp']),
                "confidence": float(row['match_confidence']),
                "lat": lat,
                "lon": lon
            })

        meeting_lines = []
        if not meetings.empty:
            for idx, m in meetings.iterrows():
                loc = m['camera_location']
                lat, lon = LOCATION_COORDS.get(loc, (18.9780, 72.8300))
                meeting_lines.append({
                    "suspect_1": str(m['suspect_1']),
                    "suspect_2": str(m['suspect_2']),
                    "camera_id": str(m['camera_id']),
                    "location": str(loc),
                    "calls": int(m['cdr_call_count']),
                    "lat": lat,
                    "lon": lon
                })

        markers_json = json.dumps(markers)
        meetings_json = json.dumps(meeting_lines)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CCTV Co-Location & Meeting Hotspots Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; }}
        #header {{ position: absolute; top: 15px; left: 20px; z-index: 1000; background: rgba(15, 23, 42, 0.9); padding: 15px 25px; border-radius: 12px; border: 1px solid #334155; backdrop-filter: blur(8px); }}
        h1 {{ margin: 0 0 5px 0; font-size: 20px; color: #38bdf8; }}
        p {{ margin: 0; font-size: 13px; color: #94a3b8; }}
        #map {{ width: 100vw; height: 100vh; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>📍 Mumbai CCTV Physical Meeting Hotspots</h1>
        <p>Red Pulse Circles = Confirmed Physical Meetings | Blue Markers = Camera Sightings</p>
    </div>

    <div id="map"></div>

    <script>
        const map = L.map('map').setView([18.9800, 72.8300], 13);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            maxZoom: 19
        }}).addTo(map);

        const markers = {markers_json};
        const meetings = {meetings_json};

        // Add camera markers
        markers.forEach(m => {{
            const marker = L.circleMarker([m.lat, m.lon], {{
                radius: 6,
                fillColor: '#38bdf8',
                color: '#ffffff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }}).addTo(map);

            marker.bindPopup(`
                <div style="font-family:sans-serif; color:#0f172a;">
                    <h4 style="margin:0 0 5px 0;">📷 ${{m.camera_id}}</h4>
                    <p style="margin:0; font-size:12px;"><b>Location:</b> ${{m.location}}</p>
                    <p style="margin:0; font-size:12px;"><b>Suspect Sighted:</b> ${{m.suspect}}</p>
                    <p style="margin:0; font-size:12px;"><b>Time:</b> ${{m.timestamp}}</p>
                    <p style="margin:0; font-size:12px;"><b>Confidence:</b> ${{m.confidence * 100}}%</p>
                </div>
            `);
        }});

        // Add meeting pulse markers
        meetings.forEach(m => {{
            const meetingCircle = L.circle([m.lat, m.lon], {{
                radius: 120,
                fillColor: '#ef4444',
                color: '#ef4444',
                weight: 2,
                opacity: 0.9,
                fillOpacity: 0.4
            }}).addTo(map);

            meetingCircle.bindPopup(`
                <div style="font-family:sans-serif; color:#0f172a;">
                    <h4 style="margin:0 0 5px 0; color:#ef4444;">🤝 CONFIRMED PHYSICAL MEETING</h4>
                    <p style="margin:0; font-size:12px;"><b>Suspect 1:</b> ${{m.suspect_1}}</p>
                    <p style="margin:0; font-size:12px;"><b>Suspect 2:</b> ${{m.suspect_2}}</p>
                    <p style="margin:0; font-size:12px;"><b>Camera:</b> ${{m.camera_id}} (${{m.location}})</p>
                    <p style="margin:0; font-size:12px;"><b>Calls Exchanged:</b> ${{m.calls}} calls</p>
                </div>
            `);
        }});
    </script>
</body>
</html>
"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_template)

        print(f"Generated CCTV Geospatial Map -> {output_file}")
        return output_file

if __name__ == "__main__":
    geo = GeoMapGenerator()
    geo.generate_interactive_map()
