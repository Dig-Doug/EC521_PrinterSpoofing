import PIL
from PIL import Image

class Page:
    def __init__(self, aPageData):
        self.width = len(aPageData[0]) / 3
        self.height = len(aPageData)
        self.data = aPageData

    def saveToPNG(self, aFilePath):

        im = PIL.Image.new('RGB', (self.width, self.height))
        pix = im.load()
        for y in range(0, self.height):
            for x in range(0, self.width):
                pix[x, y] = (self.data[y][x*3], self.data[y][x*3 + 1], self.data[y][x*3 + 2])

        im.save(aFilePath, "PNG")

    def saveWithWatermark(self, aFilePath, aWatermarkFile):

        # save data
        self.saveToPNG(aFilePath)

        orig = PIL.Image.open(aFilePath)
        water = PIL.Image.open(aWatermarkFile)

        orig = orig.convert("RGBA")
        water = water.convert("RGBA")

        new_img = PIL.Image.blend(orig, water, 0.5)
        new_img.save(aFilePath,"PNG")
