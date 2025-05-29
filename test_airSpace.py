from airspace_data import AirSpace

airspace = AirSpace()
airspace.load_from_files("Cat_nav.txt", "Cat_seg.txt", "Cat_aer.txt")

print(f"NavPoints cargados: {len(airspace.navpoints)}")
print(f"NavSegments cargados: {len(airspace.navsegments)}")
print(f"Aeropuertos cargados: {len(airspace.airports)}")

for ap in airspace.airports:
    print(ap)