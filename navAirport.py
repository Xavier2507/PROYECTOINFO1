class NavAirport:
    def __init__(self, name):
        self.name = name
        self.SIDs = []
        self.STARs = []

    def add_sid(self, sid_name):
        if sid_name not in self.SIDs:
            self.SIDs.append(sid_name)

    def add_star(self, star_name):
        if star_name not in self.STARs:
            self.STARs.append(star_name)

    def __str__(self):
        return f"{self.name} - SIDs: {self.SIDs} - STARs: {self.STARs}"
