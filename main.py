from datetime import datetime
import pytz
import requests
from container import container

def main():
    updateLog("Insert Message to log.txt")
    
    manifestData = parseManifest("sampleManifest.txt")
    for container in manifestData:
        container.printContainer()
        
# To store each container object from manifest.txt into a list
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

            newContainer = container(location, weight, description)
            manifest.append(newContainer)

    return manifest

# def updateMaifest():
#     # insert code

# def load():
#     # insert code   

# def unload():
#     # insert code

# def balance():
#     # insert code

# To get current PST time from an external source, for updateLog()
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
    
    with open("log.txt", "a") as logFile:
        logFile.write(logInput + "\n")

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()
