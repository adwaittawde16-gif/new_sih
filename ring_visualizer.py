import os
import sys
import json
import networkx as nx
from intelligence_engine import IntelligenceEngine
from crime_ring_detector import CrimeRingDetector

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class RingVisualizer:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()
        self.detector = CrimeRingDetector(self.engine)

    def generate_ring_html(self, ring_id="RING-01", output_folder=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'"):
        """Generate interactive HTML graph focused specifically on a target Crime Ring."""
        syndicates = self.detector.detect_syndicates()
        r_sub = syndicates[syndicates['syndicate_id'] == ring_id]
        
        if r_sub.empty:
            print(f"Crime Ring '{ring_id}' not found.")
            return None
            
        ring_data = r_sub.iloc[0]
        members = ring_data['members']
        
        pair_df, _ = self.engine.get_cdr_summary()
        cctv_meetings = self.engine.get_cctv_meetings()
        threat_scores = self.engine.calculate_threat_scores()
        
        score_dict = dict(zip(threat_scores['suspect_name'], threat_scores['total_threat_score']))
        phone_dict = dict(zip(threat_scores['suspect_name'], threat_scores['phone_number']))

        # Build Subgraph
        G = nx.Graph()
        for m in members:
            G.add_node(m, threat_score=score_dict.get(m, 0.0), phone=phone_dict.get(m, 'N/A'))

        for _, row in pair_df.iterrows():
            u, v = str(row['suspect_1']), str(row['suspect_2'])
            if u in members and v in members:
                calls = int(row['total_calls'])
                duration = float(row['total_duration_min'])
                
                has_meeting = False
                if not cctv_meetings.empty:
                    m_sub = cctv_meetings[
                        ((cctv_meetings['suspect_1'] == u) & (cctv_meetings['suspect_2'] == v)) |
                        ((cctv_meetings['suspect_1'] == v) & (cctv_meetings['suspect_2'] == u))
                    ]
                    has_meeting = not m_sub.empty

                G.add_edge(u, v, weight=calls, duration=duration, meeting=has_meeting)

        nodes = []
        for n, d in G.nodes(data=True):
            is_leader = (n == ring_data['ring_leader'])
            nodes.append({
                "id": str(n),
                "score": d.get('threat_score', 0.0),
                "phone": d.get('phone', 'N/A'),
                "is_leader": is_leader,
                "connections": int(G.degree(n))
            })

        links = []
        for u, v, d in G.edges(data=True):
            links.append({
                "source": str(u),
                "target": str(v),
                "calls": d.get('weight', 1),
                "duration": d.get('duration', 0.0),
                "meeting": bool(d.get('meeting', False))
            })

        graph_json = json.dumps({"nodes": nodes, "links": links})
        outfile = os.path.join(output_folder, f"ring_graph_{ring_id}.html")

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crime Ring Topology - {ring_id}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #0f172a; color: #f8fafc; overflow: hidden; }}
        #header {{ position: absolute; top: 15px; left: 20px; z-index: 10; background: rgba(15, 23, 42, 0.9); padding: 15px 25px; border-radius: 12px; border: 1px solid #334155; backdrop-filter: blur(8px); }}
        h1 {{ margin: 0 0 5px 0; font-size: 22px; color: #f43f5e; }}
        p {{ margin: 0; font-size: 13px; color: #94a3b8; }}
        svg {{ width: 100vw; height: 100vh; }}
        .node {{ cursor: pointer; stroke: #fff; stroke-width: 1.5px; }}
        .node.leader {{ stroke: #f43f5e; stroke-width: 4px; }}
        .link {{ stroke-opacity: 0.8; }}
        .link.meeting {{ stroke: #ef4444; stroke-width: 3.5px; stroke-dasharray: 4; }}
        .link.normal {{ stroke: #38bdf8; stroke-width: 1.5px; }}
        text {{ font-size: 11px; fill: #f8fafc; font-weight: bold; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🚨 CRIME RING NETWORK: {ring_id}</h1>
        <p><strong>Ring Leader:</strong> {ring_data['ring_leader']} (Threat Score: {ring_data['leader_threat_score']}/100)</p>
        <p><strong>Members:</strong> {ring_data['ring_size']} | <strong>Internal Calls:</strong> {ring_data['total_internal_calls']} | <strong>CCTV Meetings:</strong> {ring_data['physical_meetings_count']}</p>
    </div>

    <svg id="graph"></svg>

    <script>
        const data = {graph_json};
        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph");

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("class", d => d.meeting ? "link meeting" : "link normal");

        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("class", d => d.is_leader ? "node leader" : "node")
            .attr("r", d => d.is_leader ? 14 : 9)
            .attr("fill", d => d.is_leader ? "#f43f5e" : "#38bdf8")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const label = svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .enter().append("text")
            .text(d => (d.is_leader ? "👑 " : "") + d.id)
            .attr("dx", 15)
            .attr("dy", 4);

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
"""
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(html_template)

        print(f"Generated Crime Ring Subgraph HTML -> {outfile}")
        return outfile

if __name__ == "__main__":
    rv = RingVisualizer()
    rv.generate_ring_html("RING-01")
