import os
from intelligence_engine import IntelligenceEngine
from crime_ring_detector import CrimeRingDetector
from ring_visualizer import RingVisualizer

def export_all_ring_graphs(output_folder=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'\crime_rings_html"):
    """Export interactive D3 network HTML graphs for all detected Crime Rings."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    engine = IntelligenceEngine()
    detector = CrimeRingDetector(engine)
    visualizer = RingVisualizer(engine)
    
    syndicates = detector.detect_syndicates()
    print(f"Exporting Subgraph Visualizations for {len(syndicates)} Crime Rings into '{output_folder}'...")
    
    exported_files = []
    for idx, row in syndicates.iterrows():
        ring_id = row['syndicate_id']
        outfile = visualizer.generate_ring_html(ring_id, output_folder)
        if outfile:
            exported_files.append(outfile)

    print(f"Successfully exported {len(exported_files)} Crime Ring graph HTML files!")
    return exported_files

if __name__ == "__main__":
    export_all_ring_graphs()
