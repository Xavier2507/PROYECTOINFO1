airspace = AirSpace()
airspace.load_from_files("Cat_nav.txt", "Cat_seg.txt", "Cat_aer.txt")

id_to_navpoint = airspace.navpoints
coords = {np.number: (np.latitude, np.longitude) for np in id_to_navpoint.values()}

fig, ax = plt.subplots()

fake_nodes = {}
fake_lat, fake_lon = 40.0, 0.0

def get_coord(point_id):
    global fake_lat, fake_lon
    if point_id in coords:
        return coords[point_id]
    if point_id not in fake_nodes:
        fake_nodes[point_id] = (fake_lat, fake_lon)
        fake_lat += 0.05
        fake_lon += 0.05
    return fake_nodes[point_id]

for seg in airspace.navsegments:
    lat0, lon0 = get_coord(seg.origin_number)
    lat1, lon1 = get_coord(seg.destination_number)

    ax.annotate(
        '', xy=(lon1, lat1), xytext=(lon0, lat0),
        arrowprops=dict(arrowstyle="->", color='gray', lw=1, alpha=0.6)
    )

for np in id_to_navpoint.values():
    ax.plot(np.longitude, np.latitude, 'ko', markersize=3)
    ax.text(np.longitude + 0.02, np.latitude + 0.02, np.name, fontsize=8)

for pid, (lat, lon) in fake_nodes.items():
    ax.plot(lon, lat, 'ro', markersize=2)
    ax.text(lon + 0.01, lat + 0.01, f"{pid}", fontsize=6, color='red')

ax.set_title("Espacio aéreo completo (incluye nodos faltantes)")
ax.axis('equal')
plt.tight_layout()
plt.show()
