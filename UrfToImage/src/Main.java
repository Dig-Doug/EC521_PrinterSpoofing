import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import javax.imageio.ImageIO;

public class Main
{
	public static void main(final String[] args)
	{
		try
		{
			Path path = Paths.get("/Users/Doug/Desktop/test2.urf");
			byte[] data = Files.readAllBytes(path);
			
			//read the header
			int index = 0;
			for (int i = 0; i < 8; i++, index++)
				System.out.print((char)data[i]);
			System.out.println();
			
			int pages = getInt(data, index); index += 4;
			System.out.println("Pages: " + pages);
			
			int bitsPerPixel = data[index]; index++;
			System.out.println("Bits per pixel: " + bitsPerPixel);
			
			int colorSpace = data[index]; index++;
			System.out.println("Color space: " + colorSpace);
			
			int duplexMode = data[index]; index++;
			System.out.println("Duplex: " + duplexMode);
			
			int printQuality = data[index]; index++;
			System.out.println("Quality: " + printQuality);
			
			//idk
			index += 8;
			
			int pageWidth = getInt(data, index); index += 4;
			int pageHeight = getInt(data, index); index += 4;
			int resolution = getInt(data, index); index += 4;
			
			System.out.println("Width: " + pageWidth + " height: " + pageHeight + " res: " + resolution);
			
			//idk
			index += 8;
			
			//raster data
			BufferedImage img = new BufferedImage(pageWidth, pageHeight, BufferedImage.TYPE_INT_ARGB);
			int x = 0;
			int y = 0;
			while (index < data.length)
			{
				byte lineRepeatCode = data[index]; index++;
				byte packBitsCode = data[index]; index++;
				
				if (packBitsCode == -128)
				{
					//FillRestOfLineWithFillByte();
					while (x < pageWidth)
					{
						img.setRGB(x, y, toColor(lineRepeatCode));
						x++;
					}
					
					if (x >= pageWidth)
					{
						y++;
						x = 0;
					}
				}
				else if (packBitsCode >= 0)
				{
					// copy single pixel and repeat it n+1 times
					int n = (packBitsCode) + 1;
					while (n >= 0)
					{
						img.setRGB(x, y, toColor(lineRepeatCode));
						x++;
						if (x >= pageWidth)
						{
							y++;
							x = 0;
						}
						n--;
					}
					/*
					 * int n = ((int)code)+1;
					uint8_t pixel[pixel_size];
					ReadData(&pixel, pixel_size);
					while ( n-- > 0 )
					{
						AddPixelToLine( pixel );
					}
					 */
				}
				else
				{
					int n = -(packBitsCode) + 1;
					while (n >= 0)
					{
						img.setRGB(x, y, toColor(lineRepeatCode));
						lineRepeatCode = data[index]; index++;
						x++;
						n--;
						if (x >= pageWidth)
						{
							y++;
							x = 0;
						}
						
						/*
						 // copy the following (-n)+1 pixels verbatim
							int n = (-(int)code)+1;
							ReadData(linePtr, n * pixel_size);
						 */
					}
				}
				
				System.out.println("x: " + x + " y: " + y + " index: " + index);
			}
			
		    File outputfile = new File("/Users/Doug/Desktop/test.png");
		    ImageIO.write(img, "png", outputfile);
		    
		    System.out.println("Done");
		}
		catch (Exception e)
		{
			
		}
	}
	
	private static int getInt(byte[] aData, int aIndex)
	{
		int val = unsignedToBytes(aData[aIndex]) << 24; aIndex++;
		val += unsignedToBytes(aData[aIndex]) << 16; aIndex++;
		val += unsignedToBytes(aData[aIndex]) << 8; aIndex++;
		val += unsignedToBytes(aData[aIndex]); aIndex++;
		return val;
	}
	
	  public static int unsignedToBytes(byte b)
	  {
		   return b & 0xFF;
	  }
	  
	  public static int toColor(byte aByte)
	  {
		  int clr = unsignedToBytes(aByte);
		  int color = 255 << 24;
		  color += clr << 16;
		  color += clr << 8;
		  color += clr;
		  return color;
	  }
	
	/*
	 * 
554e 4952 4153 5400     = "UNIRAST\0"
0000 0011               = 17 pages

// page header (32 bytes)
0:  18                  = bits per pixel
1:  01                  = color space
2:  00                  = duplex mode
3:  04                  = print quality
4:  0000 0001
8:  0000 0000
C:  0000 13ec           = 5100 = page width
10: 0000 19c8           = 6600 = page height
14: 0000 0258           = 600 = resolution
18: 0000 0000
1C: 0000 0000

// raster data
20: ff                  = line repeat code -- how many times this line repeats. Unsigned byte.
21: 80                  = PackBits code (see below)
22: 9b                  = line repeat code
23: 80                  = PackBits code
24: 01					= line repeat code

etc...

UNIRAST PackBits Algorithm:
===========================

This is sort of an inverted version of the TIFF PackBits algorithm.
Code is a signed byte, with three interpretations:

switch ( code )
{
	case -128:	// 0x80
		FillRestOfLineWithFillByte();
		break;
		
	case 0..127:	// copy single pixel and repeat it n+1 times
		int n = ((int)code)+1;
		uint8_t pixel[pixel_size];
		ReadData(&pixel, pixel_size);
		while ( n-- > 0 )
		{
			AddPixelToLine( pixel );
		}
		break;
		
	case -128..-1:	// copy the following (-n)+1 pixels verbatim
		int n = (-(int)code)+1;
		ReadData(linePtr, n * pixel_size);
		break;
}

In TIFF, the 0x80 byte is a NOP used for padding, and the -128..-1 and 0..127 cases are the other way around. I saw some weird results when I tried that...

	 */
	
}
