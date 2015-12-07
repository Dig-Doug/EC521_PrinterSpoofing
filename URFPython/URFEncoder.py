import FileUtils

class URFEncoder:
    @classmethod
    def encode(cls, pages, output_path):

        output_file = open(output_path, 'wb')

        writer = FileUtils.FileUtils(output_file)

        # write doc header
        output_file.write('UNIRAST')
        writer.write_char(0)

        # write page count
        writer.write_int(len(pages))

        for i in pages:
            i.encode(output_file)

        output_file.close()