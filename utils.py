from container import Container
from datetime import datetime
import pytz
import requests


# To get current PST time from an external source, helper for updateLog()
def getCurrentTime():
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/America/Los_Angeles")
        response.raise_for_status()  # Raises an exception if there is an error in the request
        data = response.json()
        datetimeString = data["datetime"]
        utcTime = datetime.strptime(datetimeString, "%Y-%m-%dT%H:%M:%S.%f%z")
        pstTimezone = pytz.timezone('America/Los_Angeles')
        pstTime = utcTime.astimezone(pstTimezone)
        return pstTime
    except requests.RequestException as e:
        print("Error fetching time:", e)
        return None

# To update log file with a message string
# USAGE: updateLog("Insert Message to log.txt")
def updateLog(message):
    pstTime = getCurrentTime()

    if 10<=pstTime.day % 100<=20: suffix = "th"
    else: suffix = {1:"st", 2:"nd", 3:"rd"}.get(pstTime.day % 10, "th")
    
    month_day_year = pstTime.strftime(f"%B {pstTime.day}{suffix} %Y")
    timePart = pstTime.strftime("%H:%M")
    pstTimeFormatted = f"{month_day_year}: {timePart}"
    logInput = f"{pstTimeFormatted} {message}"
    print(logInput)
    
    with open("KeoghsPort2024.txt", "a") as logFile:
        logFile.write(logInput + "\n")

# To store each container object from manifest.txt into a list
# USAGE: parseManifest("file/path/Manifest.txt")
def parseManifest(filePath):
    manifest = []

    with open(filePath, 'r') as file:
        updateLog("Manifest {} is opened".format(filePath))
        for line in file:
            line = line.strip()
            locationPart, weightPart, descriptionPart = line.split(", ")
            
            location = tuple(map(int, locationPart.strip("[]").split(',')))
            weight = int(weightPart.strip("{}"))
            description = descriptionPart

            newContainer = Container(location, weight, description)
            manifest.append(newContainer)

    return manifest

# To create a new Manifest file according to the ending state
# USAGE: updateMaifest(state_object, "file/path/Manifest.txt")
def updateMaifest(end_state, filePath):
    with open(filePath, "w") as file:
        for row_index, row in enumerate(end_state.state_representation, start=1):
            for col_index, container in enumerate(row, start=1):
                if isinstance(container, Container):
                    weight = f"{int(container.get_weight()):05}" if container.get_weight() else "00000"
                    description = container.get_description() if container.get_description() else "NAN"
                else:
                    weight = "00000"
                    description = "NAN"

                line = f"[{row_index:02},{col_index:02}], {{{weight}}}, {description}\n"
                file.write(line)

    updateLog("Manifest successfully updated in {}".format(filePath))