
def main():
    manifest_data = parseManifest("sampleManifest.txt")
    for container in manifest_data:
        print(container)
        
def parseManifest(filePath):
    manifest = []

    with open(filePath, 'r') as file:
        # update log with "Manifest name.txt is opened"
        for line in file:
            line = line.strip()
            locationPart, weightPart, descriptionPart = line.split(", ")
            location = tuple(map(int, locationPart.strip("[]").split(',')))
            weight = int(weightPart.strip("{}"))
            description = descriptionPart
            manifest.append([location, weight, description])

    return manifest

# def updateMaifest():
#     # insert code

# def load():
#     # insert code   

# def unload():
#     # insert code

# def balance():
#     # insert code

# def updateLog():
#     # insert code

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()
