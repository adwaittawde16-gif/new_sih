import os
import json
import networkx as nx
from intelligence_engine import IntelligenceEngine

class GraphVisualizer:
    def __init__(self, engine=None):
        self.engine = engine if engine else IntelligenceEngine()

    def generate_interactive_html_graph(self, output_file=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'\cdr_network_graph.html"):
        """Generate an interactive standalone D3/JS HTML network graph visualization."""
        pair_df, _ = self.engine.get_cdr_summary()
        cctv_meetings = self.engine.get_cctv_meetings()
        threat_scores = self.engine.calculate_threat_scores()

        score_dict = dict(zip(threat_scores['suspect_name'], threat_scores['total_threat_score']))
        phone_dict = dict(zip(threat_scores['suspect_name'], threat_scores['phone_number']))

        G = nx.Graph()

        # Add edges from CDR pairs
        for _, row in pair_df.iterrows():
            u, v = str(row['suspect_1']), str(row['suspect_2'])
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

        # Set node attributes safely for all nodes in graph
        for n in G.nodes():
            G.nodes[n]['threat_score'] = float(score_dict.get(n, 0.0))
            G.nodes[n]['phone'] = str(phone_dict.get(n, 'N/A'))

        # Prepare JSON data for D3
        nodes = []
        for n, d in G.nodes(data=True):
            deg = G.degree(n)
            nodes.append({
                "id": str(n),
                "score": d.get('threat_score', 0.0),
                "phone": d.get('phone', 'N/A'),
                "connections": int(deg)
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

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CDR & CCTV Intelligence Network Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #0f172a;
            color: #f8fafc;
            overflow: hidden;
        }}
        #header {{
            position: absolute;
            top: 15px;
            left: 20px;
            z-index: 10;
            background: rgba(15, 23, 42, 0.85);
            padding: 15px 25px;
            border-radius: 12px;
            border: 1px solid #334155;
            backdrop-filter: blur(8px);
        }}
        h1 {{ margin: 0 0 5px 0; font-size: 22px; color: #38bdf8; }}
        p {{ margin: 0; font-size: 13px; color: #94a3b8; }}
        #legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 10;
            background: rgba(15, 23, 42, 0.85);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #334155;
            font-size: 12px;
        }}
        .legend-item {{ display: flex; align-items: center; margin-bottom: 6px; }}
        .legend-color {{ width: 14px; height: 14px; border-radius: 50%; margin-right: 8px; }}
        #details {{
            position: absolute;
            top: 15px;
            right: 20px;
            width: 320px;
            z-index: 10;
            background: rgba(15, 23, 42, 0.9);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #334155;
            backdrop-filter: blur(8px);
            display: none;
        }}
        #details h3 {{ margin-top: 0; color: #f43f5e; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
        svg {{ width: 100vw; height: 100vh; }}
        .node {{ cursor: pointer; stroke: #fff; stroke-width: 1.5px; }}
        .link {{ stroke-opacity: 0.7; }}
        .link.meeting {{ stroke: #ef4444; stroke-width: 3px; stroke-dasharray: 4; }}
        .link.normal {{ stroke: #38bdf8; }}
        text {{ font-size: 10px; fill: #cbd5e1; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🕵️ CDR & CCTV Network Topology</h1>
        <p>Red Dashed Links = Confirmed CCTV Physical Meetings | Node Color = Threat Score</p>
    </div>

    <div id="legend">
        <div class="legend-item"><div class="legend-color" style="background:#ef4444;"></div> High Threat Score (&gt; 70)</div>
        <div class="legend-item"><div class="legend-color" style="background:#f59e0b;"></div> Medium Threat Score (40 - 70)</div>
        <div class="legend-item"><div class="legend-color" style="background:#10b981;"></div> Low Threat Score (&lt; 40)</div>
        <div class="legend-item"><span style="color:#ef4444; font-weight:bold; margin-right:6px;">- - -</span> Confirmed Physical Meeting</div>
    </div>

    <div id="details">
        <h3 id="det-name">Suspect Details</h3>
        <p><strong>Phone:</strong> <span id="det-phone"></span></p>
        <p><strong>Threat Score:</strong> <span id="det-score" style="font-weight:bold; color:#ef4444;"></span> / 100</p>
        <p><strong>Active Network Connections:</strong> <span id="det-conn"></span></p>
    </div>

    <svg id="graph"></svg>

    <script>
        const data = {graph_json};

        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph");

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const colorScale = d3.scaleSequential()
            .domain([0, 100])
            .interpolator(d3.interpolateRgb("#10b981", "#ef4444"));

        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("class", d => d.meeting ? "link meeting" : "link normal")
            .attr("stroke-width", d => Math.max(1.5, d.calls * 0.8));

        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => 6 + Math.sqrt(d.connections) * 3)
            .attr("fill", d => colorScale(d.score))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const label = svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .enter().append("text")
            .text(d => d.id)
            .attr("dx", 12)
            .attr("dy", 4);

        node.on("click", (event, d) => {{
            d3.select("#details").style("display", "block");
            d3.select("#det-name").text(d.id);
            d3.select("#det-phone").text(d.phone);
            d3.select("#det-score").text(d.score);
            d3.select("#det-conn").text(d.connections);
        }});

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
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_template)

        print(f"Generated Interactive Network Graph HTML -> {output_file}")
        return output_file

if __name__ == "__main__":
    viz = GraphVisualizer()
    viz.generate_interactive_html_graph()
