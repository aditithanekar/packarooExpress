class container:
    def __init__(self, location, weight, description):
        self.location = location
        self.weight = weight
        self.description = description
        
        if description == "NAN":
            self.IsNAN = True
        else:
            self.IsNAN = False
            
        if description == "UNUSED":
            self.IsUNUSED = True
        else:
            self.IsUNUSED = False
            
    def printContainer(self):
        print(self.location, self.weight, self.description)
