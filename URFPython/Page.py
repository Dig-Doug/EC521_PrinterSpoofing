import png

class Page:
    def __init__(self, aPageData):
        self.width = len(aPageData[0]) / 3
        self.height = len(aPageData)
        self.data = aPageData

    def saveToPNG(self, aFilePath):
               # open file as writable bytewise
        file = open(aFilePath, "wb")

        # create png writer
        writer = png.Writer(self.width, self.height)

        # write lines
        writer.write(file, self.data)

        # close file
        file.close()