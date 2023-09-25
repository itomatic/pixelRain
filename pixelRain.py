import zlib
import struct

def subFilter(scanLine):
    #write sub filter algorithm later
    return 'ERROR'

def scalePixels(factor, pixStream, bitDepth):
    returnPixels = []
    for scanLine in pixStream:
        tempLine = b''
        print(str(bitDepth/2)+'s')
        indivBytes = struct.iter_unpack(str(int(bitDepth/2))+'s',scanLine)
        for channel in indivBytes:
            for iter in range(0,factor):
                tempLine+=channel[0]
        for iter in range(0,factor):
            returnPixels.append(tempLine)
    return returnPixels

def writeToPNG(name,width,height,pixStream,bitDepthIn):

    #establish parameters of the PNG file
    bitDepth = bitDepthIn #bits per color channel
    colorType = 6 #truecolor with alpha channel ()
    compressMethod = 0 #0 = no
    filterMethod = 0 #0 = no
    interlaceMethod = 0 #0 = not interlaced

    #set up the bytes that will be used to create the PNG image file

    #standard header chunk for PNG signature
    byteHeader = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

    #establish the size of the PNG in pixels
    byteIHDR = width.to_bytes(4)+height.to_bytes(4)
    #convert the parameters established earlier into bytes
    byteIHDR += bitDepth.to_bytes(1)+colorType.to_bytes(1)+compressMethod.to_bytes(1)+filterMethod.to_bytes(1)+interlaceMethod.to_bytes(1)
    #calculate length of chunk data
    IHDRlen = len(byteIHDR)
    #add chunk type
    byteIHDR = 'IHDR'.encode('ascii')+byteIHDR
    #add chunk data length to beginning of IHDR and calculate CRC of chunk type and chunk data using zlib
    byteIHDR = IHDRlen.to_bytes(4)+byteIHDR+zlib.crc32(byteIHDR).to_bytes(4)

    #filter each scan line from the pixel stream
    #Using 0 to signify no filter process for now
    rawIDAT = b''
    for scanLine in pixStream:
        rawIDAT += b'\x00'+scanLine
    #compress the contiguous stream of filtered scanlines
    byteIDAT = zlib.compress(rawIDAT)
    #get length of chunk data
    IDATlen = len(byteIDAT)
    #add chunk type
    byteIDAT = 'IDAT'.encode('ascii')+byteIDAT
    #add chunk data length to beginning of IDAT and calculate CRC of chunk type and chunk data using zlib
    byteIDAT = IDATlen.to_bytes(4)+byteIDAT+zlib.crc32(byteIDAT).to_bytes(4)

    #standard PNG image end chunk
    byteIEND = b'\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82'

    #open/create the PNG file and then write to it
    fileData = open(name+'.png','wb')
    fileData.write(byteHeader+byteIHDR+byteIDAT+byteIEND)
    fileData.close()

def fileWritingTest():

    #hardcoded bytes necessary to creat a PNG image of a single red pixel
    byteHeader = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
    byteIHDR = b'\x00\x00\x00\x0D\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90\x77\x53\xDE'
    byteContent = b'\x00\x00\x00\x0C\x49\x44\x41\x54\x08\xD7\x63\xF8\xCF\xC0\x00\x00\x03\x01\x01\x00\x18\xDD\x8D\xB0'
    byteIEND = b'\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82'

    #testing ability to create file
    f = open('textTest.txt', 'w')
    f.write('Hello my little test')
    f.close()

    #testing ability to make PNG file of single red pixel
    g = open('pixTest.png', 'wb')
    g.write(byteHeader+byteIHDR+byteContent+byteIEND)
    g.close()
    
    # f2 = open('textTest.txt', 'rb')
    # print(f2.read())
    # f2.close()

    # g2 = open('pixTest.png','rb')
    # print(g2.read())
    # g2.close()

def byteColor(pixColor):
    color = pixColor[0].to_bytes(1)
    color += pixColor[1].to_bytes(1)
    color += pixColor[2].to_bytes(1)
    color += pixColor[3].to_bytes(1)
    return color

def createChecker(name,width,height): 

    black = b'\x00\x00\x00\x00\x00\x00\xFF\xFF'
    white = b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
    pixelScale = 10 #establish how much bigger I want each checker to be, growth in X and Y
    channelBitDepth = 16 #set bit depth of each channel for final image

    board = []

    for row in range(height):
        if row%2 == 0:
            currentColor = black
        else:
            currentColor = white
        tempBoardRow = b''
        for pixel in range(width):
            tempBoardRow += currentColor
            currentColor =  bytes(a^b for a, b in zip(currentColor,b'\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00'))
        board.append(tempBoardRow)
    
    board = scalePixels(pixelScale,board,channelBitDepth)
    writeToPNG(name,width*pixelScale,height*pixelScale,board,channelBitDepth)
            
#fileWritingTest()
#writeToPNG('PNGWriteTest',1,1,b'\x00\x00\x00\x0C\x49\x44\x41\x54\x08\xD7\x63\xF8\xCF\xC0\x00\x00\x03\x01\x01\x00\x18\xDD\x8D\xB0')
createChecker('checkerTest',3,3)
#createChecker('bigCheckerTest',35,50)