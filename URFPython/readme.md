#URF File Format
A URF file consists of 3 parts: the file header, the page header, and the page data. Each page has its own page header, so the structure of the file is as follows: File Header, Page Header, Page Data, Page Header, Page Data, etc...

##File Header
The URF file header consists of two parts. The first part is the ASCII characters "UNIRAST\0". The second part is the number of pages in the file, represented as an int (4 bytes).

###Example:

```
Hex Data						# of Bytes		Description
55 4E 49 52 41 53 54 00			8				"UNIRAST"
00 00 00 01 					4				Number of Pages
```

##Page Header
The data for each page starts with the page header. The page header contains information about the document, such as number of pages, page width & height, etc.

###Example:
```
Hex Data						# of Bytes		Description
08 								1				Number of bits per pixel (8 - Greyscale)
00 								1				Color space
01 								1				Duplex (Yes or No)
00 								1				Quality
00 00 00 00 00 00 00 00 		8				Unknown
00 00 09 F6 					4				Page Width
00 00 0C E4 					4				Page Height
00 00 01 2C 					4				Page Resolution
00 00 00 00 00 00 00 00			8				Unknown

						Total:	32
```
						
##Page Data
The data for each page is compressed using a scheme similar to the PackBits compression algorithm. In this scheme, page data is specified line by line. Each line is decoded using the following algorithm:

````java
int[] decodeLine(File aFile, int aPageWidth)
{
	// Number of times to repeat the following line
	repeatLineCount = aFile.readUnsignedByte();

	// pixel data for line
	int[] line = new int[aPageWidth];
	// index into line
	int x = 0;
	// continue until line is filled
	while (x < aPageWidth)
	{
		// get packed bits code
		packBitsCode = aFile.readSignedByte(); // byte in 2s complement

		if (packBitsCode == -128)
		{
			// fill rest of line with fill color
			while (x < aPageWidth)
			{
				line[x] = WHITE;
				x++;
			}
		}
		else if (packBitsCode >= 0)
		{
			// read pixel
			pixel = aFile.readPixel();
			// repeat color packBitsCode + 1 times
			n = packBitsCode + 1;
			while (n > 0)
			{
				line[x] = pixel;
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
				line[x] = pixel;
				// decrement n
				n -= 1;
			}
		}
	}
	
	return line;
}
````
	
Once the line has been decoded, you repeat the process for the next line, continuing until you've read all the lines of the page.

###Example:

```
Hex Data			Type						Description
FF 					Repeat line	count			Repeat following line 0xff = 255 times
80 					Packbits code				Fill rest of line with white
FF 					Same as previous			...
80 					...							...
46 					Repeat line count			Repeat following line 0x46 times
80 					Packbits code				Fill rest of line with white
01					Repeat line count			Repeat following line 0x01 times 
7F					Packbits code				Print following pixel 0x7f + 1 times 
FF					Pixel data					
7F FF				Same as previous			...
7F FF 				...							...
61					Packbits code				Repeat following line 0x61 + 1 times
FF				 	Pixel data
FB					Packbits code				Copy the following 6 pixels verbatim
FC D5 C8 67 06 03 	Pixel data
7F 					Packbits code				Print following pixel 0x7f + 1 times
00 					Pixel data
05 					Packbits code				Print following pixel 0x05 + 1 times
00 					Pixel data
FD 					Packbits code
05 25 44 E5 		Pixel data
80 					Packbits code				Fill rest of line with white
00 					Repeat line	count			Repeat following line 0x0 times
7F FF 				...							...
...
```

*Example data is taken from the black8.urf file*
