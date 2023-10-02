import zlib
import struct
import random


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
        #check if the raindrop has ht the ground, and if so move it to a space above the actual image
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

    #filter each scan line from the pixel stream
    #Using 0 to signify no filter process for now
    rawIDAT = b''
    print("-adding filter type to scan lines")
    for scanLine in pixStream:
        rawIDAT+=b'\x00'+scanLine
    #compress the contiguous stream of filtered scanlines
    print("-compressing IDAT data")
    byteIDAT = zlib.compress(rawIDAT)
    #get length of chunk data
    print("-adding IDAT bits")
    IDATlen = len(byteIDAT)
    #add chunk type
    byteIDAT = 'IDAT'.encode('ascii')+byteIDAT
    #add chunk data length to beginning of IDAT and calculate CRC of chunk type and chunk data using zlib
    print("-creating crc for IDAT chunk")
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

def byteColor8(pixColor):
    color = pixColor[0].to_bytes(1)
    color += pixColor[1].to_bytes(1)
    color += pixColor[2].to_bytes(1)
    color += pixColor[3].to_bytes(1)
    return color

def byteColor16(pixColor):
    color = pixColor[0].to_bytes(2)
    color += pixColor[1].to_bytes(2)
    color += pixColor[2].to_bytes(2)
    color += pixColor[3].to_bytes(2)
    return color

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

    #initialize a list of raindrops
    print("Creating raindropList")
    raindropList = [Raindrop(groundRange, groundMax, width, height) for _ in range(numOfDrops)]
    for frame in range(numFrames):
        #create a list of lists that will hold the pixel data initialized with a clear pixel in every spot
        print("Creating rainGrid")
        rainGrid = [[[0,0,0,255] for _ in range(width)] for _ in range(height)]#black pixels for testing
        #use the raindrop list to implement the raindrops into pixels on the rain grid
        print("Changing color of raindrops")
        for drop in raindropList:
            for i in range(raindropLength):
                if drop.currentLoc[0]-i >= 0:
                    rainGrid[drop.currentLoc[0]-i][drop.currentLoc[1]] = [255+(i*-10),255+(i*-10),255+(i*-10),255]
            #step the raindrops forward one step so that on the next frame they are in a new location
            drop.step(raindropSpeed)

        #convert the list of lists into a byte stream that can be used by the PNG writing function
        print("Converting to pixelstream")
        pixStream = []
        for row in rainGrid:
            tempRow =b''
            for pixel in row:
                tempRow+=byteColor8(pixel)
            pixStream.append(tempRow)
        #scale each pixel up so that it is easier to see the rain
        print("Scaling up pixels")
        pixStream = scalePixels(pixelScale,pixStream,channelBitDepth)
        #output the generated image as a PNG
        print("Writing to PNG file")
        writeToPNG(name+str(frame),width*pixelScale,height*pixelScale,pixStream,channelBitDepth)


#fileWritingTest()
#writeToPNG('PNGWriteTest',1,1,b'\x00\x00\x00\x0C\x49\x44\x41\x54\x08\xD7\x63\xF8\xCF\xC0\x00\x00\x03\x01\x01\x00\x18\xDD\x8D\xB0')
#createChecker('checkerTest',3,3)
#createChecker('bigCheckerTest',35,50)
createRain("rainTest",200,200)