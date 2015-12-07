import FileUtils

class URFPageHeader:
    """ Header of a URF page
    """

    def __init__(self, aBitsPerPixel, aColorSpace,
                 aDuplexMode, aPrintQuality, aPageWidth,
                 aPageHeight, aResolution, aFillColor):
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

        # create a reader for simplicity
        reader = FileUtils.FileUtils(aFile)

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

        return URFPageHeader(bitsPerPixel, colorSpace,
                             duplexMode, quality, pageWidth,
                             pageHeight, resolution, fillColor)

    def encode(self, output_file):

        writer = FileUtils.FileUtils(output_file)

        writer.write_char(self.bitsPerPixel)
        writer.write_char(self.colorSpace)
        writer.write_char(self.isDuplex)
        writer.write_char(self.quality)

        writer.write_int(0)
        writer.write_int(0)

        writer.write_int(self.pageWidth)
        writer.write_int(self.pageHeight)
        writer.write_int(self.resolution)

        writer.write_int(0)
        writer.write_int(0)
