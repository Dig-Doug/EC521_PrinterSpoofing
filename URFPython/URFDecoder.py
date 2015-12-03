#!/usr/bin/python

import sys
import argparse
import URFDocumentReader

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # setup arg parser
    parser = argparse.ArgumentParser(description='Decode URF files and ouputs them as PNG files.')
    parser.add_argument('-i', action='store', dest='input', help='Input URF file')
    parser.add_argument('-o', action='store', dest='output', help="""Output PNG file. Documents with multiple
                                                pages will be named <name>-<page #>.png""")

    # parse args
    results = parser.parse_args()

    # read document
    reader = URFDocumentReader.URFDocumentReader()
    pages = reader.read(results.input)

    for i in range(0, len(pages)):
        pages[i].saveToPNG(results.output + str(i))

if __name__ == "__main__":
    sys.exit(main())