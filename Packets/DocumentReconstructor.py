class DocumentReconstructor:
    def __init__(self, start_packet, decoded_start_packet):
        self.start_packet = start_packet
        self.decoded_start_packet = decoded_start_packet
        self.tcp_seq = decoded_start_packet.ip.tcp.seq
        self.tcp_data = decoded_start_packet.data.data.data.encode("hex")
        self.packets = [start_packet]
        self.decoded_packets = [decoded_start_packet]
        self.finished = False

    def process(self, orig_packet, decoded_packet):

        # whether or not the packet should be forwarded
        consumed_packet = False

        # get the packet data
        packet_hex = decoded_packet.data.data.data.encode("hex")

        # calculate relative sequence number for packet
        relSeq = decoded_packet.ip.tcp.seq - self.tcp_seq
        if relSeq >= 0:
            # length of tcp data in bytes (2 chars to a byte)
            byteLen = len(self.tcp_data) / 2

            # write hex data to tcp_data
            if relSeq < byteLen:
                # overwrite part of data already received
                startIndex = relSeq * 2
                self.tcp_data = self.tcp_data [:startIndex] + packet_hex + self.tcp_data [startIndex+len(packet_hex):]
            elif relSeq > (len(self.tcp_data) / 2):
                print "HOW DID WE GET HERE?"
                self.tcp_data += (relSeq - byteLen) * "  "
                self.tcp_data += packet_hex
            else:
                # append
                self.tcp_data += packet_hex

            # check if we're at the end of the chunks
            if packet_hex[-10:] == '300d0a0d0a':
                self.finished = True

            # packet is part of document, so consume it
            consumed_packet = True
            self.packets.append(orig_packet)
            self.decoded_packets.append(decoded_packet)

        return consumed_packet