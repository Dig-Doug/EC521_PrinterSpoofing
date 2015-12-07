#!/usr/bin/env python

import pcap
from Packets import PacketReader

from URFPython import URFDocumentReader

def main():
    name = "printer6.pcapng"
    pc = pcap.pcap(name)
    # IPP protocol typically use destination port 631
    filter = 'tcp dst port 631'
    pc.setfilter(filter)

    try:
        reader = PacketReader.PacketReader(pc, "out/")
        for ts, pkt in pc:
            reader.process(pkt)


    except KeyboardInterrupt:
        print 'Stopped'

    print "Done"



if __name__ == '__main__':
    main()
