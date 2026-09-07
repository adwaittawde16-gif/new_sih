import os

def patch_app_py():
    app_path = "app.py"
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add imports
    imports_to_add = """from financial_analyzer import FinancialAnalyzer
from nocturnal_call_analyzer import NocturnalCallAnalyzer
from social_media_timeline import SocialMediaTimeline
from co_accused_network import CoAccusedNetwork
from surveillance_heatmap import SurveillanceHeatmap
"""
    content = content.replace(
        "from financial_analyzer import FinancialAnalyzer\nfrom nocturnal_call_analyzer import NocturnalCallAnalyzer",
        imports_to_add
    )

    # Add radio options
    radio_opts_old = """            "7. Geospatial CCTV Meeting Map",
            "8. Interactive D3 Network Graph"
        ]"""
    radio_opts_new = """            "7. Geospatial CCTV Meeting Map",
            "8. Interactive D3 Network Graph",
            "9. Social Media Timeline",
            "10. Co-Accused FIR Network",
            "11. Surveillance Heatmap"
        ]"""
    content = content.replace(radio_opts_old, radio_opts_new)

    # Add new tabs logic at the end
    new_tabs = """    elif option == "9. Social Media Timeline":
        st.header("📱 Part 9: Social Media Timeline")
        st.markdown("Chronological footprint of suspect social media logins and platform activity.")
        smt = SocialMediaTimeline(engine)
        suspects = smt.sm_logins['suspect_name'].dropna().unique().tolist()
        if suspects:
            selected_name = st.selectbox("Select Suspect:", sorted(suspects))
            html_file = smt.generate_html_timeline(selected_name)
            with open(html_file, "r", encoding="utf-8") as f:
                html_code = f.read()
            components.html(html_code, height=750, scrolling=True)
        else:
            st.warning("No social media events found.")

    elif option == "10. Co-Accused FIR Network":
        st.header("🔗 Part 10: Co-Accused FIR Network")
        st.markdown("Network graph of suspects sharing the same FIRs.")
        net = CoAccusedNetwork(engine)
        html_file = net.generate_html_graph(max_nodes=60)
        with open(html_file, "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=750, scrolling=True)

    elif option == "11. Surveillance Heatmap":
        st.header("🔥 Part 11: Surveillance Observations Heatmap")
        st.markdown("Geospatial heatmap showing frequency of physical surveillance sightings.")
        shm = SurveillanceHeatmap(engine)
        html_file = shm.generate_heatmap()
        with open(html_file, "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=750, scrolling=True)
"""
    content = content + "\n" + new_tabs
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)

def patch_main_py():
    main_path = "main.py"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add imports
    imports_to_add = """from cell_tower_tracker import CellTowerTracker
from social_media_timeline import SocialMediaTimeline
from co_accused_network import CoAccusedNetwork
from surveillance_heatmap import SurveillanceHeatmap
"""
    content = content.replace(
        "from cell_tower_tracker import CellTowerTracker",
        imports_to_add
    )

    # Add menu options
    menu_old = """    print("  [16] Export Executive Intelligence Summary (.md)")
    print("  [17] Export Top 10 Suspect Dossiers (.md)")
    print("  [18] Exit")"""
    menu_new = """    print("  [16] Export Executive Intelligence Summary (.md)")
    print("  [17] Export Top 10 Suspect Dossiers (.md)")
    print("  [18] Social Media Timeline (HTML)")
    print("  [19] Co-Accused FIR Network (HTML)")
    print("  [20] Surveillance Heatmap (HTML)")
    print("  [21] Exit")"""
    content = content.replace(menu_old, menu_new)

    # Add functions for options
    funcs_new = """def option_18_social_media(engine):
    print("\\n" + "=" * 60)
    print("OPTION 18: SOCIAL MEDIA TIMELINE")
    print("=" * 60)
    smt = SocialMediaTimeline(engine)
    suspects = smt.sm_logins['suspect_name'].dropna().unique().tolist()
    if not suspects:
        print("No social media data.")
        return
    s_name = input(f"\\nEnter suspect name (press Enter for '{suspects[0]}'): ").strip()
    if not s_name:
        s_name = suspects[0]
    smt.print_timeline(s_name)
    outfile = smt.generate_html_timeline(s_name)
    print(f"\\nSUCCESS: Timeline HTML -> {outfile}")

def option_19_co_accused(engine):
    print("\\n" + "=" * 60)
    print("OPTION 19: CO-ACCUSED FIR NETWORK")
    print("=" * 60)
    net = CoAccusedNetwork(engine)
    net.print_top_connected(5)
    outfile = net.generate_html_graph(max_nodes=60)
    print(f"\\nSUCCESS: Co-Accused Graph HTML -> {outfile}")

def option_20_heatmap(engine):
    print("\\n" + "=" * 60)
    print("OPTION 20: SURVEILLANCE HEATMAP")
    print("=" * 60)
    shm = SurveillanceHeatmap(engine)
    shm.print_summary(top_n=5)
    outfile = shm.generate_heatmap()
    print(f"\\nSUCCESS: Surveillance Heatmap HTML -> {outfile}")

"""
    content = content.replace("def main():", funcs_new + "def main():")

    # Add to main loop
    loop_old = """        elif choice == '17':
            option_17_export_dossiers(engine)
        elif choice == '18':
            print("\\nExiting Intelligence Analysis Tool. Stay safe!")
            break
        else:
            print("\\nInvalid choice. Please enter a number between 1 and 18.")"""
    loop_new = """        elif choice == '17':
            option_17_export_dossiers(engine)
        elif choice == '18':
            option_18_social_media(engine)
        elif choice == '19':
            option_19_co_accused(engine)
        elif choice == '20':
            option_20_heatmap(engine)
        elif choice == '21':
            print("\\nExiting Intelligence Analysis Tool. Stay safe!")
            break
        else:
            print("\\nInvalid choice. Please enter a number between 1 and 21.")"""
    content = content.replace(loop_old, loop_new)
    
    # Also fix the input prompt range
    content = content.replace("Enter choice [1-18]:", "Enter choice [1-21]:")

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    patch_app_py()
    patch_main_py()
    print("Patched app.py and main.py")
