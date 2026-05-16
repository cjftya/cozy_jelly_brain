class LocationDelegate:
    def __init__(self, current_location=None, reason_of_change_location=None):
        self.current_location = current_location
        self.reason_of_change_location = reason_of_change_location
        self.available_locations = []

    def set_current_location(self, current_location):
        self.current_location = current_location

    def get_current_location(self):
        return self.current_location

    def set_reason_of_change_location(self, reason):
        self.reason_of_change_location = reason

    def get_reason_of_change_location(self):
        return self.reason_of_change_location

    def get_available_locations(self):
        return "\n".join([line for line in self.available_locations])

    def add_location(self, location):
        self.available_locations.append("- **" + location + "**")
    
    def remove_location(self, location):
        self.available_locations.remove("- **" + location + "**")

    def clear_locations(self):
        self.available_locations.clear()

    def add_all_locations(self, locations):
        for location in locations:
            self.add_location(location)