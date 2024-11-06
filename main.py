from datetime import datetime
import pytz
from container import container

def main():
    # updateLog()
    manifestData = parseManifest("sampleManifest.txt")
    for container in manifestData:
        container.printContainer()
        
def parseManifest(filePath):
    # stores container objects
    manifest = []

    with open(filePath, 'r') as file:
        # update log with "Manifest name.txt is opened"
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

def updateLog():
    pstTimezone = pytz.timezone('America/Los_Angeles')
    pstTime = datetime.now(pstTimezone)
    pstTimeFormatted = pstTime.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    print(pstTimeFormatted)

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()
