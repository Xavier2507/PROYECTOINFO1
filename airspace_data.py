from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport

class AirSpace:
    def __init__(self):
        self.navpoints = {}
        self.navsegments = []
        self.airports = []

    def load_from_files(self, nav_file, seg_file, aer_file=None):
        with open(nav_file) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 4:
                    number, name, lat, lon = parts
                    self.navpoints[int(number)] = NavPoint(number, name, lat, lon)

        with open(seg_file) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    origin, dest, dist = parts
                    seg = NavSegment(origin, dest, dist)
                    self.navsegments.append(seg)

                    if int(origin) in self.navpoints and int(dest) in self.navpoints:
                        self.navpoints[int(origin)].add_neighbor(self.navpoints[int(dest)])

        if aer_file:
            with open(aer_file) as f:
                current_airport = None
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.isupper() and "." not in line:
                        current_airport = NavAirport(line)
                        self.airports.append(current_airport)
                    elif line.endswith(".D") and current_airport:
                        current_airport.add_sid(line)
                    elif line.endswith(".A") and current_airport:
                        current_airport.add_star(line)
