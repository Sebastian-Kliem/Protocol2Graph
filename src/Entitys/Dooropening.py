class Door:
    """
    Class to represent a door in the building.
    """

    def __init__(self):
        self.open_time = None
        self.close_time = None

    def __str__(self):
        return f"""
        open time: {self.open_time}, close time: {self.close_time} 
        """
