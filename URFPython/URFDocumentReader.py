import URFPage
import FileUtils

class URFDocumentReader:
    FILE_HEADER = 'UNIRAST'

    def read(self, aInputFile):

        # open the file as read byte mode & buffered
        # max read per operation is 128ish bytes
        inputFile = open(aInputFile, "rb", 130)

        # create a reader for simplicity
        reader = FileUtils.FileUtils(inputFile)

        # read "UNIRAST" from file
        header = inputFile.read(8)

        # check that header is correct
        if header[0:7] != self.FILE_HEADER:
            raise Exception()

        # read # of pages in doc
        pageCount = reader.int()

        # read all pages
        pages = []
        while len(pages) < pageCount:
            pages.append(URFPage.URFPage.parsePage(inputFile))

        # close input file
        inputFile.close()

        return pages
