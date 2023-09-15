def writeToPNG(name,height,width,pixStream):
    fileData = open("pixelRain.png","wb")
    fileData.write()
    fileData.close()

def fileWritingTest():

    byteHeader = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
    
    byteIHDR = b'\x00\x00\x00\x0D\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90\x77\x53\xDE'

    byteContent = b'\x00\x00\x00\x0C\x49\x44\x41\x54\x08\xD7\x63\xF8\xCF\xC0\x00\x00\x03\x01\x01\x00\x18\xDD\x8D\xB0'

    byteIEND = b'\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82'

    # \x\x\x\x\'
    print(byteContent)

    f = open("textTest.txt", "w")
    f.write("Hello my little test")
    f.close()

    g = open("pixTest.png", "wb")
    g.write(byteHeader+byteIHDR+byteContent+byteIEND)
    g.close()
    
    # f2 = open("textTest.txt", "rb")
    # print(f2.read())
    # f2.close()

    g2 = open("pixTest.png","rb")
    print(g2.read())
    g2.close()

fileWritingTest()