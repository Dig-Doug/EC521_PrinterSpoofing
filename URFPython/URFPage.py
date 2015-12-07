import PIL
from PIL import Image
import URFPageHeader
import FileUtils
import PixelUtils

class URFPage:
    def __init__(self, aPageHeader, aImage):
        self.header = aPageHeader
        self.image = aImage

    def saveToPNG(self, aFilePath):

        self.image.save(aFilePath, "PNG")

    def saveWithWatermark(self, aFilePath, aWatermarkFile):

        water = PIL.Image.open(aWatermarkFile)

        orig = self.image.convert("RGBA")
        water = water.convert("RGBA")

        new_img = PIL.Image.blend(orig, water, 0.5)
        new_img.save(aFilePath,"PNG")

    def encode(self, output_file):

        self.header.encode(output_file)

        writer = FileUtils.FileUtils(output_file)
        pix = self.image.load()
        for y in range(0, self.header.pageHeight):
            x = 0
            while x < self.header.pageWidth:
                left = self.header.pageWidth - x
                step = 128
                if left < 128:
                    step = left

                writer.write_schar(-(step - 1))

                while step > 0:
                    writer.write_char(pix[x,y][0])
                    writer.write_char(pix[x,y][1])
                    writer.write_char(pix[x,y][2])
                    x += 1
                    step -= 1


    @classmethod
    def parsePage(cls, aInputFile):

        header = URFPageHeader.URFPageHeader.parse(aInputFile)

        reader = FileUtils.FileUtils(aInputFile)
        pixels = PixelUtils.PixelUtils(aInputFile, header.bitsPerPixel, header.colorSpace)

        # current line in image
        im = PIL.Image.new('RGB', (header.pageWidth, header.pageHeight))
        pix = im.load()
        currentLine = 0
        while currentLine < header.pageHeight:
            # get number of times to repeat line: + 1 because
            # we want to write the line at least once
            lineRepeatCount = reader.char() + 1

            # parse line info
            line = cls._parseLine(header, reader, pixels)

            # write line
            for i in range(0, lineRepeatCount):
                for x in range(0, len(line) / 3):
                    pix[x, currentLine] = (line[x*3], line[x*3 + 1], line[x*3 + 2])
                # increment line index
                currentLine += 1

        # create a page from the data
        return URFPage(header, im)

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
