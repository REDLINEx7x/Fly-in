#from parser import Parser  # سمي الملف ديالك كيف ما مسميه

#def main():
#    # 1. Instantiate the parser
#    config_path = "config.txt"
#    parser = Parser(config_path)

#    try:
#        # 2. Start Parsing
#        print(f"--- Starting Parsing for: {config_path} ---")
#        parser.read_file()
#        print("--- Parsing Completed Successfully! ---\n")

#        # 3. Test Drones
#        print(f"Total Drones: {parser.drones}")

#        # 4. Test Start & End Zones
#        if parser.start_v:
#            print(f"Start Hub: {parser.start_v.name} at ({parser.start_v.x}, {parser.start_v.y})")
#        if parser.end_v:
#            print(f"End Hub: {parser.end_v.name} at ({parser.end_v.x}, {parser.end_v.y})")

#        # 5. List all Zones and their Metadata
#        print(f"\nTotal Zones Found: {len(parser.zones)}")
#        for name, zone in parser.zones.items():
#            meta = zone.metadata if zone.metadata else "No metadata"
#            print(f" - {name}: Meta={meta}")

#        # 6. List all Connections
#        print(f"\nTotal Connections Found: {len(parser.connections)}")
#        for conn in parser.connections:
#            print(f" - {conn.from_zone} <---> {conn.to_zone} | Metadata: {conn.metadata}")

#    except Exception as e:
#        print(f"\n[CRITICAL ERROR]: {e}")

#if __name__ == "__main__":
#    main()
