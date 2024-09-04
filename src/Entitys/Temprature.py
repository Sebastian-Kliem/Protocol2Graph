class Temprature:
    """
    Represents a temperature measurement.
    """

    def __init__(self, t1, t2, hf, date, time):
        self.t1 = float(t1)
        self.t2 = float(t2)
        self.hf = float(hf)
        self.ct = 0
        self.date = date
        self.time = time


