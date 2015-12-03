import FileUtils

class PixelUtils:
    """ Reads the file using the specified color parameters and
        returns the color representation in RGB space.
    """

    def __init__(self, aFile, aBitDepth, aColorSpace):
        self.file = aFile
        self.reader = FileUtils.FileUtils(aFile)
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