###URF File Format

##File Header
The URF file head begins with the ASCII characters "UNIRAST\0". After these 8 bytes, the rest of header contains basic information about the document, such as number of pages, page width & height, etc.

#Example:

Hex Data						# of Bytes		Description
55 4E 49 52 41 53 54 00			8				"UNIRAST"
00 00 00 01 					4				Number of Pages
08 								1				Number of bits per pixel (8 - Greyscale)
00 								1				Color space
01 								1				Duplex (Yes or No)
00 								1				Quality
00 00 00 00 00 00 00 00 		8				Unknown
00 00 09 F6 					4				Page Width
00 00 0C E4 					4				Page Height
00 00 01 2C 					4				Page Resolution
00 00 00 00 00 00 00 00			8				Unknown

						Total:	44
						
##Page Data
The data for each page is compressed using a scheme similar to the PackBits compression algorithm. In this scheme, page data is specified line by line. Each line is decoded using the following algorithm:

pixel[] decodeLine(aFile, aPageWidth)
{
	// Number of times to repeat the following line
	repeatLineCount = aFile.readUnsignedByte();

	// pixel data for line
	pixel[] line ;
	// continue until line is filled
	while (len(line) < aPageWidth)
	{
		// get packed bits code
		packBitsCode = aFile.readSignedByte(); // byte in 2s complement

		if (packBitsCode == -128)
		{
			// fill rest of line with fill color
			while (len(line) < aPageWidth)
				line += WHITE;
		}
		else if (packBitsCode >= 0)
		{
			// read pixel
			pixel = aFile.readPixel();
			// repeat color packBitsCode + 1 times
			n = packBitsCode + 1;
			while (n > 0)
			{
				line += pixel;
				n--
			}
		}
		else
		{
			// copy next |n| + 1 pixels
			n = -(packBitsCode) + 1;

			while (n > 0)
			{
				// get the next pixel
				pixel = aFile.readPixel();
				// add to line
				line += pixel;
				// decrement n
				n -= 1;
			}
		}
	}
	
	return line;
}
	
Once the line has been decoded, you repeat the process for the next line, continuing until you've read all the lines of the page.

#Example:

Hex Data			Type						Description
FF 					Repeat line	count			Repeat following line 0xff = 255 times
80 					mPackbits code				Fill rest of line with white
FF 					Same as previous			...
80 					...							...
46 					Repeat line count			Repeat following line 0x46 times
80 					mPackbits code				Fill rest of line with white
01					Repeat line count			Repeat following line 0x01 times 
7F					mPackbits code				Print following pixel 0x7f + 1 times 
FF					Pixel data					
7F FF				Same as previous			...
7F FF 				...							...
61					mPackbits code				Repeat following line 0x61 + 1 times
FF				 	Pixel data
FB					mPackbits code				Copy the following 6 pixels verbatim
FC D5 C8 67 06 03 	Pixel data
7F 					mPackbits code				Print following pixel 0x7f + 1 times
00 					Pixel data
05 					mPackbits code				Print following pixel 0x05 + 1 times
00 					Pixel data
FD 					mPackbits code
05 25 44 E5 		Pixel data
80 					mPackbits code				Fill rest of line with white
00 					Repeat line	count			Repeat following line 0x0 times
7F FF 				...							...
...
