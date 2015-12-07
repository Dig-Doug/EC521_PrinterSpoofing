#!/usr/bin/env python

import getopt, sys
import pcap
from Packets import PacketReader

def usage():
    print >> sys.stderr, 'usage: %s [-i device] [pattern]' % sys.argv[0]
    sys.exit(1)


foundPacket = False

def get_data(ts, pkt, pc, reader):

    reader.process(pkt)

def main():
    opts, args = getopt.getopt(sys.argv[1:], 'i:h')
    name = "en1"
    for o, a in opts:
        if o == '-i': name = a
        else: usage()

    # starts capturing with pypcap library
    pc = pcap.pcap(name, immediate=True)
    # IPP protocol uses TCP with destination port 631
    # the filter follows libpcap syntax
    filter = 'tcp dst port 631'
    pc.setfilter(filter)
    try:
        print 'listening on %s: %s' % (pc.name, pc.filter)
        # pc.loop is a function that process a packet
        # with a user callback, in this case is get_data
        # get_data looks for the ipp packets that
        # contains document data
        reader = PacketReader.PacketReader(pc, "out/")
        pc.loop(-1, get_data, pc, reader)

    except KeyboardInterrupt:
        nrecv, ndrop, nifdrop = pc.stats()
        print '\n%d packets received by filter' % nrecv
        print '%d packets dropped by kernel' % ndrop
        print '%d packets dropped by interface' % nifdrop

if __name__ == '__main__':
    main()
