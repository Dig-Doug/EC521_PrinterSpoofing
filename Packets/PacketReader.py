import dpkt
import pcap
import gzip
import DocumentReconstructor
from URFPython import URFDocumentReader
from URFPython import URFEncoder

class PacketReader:

    def __init__(self, pc, out_dir):

        self.pc = pc
        self.decode = { pcap.DLT_LOOP:dpkt.loopback.Loopback,
               pcap.DLT_NULL:dpkt.loopback.Loopback,
               pcap.DLT_EN10MB:dpkt.ethernet.Ethernet }[pc.datalink()]
        self.window = []
        self.window_size = 5
        self.readingDocPackets = False
        self.document_rec = None
        self.file_count = 0
        self.output_dir = out_dir

    def process(self, pkt):

        decodedPkt = self.decode(pkt)

        # decode packet data to hex
        packet_hex = decodedPkt.data.data.data.encode("hex")

        if self.readingDocPackets == False:
            # check for operation id 0x6 if packet is big enought to have it
            if len(packet_hex) > 16 and int(packet_hex[8:16], 16) == 6:
                print "Found it!"

                # reading doc packets
                self.readingDocPackets = True

                # find the closest POST packet
                closest = None
                closestLen = 999999999999
                for i in self.window:
                    data = i[1].data.data.data.encode("hex")
                    if len(data) >= 8 and data[0:8] == "504f5354":  # "504f5354" == POST in hex
                        if decodedPkt.ip.tcp.seq - i[1].ip.tcp.seq < closestLen:
                            closest = i
                            closestLen = decodedPkt.ip.tcp.seq - closest[1].ip.tcp.seq

                print "Header packet: " + closest[1].data.data.data.encode("hex")

                # create a document reconstructor
                self.document_rec = DocumentReconstructor.DocumentReconstructor(closest[0], closest[1])

                # process all packets in the window
                for i in self.window:
                    # don't process the closest packet twice
                    if i != closest and self.document_rec.process(i[0], i[1]) == False:
                        # TODO forward packet
                        print "sent"
                self.window = []
            else:
                # add the packet to the window
                self.window.append((pkt, decodedPkt))
                # check window size
                if len(self.window) > self.window_size:
                    # TODO forward packet
                    del self.window[0]

        else:
            if self.document_rec.process(pkt, decodedPkt) == False:
                # TODO forward packet
                print "sent"
            elif self.document_rec.finished == True:
                print "Done!"
                self.process_packet_data(self.document_rec.tcp_data)
                self.readingDocPackets = False
                self.document_rec = None


    def process_packet_data(self, packet_data):

        # total = ""
        # baseSequence = ippPackets[1].ip.tcp.seq
        # for pkt in ippPackets[1:]:
        #     relSeq = pkt.ip.tcp.seq - baseSequence
        #     packetHex = pkt.data.data.data.encode("hex")
        #     # check tcp seq
        #     if (len(total) / 2) > relSeq:
        #         packetHex = packetHex[((len(total) / 2) - relSeq) * 2:]
        #     total += packetHex

        # process the header
        line_count = 0
        chunk_start = packet_data.find("4578706563743a203130302d636f6e74696e75650d0a0d0a") + 48
        chunks_data = packet_data[chunk_start:]

        # process chunks
        index = 0
        lastIndex = 0
        chunks = []
        while index < len(chunks_data) - 4:
            if chunks_data[index:index+4] == "0d0a":
                portion = chunks_data[lastIndex:index]
                lastIndex = index + 4
                if len(portion) > 0:
                    hexSize = portion.decode("hex")
                    size = int(hexSize, 16)
                    size *= 2 # size is in octets, which are 2 chars each in string
                    chunkData = chunks_data[lastIndex:lastIndex + size]
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
        filename_gzip = self.output_dir + "file" + str(self.file_count) + ".urf.gzip"
        filename_ungzip = self.output_dir + "file" + str(self.file_count) + ".urf"
        filename_orig = self.output_dir + "file" + str(self.file_count) + ".png"

        print "Writing zipped"

        file = open(filename_gzip, "wb")
        for chunk in docChunks:
            file.write(chunk.decode("hex"))
        file.close()

        print "Unzipping"

        # unzip file
        zipped = gzip.open(filename_gzip,'rb')
        file_content = zipped.read()
        file = open(filename_ungzip, "wb")
        file.write(file_content)
        file.close()

        print "Parsing"

        # parse document
        reader = URFDocumentReader.URFDocumentReader()
        pages = reader.read(filename_ungzip)

        print "Saving"

        # sanitize filename
        prefix = filename_orig
        if prefix.endswith(".png"):
            prefix = filename_orig[:-4]

        # save pages to file
        for i in range(0, len(pages)):
            pages[i].saveToPNG(prefix + "-pg" + str(i) + ".png")
            pages[i].saveWithWatermark(prefix + "-pg" + str(i) + "-edited" + ".png", "watermark.png")

        # increment file count
        self.file_count += 1

        print "Done with: " + str(self.file_count - 1)