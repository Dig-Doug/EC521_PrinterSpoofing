#!/usr/bin/env python

import dpkt, pcap
import gzip
from URFPython import URFDocumentReader
from Packets import DocumentReconstructor

#def replace_between(text, begin, end, alternative=''):
#    middle = text.split(begin, 1)[1].split(end, 1)[0]
#        return text.replace(middle, alternative)

fileCount = 0
OUTPUT_DIR = "out/"

def processPackets(ippPackets):
    total = ""
    baseSequence = ippPackets[1].ip.tcp.seq
    for pkt in ippPackets[1:]:
        relSeq = pkt.ip.tcp.seq - baseSequence
        packetHex = pkt.data.data.data.encode("hex")
        # check tcp seq
        if (len(total) / 2) > relSeq:
            packetHex = packetHex[((len(total) / 2) - relSeq) * 2:]
        total += packetHex

    # process chunks
    index = 0
    lastIndex = 0
    chunks = []
    while index < len(total) - 4:
        if total[index:index+4] == "0d0a":
            portion = total[lastIndex:index]
            lastIndex = index + 4
            if len(portion) > 0:
                hexSize = portion.decode("hex")
                size = int(hexSize, 16)
                size *= 2 # size is in octets, which are 2 chars each in string
                chunkData = total[lastIndex:lastIndex + size]
                lastIndex = lastIndex + size
                chunks.append(chunkData)

            index = lastIndex
        else:
            index += 1

    # first chunk is part of header
    headerChunk = chunks[0]
    # rest of chunks are document chunks
    docChunks = chunks[1:]

    # write chunks to file
    global fileCount
    filenameGZIP = OUTPUT_DIR + "file" + str(fileCount) + ".urf.gzip"
    filenameUNGZIP = OUTPUT_DIR + "file" + str(fileCount) + ".urf"
    filenameORIG = OUTPUT_DIR + "file" + str(fileCount) + ".png"

    print "Writing zipped"

    file = open(filenameGZIP, "wb")
    for chunk in docChunks:
        file.write(chunk.decode("hex"))
    file.close()

    print "Unzipping"

    # unzip file
    zipped = gzip.open(filenameGZIP,'rb')
    file_content = zipped.read()
    file = open(filenameUNGZIP, "wb")
    file.write(file_content)
    file.close()

    print "Parsing"

    # parse document
    reader = URFDocumentReader.URFDocumentReader()
    pages = reader.read(filenameUNGZIP)

    print "Saving"

    # sanitize filename
    prefix = filenameORIG
    if prefix.endswith(".png"):
        prefix = filenameORIG[:-4]

    # save pages to file
    for i in range(0, len(pages)):
        pages[i].saveToPNG(prefix + "-pg" + str(i) + ".png")
        pages[i].saveWithWatermark(prefix + "-pg" + str(i) + "-edited" + ".png", "watermark.png")

    # increment file count
    fileCount += 1

    print "Done"

def main():
    name = "printer6.pcapng"
    pc = pcap.pcap(name)
    # IPP protocol typically use destination port 631
    filter = 'tcp dst port 631'
    pc.setfilter(filter)
    decode = { pcap.DLT_LOOP:dpkt.loopback.Loopback,
               pcap.DLT_NULL:dpkt.loopback.Loopback,
               pcap.DLT_EN10MB:dpkt.ethernet.Ethernet }[pc.datalink()]
    try:
        window = []
        window_size = 2
        readingDocPackets = False
        doc_seq = 0
        doc_data = ""
        document_rec = None
        for ts, pkt in pc:
            decodedPkt = decode(pkt)

            packetHex = decodedPkt.data.data.data.encode("hex")

            if readingDocPackets == False:
                # check for operation id 0x6 if packet is big enought to have it
                if len(packetHex) > 16 and int(packetHex[8:16], 16) == 6:
                    print "Found it!"

                    # reading doc packets
                    readingDocPackets = True

                    # find the closest POST packet
                    closest = window[0]
                    for i in window:
                        if i[1].data.data.data.encode("hex")[0:8] == "504f5354": # "504f5354" == POST in hex
                            if decodedPkt.ip.tcp.seq - i[1].ip.tcp.seq < decodedPkt.ip.tcp.seq - closest[1].ip.tcp.seq:
                                closest = i

                    # create a document reconstructor
                    document_rec = DocumentReconstructor.DocumentReconstructor(closest[0], closest[1])

                    # process all packets in the window
                    for i in window:
                        # don't process the closest packet twice
                        if i != closest and document_rec.process(i[0], i[1]) == False:
                            # TODO forward packet
                            print "sent"
                    window = []
                else:
                    # add the packet to the window
                    window.append((pkt, decodedPkt))
                    # check window size
                    if len(window) > window_size:
                        # TODO forward packet
                        del window[0]

            else:
                if document_rec.process(pkt, decodedPkt) == False:
                    # TODO forward packet
                    print "sent"
                elif document_rec.finished == True:
                    print "Done!"
                    readingDocPackets = False

    except KeyboardInterrupt:
        print 'Stopped'

    print "Done"



if __name__ == '__main__':
    main()
