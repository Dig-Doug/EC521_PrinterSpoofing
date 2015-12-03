class FileUtils:
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
        result += ord(val)
        return result

    def schar(self):
        """Returns a signed char in range [-128, 127]"""
        result = 0
        val = self._file.read(1);
        result += ord(val)
        """compute the 2's compliment of int value val"""
        if (result & (1 << (8 - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            result = result - (1 << 8)
        return result