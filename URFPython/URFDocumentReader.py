import png

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


class _FileUtils:
    """ Helper class for getting different primitives out of a file.
    """

    def __init__(self, aFile):
        self._file = aFile

    def int(self):
        """Returns a signed 4 byte int"""
        result = 0
        result += ord(self._file.read(1)) << 24
        result += ord(self._file.read(1)) << 16
        result += ord(self._file.read(1)) << 8
        result += ord(self._file.read(1)) << 0
        return result

    def char(self):
        """Returns a unsigned char in range [0, 255]"""
        result = 0
        val = self._file.read(1);
        if len(val) != 1:
            raise Error()
        result += ord(val)
        return result

    def schar(self):
        """Returns a signed char in range [-128, 127]"""
        result = 0
        val = self._file.read(1);
        if len(val) != 1:
            raise Error()
        result += ord(val)
        """compute the 2's compliment of int value val"""
        if (result & (1 << (8 - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            result = result - (1 << 8)
        return result

class _PixelUtils:
    """ Reads the file using the specified color parameters and
        returns the color representation in RGB space.
    """

    def __init__(self, aFile, aBitDepth, aColorSpace):
        self.file = aFile
        self.reader = _FileUtils(aFile)
        self.depth = aBitDepth
        self.colorSpace = aColorSpace

    def pixel(self):
        # resulting RGB value
        result = ()

        if self.depth == 8:
            value = self.reader.char()
            result = [value, value, value]
        elif self.depth == 24:
            r = self.reader.char()
            g = self.reader.char()
            b = self.reader.char()
            result = (r, g, b)

        return result

    def convert(self, aRGB):
        r = (aRGB & 0x00ff0000) >> 16
        g = (aRGB & 0x0000ff00) >> 8
        b = (aRGB & 0x000000ff) >> 0
        return (r, g, b)

class URFDocumentHeader:
    """ Header of a URF document
    """

    FILE_HEADER = 'UNIRAST'

    def __init__(self, aPageCount, aBitsPerPixel, aColorSpace,
                 aDuplexMode, aPrintQuality, aPageWidth,
                 aPageHeight, aResolution, aFillColor):
        self.pageCount = aPageCount
        self.bitsPerPixel = aBitsPerPixel
        self.colorSpace = aColorSpace
        self.isDuplex = aDuplexMode
        self.quality = aPrintQuality
        self.pageWidth = aPageWidth
        self.pageHeight = aPageHeight
        self.resolution = aResolution
        self.fillColor = aFillColor

    @classmethod
    def parse(cls, aFile):

        # read "UNIRAST" from file
        header = aFile.read(8)

        # check that header is correct
        if header[0:7] != cls.FILE_HEADER:
            raise InputError("Input File", "Invalid file header")

        # create a reader for simplicity
        reader = _FileUtils(aFile)

        # read stuff
        pageCount = reader.int()

        bitsPerPixel = reader.char()
        colorSpace = reader.char()
        duplexMode = reader.char()
        quality = reader.char()

        # unknown data
        aFile.read(8)

        pageWidth = reader.int()
        pageHeight = reader.int()
        resolution = reader.int()

        # unknown data
        aFile.read(8)

        fillColor = 0xffffffff

        return URFDocumentHeader(pageCount, bitsPerPixel, colorSpace,
                                 duplexMode, quality, pageWidth,
                                 pageHeight, resolution, fillColor)

class _URFPageReader:
    """ Reads pages of a URF document and saves pages as PNGs.
    """

    def __init__(self, aHeader, aInputFile, aOutputName):
        self.header = aHeader
        self.input = aInputFile
        self.page = 0
        self.output = aOutputName
        # create readers for simplicity
        self.reader = _FileUtils(self.input)
        self.pixels = _PixelUtils(self.input, self.header.bitsPerPixel, self.header.colorSpace)

    def hasNext(self):
        return self.page < self.header.pageCount

    def parseNext(self):
        # check that we haven't read all pages
        if self.hasNext() == False:
            raise Error()

        # name of output file
        filename = self.output + "-" + str(self.page + 1) + ".png"

        # open file as writable bytewise
        file = open(filename, "wb")

        # create png writer
        writer = png.Writer(self.header.pageWidth, self.header.pageHeight)

        print self.input.tell()

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

        # write lines
        writer.write(file, lines)

        # finished page, increment current
        self.page += 1

        # idk
        test = self.input.read(32);

        # close output file
        file.close()

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

class URFDocumentReader:

    def read(self, aInputFile, aOutputName):

        # open the file as read byte mode & buffered
        # max read per operation is 128ish bytes
        inputFile = open(aInputFile, "rb", 130)

        # parse header
        header = URFDocumentHeader.parse(inputFile)

        # remove the PNG suffix if user added it
        # it will be added later
        outputName = aOutputName
        if outputName.endswith('.png'):
            outputName = outputName[:-4]

        # open page reader
        pageReader = _URFPageReader(header, inputFile, outputName)

        # read all pages
        while pageReader.hasNext():
            pageReader.parseNext()

        # close input file
        inputFile.close()