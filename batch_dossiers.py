import os
from intelligence_engine import IntelligenceEngine
from generate_dossier import generate_suspect_dossier

def generate_all_top_dossiers(top_n=10, output_folder=r"c:\Users\adwait\OneDrive\Desktop\new_sih26'\dossiers"):
    """Export comprehensive dossiers for top N threat suspects."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    engine = IntelligenceEngine()
    scores = engine.calculate_threat_scores()
    
    top_suspects = scores['suspect_name'].head(top_n).tolist()
    print(f"Generating Dossiers for Top {len(top_suspects)} Threat Suspects into '{output_folder}'...")
    
    generated_files = []
    for rank, name in enumerate(top_suspects, 1):
        file_path = generate_suspect_dossier(name, output_folder)
        if file_path:
            generated_files.append(file_path)
            
    print(f"\nSuccessfully generated {len(generated_files)} suspect dossiers!")
    return generated_files

if __name__ == "__main__":
    generate_all_top_dossiers(top_n=10)
