import FileUtils

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
            raise Exception()

        # create a reader for simplicity
        reader = FileUtils.FileUtils(aFile)

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