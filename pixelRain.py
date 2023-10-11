import zlib
import struct
import random
import time


class Raindrop:

    #the raindrop class holds all of the information unique to each individual raindrop
    def __init__(self, groundRange, groundMax, width, height):
        #save inputs to be used in other functions
        self.height = height 
        #create a semi random place where the raindrop will hit the "ground"
        self.ground = random.randrange(groundRange,groundMax)
        #set a random start for the raindrop that is at least above the ground
        self.origin = (random.randrange(0-groundMax, self.ground),random.randrange(width))
        self.currentLoc = [self.origin[0],self.origin[1]]

    def __str__(self):
        return f"({self.currentLoc[1]},{self.currentLoc[0]})"

    def step(self, speed):
        #check if the raindrop has hit the ground, and if so move it to a space above the actual image
        if self.currentLoc[0]>=self.ground:
            self.currentLoc[0] = self.currentLoc[0] - self.height
        else:
            #otherwise, have the raindrop move one step
            self.currentLoc[0] += speed

def subFilter(scanLine):
    #write sub filter algorithm later
    return 'ERROR'

def scalePixels(factor, pixStream, bitDepth):
    #this function iterates through each scanline, then takes each pixel and multiplies it by the scaling factor
    #it then also multiplies each scanline by the scaling factor, saves it to a new pixel stream and returns it
    returnPixels = []
    for scanLine in pixStream:
        tempLine = b''
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

    #split the pixel input stream into multiple IDAT chunks each 100 scanlines large
    fullRawIDAT = b''
    i = 0
    while i < height:
        #filter each scan line for this IDAT chunk
        #Using 0x00 to signify no filter process for now
        rawIDAT = b''
        for scanLine in range(i, i+100):
            if scanLine < height:
                rawIDAT+=b'\x00'+pixStream[scanLine]
        fullRawIDAT = fullRawIDAT+rawIDAT
        i+=100
    #compress the contiguous stream of filtered scanlines
    byteIDAT = zlib.compress(fullRawIDAT)
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

def bytesToColor8(pixColor):
    color = pixColor[0].to_bytes(1)
    color += pixColor[1].to_bytes(1)
    color += pixColor[2].to_bytes(1)
    color += pixColor[3].to_bytes(1)
    return color

def colorToBytes8(pixColor):
    color = pixColor[0].to_bytes(1)
    color += pixColor[1].to_bytes(1)
    color += pixColor[2].to_bytes(1)
    color += pixColor[3].to_bytes(1)
    return color

def colorToBytes16(pixColor):
    color = pixColor[0].to_bytes(2)
    color += pixColor[1].to_bytes(2)
    color += pixColor[2].to_bytes(2)
    color += pixColor[3].to_bytes(2)
    return color

def openBackgroundImage(imgToOpen):

    bgPixStream = []

    try:
        bgFile = open(imgToOpen,'rb')
    except:
        print('Unable to open background image')
    else:

        if bgFile.read(8) == b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A':
            print('verified PNG signature')
        else:
            raise Exception('Not a valid PNG file')
        
        chunkLength = int.from_bytes(bgFile.read(4))
        chunkSignature = bgFile.read(4)
        if chunkSignature == b'IHDR':
            print('verified IHDR signature')
        else:
            raise Exception('Not a valid PNG file')
        
        byteWidth = bgFile.read(4)
        width = int.from_bytes(byteWidth)
        byteHeight =bgFile.read(4)
        height =  int.from_bytes(byteHeight)
        byteBitDepth = bgFile.read(1)
        bitDepth =  int.from_bytes(byteBitDepth)
        byteColorType = bgFile.read(1)
        colorType =  int.from_bytes(byteColorType)
        byteCompressionMethod = bgFile.read(1)
        compressionMethod =  int.from_bytes(byteCompressionMethod)
        byteFilterMethod = bgFile.read(1)
        filterMethod =  int.from_bytes(byteFilterMethod)
        byteInterlaceMethod = bgFile.read(1)
        interlaceMethod =  int.from_bytes(byteInterlaceMethod)

        chunkCRC = bgFile.read(4)
        testCRC = zlib.crc32(chunkSignature+byteWidth+byteHeight+byteBitDepth+byteColorType+byteCompressionMethod+byteFilterMethod+byteInterlaceMethod).to_bytes(4)
        if testCRC == chunkCRC:
            print('verified IHDR CRC')
        else:
            raise Exception('IHDR does not match CRC')
        
        if compressionMethod != 0 or filterMethod != 0 or interlaceMethod != 0:
            print('Unable to process this image file')
        else:
            while True:
                chunkLength = int.from_bytes(bgFile.read(4))
                chunkSignature = bgFile.read(4)
                print(chunkSignature)
                if chunkSignature == b'\x49\x45\x4E\x44':
                    break
                chunkData = bgFile.read(chunkLength)
                chunkCRC = bgFile.read(4)
                testCRC = zlib.crc32(chunkSignature+chunkData).to_bytes(4)
                if testCRC != chunkCRC:
                    print('issue with {} chunk'.format(chunkSignature))
                else:
                    if chunkSignature == 'IDAT'.encode('ascii'):
                        pixelData = zlib.decompress(chunkData)
                        match colorType:
                            case 0:
                                print('unable to process grayscale images')
                            case 2:
                                print('working on true color image')
                            case 3:
                                print('unable to process indexed PNG images')
                            case 4:
                                print('unable to process grayscale images with alpha')
                            case 6:
                                print('working on true color image with alpha')
                            case _:
                                print('unrecognized color type')

                        bgPixStream.append(chunkData)
    finally:
        bgFile.close()

def createChecker(name,width,height): 

    black = b'\x00\x00\x00\x00\x00\x00\xFF\xFF'#black pixel bytewise with an alpha channel
    white = b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'#white pixel bytewise with an alpha channel
    pixelScale = 10 #establish how much bigger I want each checker to be, growth in X and Y
    channelBitDepth = 16 #set bit depth of each channel for final image

    #create the list that will hold all of the rows of the checkerboard
    board = []
    #iterate through each row, then iterate through each square in the row, and alternate between adding a black pixel or a white pixel
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
    
    #scale each pixel up so that it is easier to see the checker pattern
    board = scalePixels(pixelScale,board,channelBitDepth)
    #send the byte stream of the image to the function that actually formats it as a PNG image
    writeToPNG(name,width*pixelScale,height*pixelScale,board,channelBitDepth)
            
def createRain(name,width,height):

    #establish the range within which raindrops can hit the "ground"
    groundRange = height-40
    groundMax = height-20
    #designate how dense the raindrops should be comparitive to the size of the picture ie pixels per raindrop
    rainDensity = 400
    numOfDrops = round((width*height)/rainDensity)
    #designate how many pixels long a rain drop is
    raindropLength = 16
    #designate how fast raindrops fall
    raindropSpeed = 12
    #calculate number of frames to complete the loop
    numFrames = round(height/raindropSpeed)
    #establish how much bigger I want each pixel to be, growth in X and Y
    pixelScale = 5 
    #set bit depth of each channel for final image
    channelBitDepth = 8 
    #establish counters to get total times for processes to calculate averages with
    rainTime = 0.0
    aggregateTime = 0.0

    #initialize a list of raindrops
    raindropList = [Raindrop(groundRange, groundMax, width, height) for _ in range(numOfDrops)]
    for frame in range(numFrames):   

        #print frame number to giver user idea of how long is left to run
        print('Working on frame '+str(frame+1)+'/'+str(numFrames), end='\r')

        #establish timer to see how long it takes to run the rain creation algorithm
        rainStart = time.perf_counter()

        #create a list of lists that will hold the pixel data initialized with a clear pixel in every spot
        rainGrid = [[[0,0,0,255] for _ in range(width)] for _ in range(height)]#black pixels for testing
        #use the raindrop list to implement the raindrops into pixels on the rain grid
        for drop in raindropList:
            for i in range(raindropLength):
                if drop.currentLoc[0]-i >= 0:
                    rainGrid[drop.currentLoc[0]-i][drop.currentLoc[1]] = [255+(i*-10),255+(i*-10),255+(i*-10),255]
            #step the raindrops forward one step so that on the next frame they are in a new location
            drop.step(raindropSpeed)

        #convert the list of lists into a byte stream that can be used by the PNG writing function
        pixStream = []
        for row in rainGrid:
            tempRow =b''
            for pixel in row:
                tempRow+=colorToBytes8(pixel)
            pixStream.append(tempRow)
        
        #add how long the rain algorithm took to calculate average
        rainStop = time.perf_counter()
        rainTime+=rainStop-rainStart

        #scale each pixel up so that it is easier to see the rain
        pixStream = scalePixels(pixelScale,pixStream,channelBitDepth)

        #establish timer to see how long it takes to write to the PNG
        fileWriteStart = time.perf_counter()
        #output the generated image as a PNG
        writeToPNG(name+str(frame),width*pixelScale,height*pixelScale,pixStream,channelBitDepth)
        #add how long the PNG file writing process took to compute average
        fileWriteStop = time.perf_counter()
        aggregateTime = fileWriteStop-fileWriteStart+aggregateTime

    #calculate time averages and print them out
    print('\nRain generation averaged {} seconds per frame'.format(rainTime/numFrames))
    print('File writing averaged {} seconds per frame'.format(aggregateTime/numFrames))

#fileWritingTest()
#writeToPNG('PNGWriteTest',1,1,b'\x00\x00\x00\x0C\x49\x44\x41\x54\x08\xD7\x63\xF8\xCF\xC0\x00\x00\x03\x01\x01\x00\x18\xDD\x8D\xB0')
#createChecker('checkerTest',3,3)
#createChecker('bigCheckerTest',35,50)
#createRain('rainTest',500,500)
testBGFileRead = openBackgroundImage('checkerTest.png')