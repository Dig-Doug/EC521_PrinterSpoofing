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

    print "Parsing input file..."

    # read document
    reader = URFDocumentReader.URFDocumentReader()
    pages = reader.read(results.input)

    print "Finished parsing input file..."

    prefix = results.output
    if prefix.endswith(".png"):
        prefix = results.output[:-4]

    for i in range(0, len(pages)):
        pages[i].saveToPNG(prefix + "-" + str(i) + ".png")
        # pages[i].saveWithWatermark(results.output + str(i), "/Users/Doug/Desktop/watermark.png")

if __name__ == "__main__":
    sys.exit(main())