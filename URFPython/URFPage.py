import PIL
from PIL import Image
import URFPageHeader
import FileUtils
import PixelUtils

class URFPage:
    def __init__(self, aPageHeader, aPageData):
        self.header = aPageHeader
        self.data = aPageData

    def saveToPNG(self, aFilePath):

        im = PIL.Image.new('RGB', (self.header.pageWidth, self.header.pageHeight))
        pix = im.load()
        for y in range(0, self.header.pageHeight):
            for x in range(0, self.header.pageWidth):
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

    @classmethod
    def parsePage(cls, aInputFile):

        header = URFPageHeader.URFPageHeader.parse(aInputFile)

        reader = FileUtils.FileUtils(aInputFile)
        pixels = PixelUtils.PixelUtils(aInputFile, header.bitsPerPixel, header.colorSpace)

        # current line in image
        currentLine = 0
        lines = []
        while currentLine < header.pageHeight:
            # get number of times to repeat line: + 1 because
            # we want to write the line at least once
            lineRepeatCount = reader.char() + 1

            # parse line info
            line = cls._parseLine(header, reader, pixels)

            # write line
            for i in range(0, lineRepeatCount):
                lines.append(line)

            # increment line index
            currentLine += lineRepeatCount

        # create a page from the data
        return URFPage(header, lines)

    @classmethod
    def _parseLine(cls, header, reader, pixels):
        # pixel data for line
        line = []
        # continue until line is filled
        while len(line) < header.pageWidth * 3:
            # get packed bits code
            packBitsCode = reader.schar()

            # 0x80
            if packBitsCode == -128:
                # fill rest of line with fill color
                while len(line) < header.pageWidth * 3:
                    line += pixels.convert(header.fillColor)

            elif packBitsCode >= 0:
                # repeat color n times
                n = (packBitsCode) + 1

                # get the color
                pixel = pixels.pixel()

                # append pixel n + 1 times
                while n > 0:
                    line += pixel
                    n -= 1

            else:
                # copy next |n| + 1 pixels
                n = -(packBitsCode) + 1

                while n > 0:
                    # get the next pixel
                    pixel = pixels.pixel()
                    # add to line
                    line += pixel
                    # decrement n
                    n -= 1

        return line
