import FileUtils
import PixelUtils
import Page

class URFPageReader:
    """ Reads pages of a URF document and saves pages as PNGs.
    """

    def __init__(self, aHeader, aInputFile):
        self.header = aHeader
        self.input = aInputFile
        self.page = 0
        # create readers for simplicity
        self.reader = FileUtils.FileUtils(self.input)
        self.pixels = PixelUtils.PixelUtils(self.input, self.header.bitsPerPixel, self.header.colorSpace)

    def hasNext(self):
        return self.page < self.header.pageCount

    def parseNext(self):
        # check that we haven't read all pages
        if self.hasNext() == False:
            raise Exception()

        # current line in image
        currentLine = 0
        lines = []
        while currentLine < self.header.pageHeight:
            # get number of times to repeat line: + 1 because
            # we want to write the line at least once
            lineRepeatCount = self.reader.char() + 1

            # parse line info
            line = self._parseLine()

            # write line
            for i in range(0, lineRepeatCount):
                lines.append(line)

            #increment line index
            currentLine += lineRepeatCount

        # finished page, increment current
        self.page += 1

        # idk
        test = self.input.read(32);

        # create a page from the data
        return Page.Page(lines)

    def _parseLine(self):
        # pixel data for line
        line = []
        # continue until line is filled
        while len(line) < self.header.pageWidth * 3:
            # get packed bits code
            packBitsCode = self.reader.schar()

            # 0x80
            if packBitsCode == -128:
                # fill rest of line with fill color
                while len(line) < self.header.pageWidth * 3:
                    line += self.pixels.convert(self.header.fillColor)

            elif packBitsCode >= 0:
                # repeat color n times
                n = (packBitsCode) + 1

                # get the color
                pixel = self.pixels.pixel()

                # append pixel n + 1 times
                while n > 0:
                    line += pixel
                    n -= 1

            else:
                # copy next |n| + 1 pixels
                n = -(packBitsCode) + 1

                while n > 0:
                    # get the next pixel
                    pixel = self.pixels.pixel()
                    # add to line
                    line += pixel
                    # decrement n
                    n -= 1

        return line