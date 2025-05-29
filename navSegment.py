class NavSegment:
    def __init__(self, origin_number, destination_number, distance):
        self.origin_number = int(origin_number)
        self.destination_number = int(destination_number)
        self.distance = float(distance)

    def __str__(self):
        return f"{self.origin_number} → {self.destination_number} ({self.distance:.2f} km)"
