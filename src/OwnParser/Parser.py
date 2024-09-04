from datetime import datetime

from bs4 import BeautifulSoup

from src.Entitys.DeviceDetails import DeviceDetails
from src.Entitys.Dooropening import Door #Dooropening,
from src.Entitys.Temprature import Temprature


def getTempratures(tempraruesHtml) -> list:
    """
    Parses the temperature data from the given HTML and returns a list of temperature objects.
    :param tempraruesHtml:
    :return:
    """
    htmlTempratures = BeautifulSoup(tempraruesHtml, 'html.parser')

    articleNumber = ""
    serialNumber = ""
    appliance = ""
    printingDate = ""
    software = ""
    panel = ""
    measurement = ""

    temperatureObjects = []

    for tr in htmlTempratures.select("tr"):
        if "Article Number" in str(tr.text) or "Artikelnummer" in str(tr.text) or "Artikel Nummer" in str(tr.text):
            splitted = tr.text.split(':')
            articleNumber = splitted[1]
            continue

        if "Control Panel" in str(tr.text) or "Software Version" in str(tr.text):
            splitted = tr.text.split(':')
            software = splitted[1]
            continue

        if "Softwareversion" in str(tr.text) or "Steuerung" in str(tr.text):
            splitted = tr.text.split(':')
            software = splitted[1]
            continue

        if "Serial Nr" in str(tr.text) or "Seriennr" in str(tr.text) or "Serial number" in str(tr.text):
            splitted = tr.text.split(':')
            serialNumber = splitted[1]
            continue

        if "Appliance" in str(tr.text) or "Unit type" in str(tr.text) or "Gerätetyp" in str(tr.text):
            splitted = tr.text.split(':')
            appliance = splitted[1]
            continue

        if "Printing Date" in str(tr.text) or "Druckdatum" in str(tr.text):
            splitted = tr.text.split(':')
            printingDate = splitted[1]
            continue

        if "UM" in str(tr.text):
            splitted = tr.text.split(':')
            measurement = splitted[1]
            continue

        if "T1" in str(tr.text):
            colums = tr.select("td")

            datetimelist = colums[0].text.split(' ')
            date = datetimelist[0]
            time = datetimelist[1]

            splitted = colums[1].text.split(',')

            currentprogram = splitted[0]

            nextsplit = splitted[1].split(' ')
            # print(nextsplit)
            T1, T2, HF = 0.0, 0.0, 0.0
            for item in nextsplit:
                if "T1:" in item:
                    split = item.split(':')
                    T1 = split[1]
                if "T2:" in item:
                    split = item.split(':')
                    T2 = split[1]
                if "HF" in item:
                    split = item.split(':')
                    HF = split[1]

            temperatureObject = Temprature(T1, T2, HF, date, time)
            temperatureObject.currentprogram = currentprogram

            # get row for CT
            nextRow = tr.findNext('tr')
            if nextRow:
                if "CT" in tr.findNext('tr').text or "KT" in tr.findNext('tr').text:
                    ctRowsplitted = tr.findNext('tr').text.split(',')
                    ctlist = ctRowsplitted[1].split(":")
                    ct = ctlist[1]
                    if not ct == "0":
                        temperatureObject.ct = float(ct)

            temperatureObjects.append(temperatureObject)

    deviceDetails = DeviceDetails(articleNumber, serialNumber, appliance, printingDate, software)
    deviceDetails.measurement = measurement
    deviceDetails.panel = panel

    return [deviceDetails, temperatureObjects]


def getDooropenings(doorHtml):
    """
    Parses the door opening data from the given HTML and returns a list of door objects.
    :param doorHtml:
    :return:
    """
    htmlDoor = BeautifulSoup(doorHtml, 'html.parser')

    # doorobjects = []
    # for tr in htmlDoor.select("tr"):
    #     if "Open, Door" in str(tr.text):
    #     # if "Öffnen" in str(tr.text) or "Open, Door" in str(tr.text):
    #     #     print(tr.text)
    #         colums = tr.select("td")
    #
    #         datetimelist = colums[0].text.split(' ')
    #         date = datetimelist[0]
    #         time = datetimelist[1]
    #
    #         doorObject = Dooropening(1, date, time)
    #         doorobjects.append(doorObject)
    #
    #     if "Close, Door" in str(tr.text):
    #     # if "Schließen" == str(tr.text) or "Close, Door" in str(tr.text):
    #     #     print(tr.text)
    #         colums = tr.select("td")
    #
    #         datetimelist = colums[0].text.split(' ')
    #         date = datetimelist[0]
    #         time = datetimelist[1]
    #
    #         doorObject = Dooropening(0, date, time)
    #         doorobjects.append(doorObject)
    #
    # for item in doorobjects:
    #     print(item)
    # return doorobjects
    doors = []
    current_door = None
    for tr in htmlDoor.select("tr"):
        if "Open, Door" in str(tr.text) or "Öffnen, Tür" in str(tr.text):
            columns = tr.select("td")
            datetimelist = columns[0].text.split(' ')
            date = datetimelist[0]
            time = datetimelist[1]

            if current_door is None:  # Wenn kein aktuelles Tür-Objekt existiert, erstelle ein neues
                current_door = Door()

            current_door.open_time = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S")

        if "Close, Door" in str(tr.text) or "Schließen, Tür" in str(tr.text):
            columns = tr.select("td")
            datetimelist = columns[0].text.split(' ')
            date = datetimelist[0]
            time = datetimelist[1]

            if current_door is not None:
                current_door.close_time = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S")
                doors.append(current_door)  # Füge das vollständige Tür-Objekt zur Liste hinzu
                current_door = None  # Setze current_door zurück, um ein neues Objekt zu erstellen

    return doors
