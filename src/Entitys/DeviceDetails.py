class DeviceDetails:
    """
    Class to represent device details
    """

    def __init__(self,
                 articleNumber,
                 serialNumber,
                 appliance,
                 printingDate,
                 software):

        self.articleNumber = articleNumber
        self.serialNumber = serialNumber
        self.appliance = appliance
        self.printingDate = printingDate
        self.software = software

