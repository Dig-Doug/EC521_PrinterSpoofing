import URFDocumentHeader
import URFPageReader

class URFDocumentReader:
    def read(self, aInputFile):

        # open the file as read byte mode & buffered
        # max read per operation is 128ish bytes
        inputFile = open(aInputFile, "rb", 130)

        # parse header
        header = URFDocumentHeader.URFDocumentHeader.parse(inputFile)

        # open page reader
        pageReader = URFPageReader.URFPageReader(header, inputFile)

        # read all pages
        pages = []
        while pageReader.hasNext():
            pages.append(pageReader.parseNext())

        # close input file
        inputFile.close()

        return pages
