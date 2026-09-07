"""
co_accused_network.py
---------------------
Maps co-accused relationships from FIR data.
Multiple suspects sharing the same FIR number are treated as co-accused.
Builds a co-accused graph and exposes:
  - Co-accused pairs list
  - Shared FIR network visualisation (HTML, D3)
  - Centrality ranking (suspects with most shared FIRs)
  - Cluster detection (groups of co-accused suspects)

Part of: CDR & CCTV Intelligence & Threat Analysis System
For: Brihanmumbai Police Department — SIH 2026
"""

import sys
import os
import pandas as pd
import json
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class CoAccusedNetwork:
    def __init__(self, engine=None, data_folder=None):
        if engine is None:
            from intelligence_engine import IntelligenceEngine
            folder = data_folder or os.path.dirname(os.path.abspath(__file__))
            engine = IntelligenceEngine(data_folder=folder)
            engine.load_data()
            engine.build_lookups()
        self.engine = engine
        self.fir_df = engine.firs_df
        self._build_network()

    # ------------------------------------------------------------------
    # Build co-accused graph from FIR data
    # ------------------------------------------------------------------
    def _build_network(self):
        """Group suspects by FIR number; build edge list."""
        fir_to_suspects = defaultdict(set)
        for _, row in self.fir_df.iterrows():
            fir = str(row.get('fir_number', '')).strip()
            name = str(row.get('accused_name', '')).strip()
            if fir and name:
                fir_to_suspects[fir].add(name)

        self.edges = []
        self.fir_to_suspects = {k: sorted(v) for k, v in fir_to_suspects.items()}

        for fir, suspects in self.fir_to_suspects.items():
            suspects = sorted(suspects)
            for i in range(len(suspects)):
                for j in range(i + 1, len(suspects)):
                    self.edges.append((suspects[i], suspects[j], fir))

        self.adjacency = defaultdict(lambda: defaultdict(list))
        for a, b, fir in self.edges:
            self.adjacency[a][b].append(fir)
            self.adjacency[b][a].append(fir)

        self.degree = {s: len(neighbors) for s, neighbors in self.adjacency.items()}

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------
    def get_co_accused(self, suspect_name: str) -> dict:
        """Return {co_accused_name: [shared_firs]} for a suspect."""
        name = suspect_name.strip()
        return dict(self.adjacency.get(name, {}))

    def shared_firs(self, suspect_a: str, suspect_b: str) -> list:
        """Return list of FIR numbers shared between two suspects."""
        a = suspect_a.strip()
        b = suspect_b.strip()
        return self.adjacency.get(a, {}).get(b, [])

    def top_connected(self, n: int = 10) -> list:
        """Return top-N suspects by co-accused count (degree centrality)."""
        return sorted(self.degree.items(), key=lambda x: -x[1])[:n]

    def get_fir_group(self, fir_number: str) -> list:
        """Return all suspects in a given FIR."""
        return self.fir_to_suspects.get(fir_number.strip(), [])

    # ------------------------------------------------------------------
    # Terminal display
    # ------------------------------------------------------------------
    def print_co_accused(self, suspect_name: str):
        co = self.get_co_accused(suspect_name)
        if not co:
            print(f"[!] No co-accused found for: {suspect_name}")
            return
        print(f"\n{'='*65}")
        print(f"  CO-ACCUSED NETWORK — {suspect_name}")
        print(f"{'='*65}")
        print(f"  Total co-accused: {len(co)}")
        print(f"{'-'*65}")
        for name, firs in sorted(co.items(), key=lambda x: -len(x[1])):
            print(f"  * {name:<35} Shared FIRs: {', '.join(firs)}")
        print()

    def print_top_connected(self, n: int = 10):
        print(f"\n{'='*65}")
        print(f"  TOP {n} MOST CO-ACCUSED SUSPECTS (Central Nodes)")
        print(f"{'='*65}")
        for rank, (name, deg) in enumerate(self.top_connected(n), 1):
            bar = '#' * min(deg, 30)
            print(f"  {rank:>2}. {name:<35} {bar} ({deg} co-accused)")
        print()

    def print_fir_group(self, fir_number: str):
        group = self.get_fir_group(fir_number)
        print(f"\n  FIR {fir_number} — Co-accused suspects ({len(group)}):")
        for name in group:
            print(f"    - {name}")
        print()

    # ------------------------------------------------------------------
    # D3 HTML Network Graph
    # ------------------------------------------------------------------
    def generate_html_graph(self, output_folder: str = None,
                            focus_suspect: str = None,
                            max_nodes: int = 60) -> str:
        """
        Generate an interactive D3 force-directed graph of the co-accused network.
        """
        output_folder = output_folder or os.path.dirname(os.path.abspath(__file__))

        if focus_suspect:
            co = self.get_co_accused(focus_suspect)
            names = {focus_suspect} | set(co.keys())
            edge_subset = [(a, b, firs) for a, b, firs in self.edges
                           if a in names and b in names]
            title = f"Co-Accused Network — {focus_suspect}"
            filename = f"co_accused_{focus_suspect.replace(' ','_').replace('.','')}.html"
        else:
            top_names = {n for n, _ in self.top_connected(max_nodes)}
            edge_subset = [(a, b, firs) for a, b, firs in self.edges
                           if a in top_names and b in top_names]
            names = set()
            for a, b, _ in edge_subset:
                names.add(a); names.add(b)
            title = f"Co-Accused Network (Top {len(names)} Suspects)"
            filename = "co_accused_network.html"

        node_list = sorted(names)
        node_idx = {n: i for i, n in enumerate(node_list)}

        nodes_json = json.dumps([{
            'id': i,
            'name': n,
            'degree': self.degree.get(n, 0),
            'group': min(self.degree.get(n, 0), 5),
        } for i, n in enumerate(node_list)])

        links_json = json.dumps([{
            'source': node_idx[a],
            'target': node_idx[b],
            'firs': firs,
            'weight': len(firs),
        } for a, b, firs in edge_subset
          if a in node_idx and b in node_idx])

        out_path = os.path.join(output_folder, filename)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; font-family: 'Segoe UI', Arial, sans-serif; overflow: hidden; }}
  #title {{ position: absolute; top: 12px; left: 20px; color: #58a6ff; font-size: 1.1rem; font-weight: 600; }}
  #stats {{ position: absolute; top: 40px; left: 20px; color: #8b949e; font-size: 0.78rem; }}
  #tooltip {{
    position: absolute; background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 10px 14px; color: #e6edf3; font-size: 0.82rem;
    pointer-events: none; display: none; max-width: 280px; line-height: 1.5;
  }}
  #legend {{ position: absolute; bottom: 20px; left: 20px; }}
  .leg-item {{ display: flex; align-items: center; gap: 8px; color: #8b949e; font-size: 0.75rem; margin-bottom: 4px; }}
  .leg-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  svg {{ width: 100vw; height: 100vh; }}
  line {{ stroke-opacity: 0.45; }}
</style>
</head>
<body>
<div id="title">&#x1F46A; {title}</div>
<div id="stats">Nodes: {len(node_list)} &nbsp;|&nbsp; Edges: {len(edge_subset)}</div>
<div id="tooltip"></div>
<svg id="graph"></svg>
<div id="legend">
  <div class="leg-item"><div class="leg-dot" style="background:#3fb950"></div> Low connectivity</div>
  <div class="leg-item"><div class="leg-dot" style="background:#d29922"></div> Medium</div>
  <div class="leg-item"><div class="leg-dot" style="background:#f85149"></div> High (Central Node)</div>
</div>
<script>
const nodes = {nodes_json};
const links = {links_json};

const colorScale = d3.scaleOrdinal()
  .domain([0,1,2,3,4,5])
  .range(['#3fb950','#58a6ff','#a5d6ff','#d29922','#f0883e','#f85149']);

const svg = d3.select('#graph');
const W = window.innerWidth, H = window.innerHeight;

const sim = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(d => 80 / (d.weight || 1)))
  .force('charge', d3.forceManyBody().strength(-180))
  .force('center', d3.forceCenter(W/2, H/2))
  .force('collision', d3.forceCollide(22));

const link = svg.append('g').selectAll('line')
  .data(links).enter().append('line')
  .attr('stroke', d => d.weight > 1 ? '#f85149' : '#30363d')
  .attr('stroke-width', d => Math.min(d.weight * 1.2, 5));

const node = svg.append('g').selectAll('circle')
  .data(nodes).enter().append('circle')
  .attr('r', d => 8 + Math.min(d.degree * 2, 18))
  .attr('fill', d => colorScale(d.group))
  .attr('stroke', '#0d1117').attr('stroke-width', 2)
  .call(d3.drag()
    .on('start', (e, d) => {{ if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
    .on('drag', (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
    .on('end', (e, d) => {{ if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }}));

const label = svg.append('g').selectAll('text')
  .data(nodes).enter().append('text')
  .text(d => d.name.replace('Md. ', ''))
  .attr('font-size', '9px').attr('fill', '#8b949e')
  .attr('text-anchor', 'middle').attr('dy', d => -12 - Math.min(d.degree, 9));

const tooltip = d3.select('#tooltip');
node.on('mouseover', (e, d) => {{
    const co = links.filter(l => l.source.id === d.id || l.target.id === d.id);
    tooltip.style('display','block')
      .html(`<strong>${{d.name}}</strong><br>Co-accused: ${{d.degree}}<br>Shared FIRs: ${{co.map(l => l.firs.join(', ')).join('; ')}}`);
  }})
  .on('mousemove', e => tooltip.style('left', (e.pageX+14)+'px').style('top', (e.pageY-28)+'px'))
  .on('mouseout', () => tooltip.style('display','none'));

sim.on('tick', () => {{
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('cx', d => d.x).attr('cy', d => d.y);
  label.attr('x', d => d.x).attr('y', d => d.y);
}});
</script>
</body>
</html>"""

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return out_path
