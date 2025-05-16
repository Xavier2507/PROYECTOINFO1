class NavPoint:
    def __init__(self, number, name, latitude, longitude):
        self.number = int(number)
        self.name = name
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.neighbors = []

    def add_neighbor(self, nav_point):
        if nav_point not in self.neighbors:
            self.neighbors.append(nav_point)

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"
