import database
import json

class Backend:
    def __init__(self):
        self.databaseName = "test1.db"
        self.imagesUrlBase = "http://fmaj7/images/"

    def getImages(self):
        database.connectToDatabase(self.databaseName)
        images = database.getImages()

        curatedImages=[]

        for image in images:
            dictItem = {'src':self.imagesUrlBase+image[1], 
                        'width':image[2], 
                        'height':image[3]}

            curatedImages.append(dictItem)
    
        jsonString = json.dumps(curatedImages, indent=4)
        return jsonString
