class LocationDelegate:
    def __init__(self, current_location=None):
        self.current_location = current_location
        self.available_locations = []

    def set_current_location(self, current_location):
        self.current_location = current_location

    def get_current_location(self):
        return self.current_location

    def get_available_locations(self, context_format=False):
        if context_format:
            return "[" + ", ".join(self.available_locations) + "]"
        else:
            return self.available_locations

    def add_location(self, location):
        self.available_locations.append(location)

    def remove_location(self, location):
        self.available_locations.remove(location)

    def clear_locations(self):
        self.current_location = None
        self.available_locations.clear()

    def add_all_locations(self, locations):
        for location in locations:
            self.add_location(location)
