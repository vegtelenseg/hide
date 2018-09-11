from PIL import Image
import binascii
import optparse
import imghdr
import os

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def hex2rgb(hexcode):
    # skip the '#' from the hex code
    return tuple(map(ord, hexcode[1:].decode('hex')))

def str2bin(message):
    binary = bin(int(binascii.hexlify(message), 16))
    # Skip the first two characters because they add a 0b at the front,
    # which we do not really want to be storing
    return binary[2:]

def bin2str(binary):
    # Also add the 0b we stripped off earlier
    message = binascii.unhexlify('%x' % (int('0b' + binary, 2)))
    return message

def encode(hexcode, digit):
    # if last digit of hecode is in range below, then save some data in there
    if hexcode[-1] in ('0', '1', '2', '3', '4', '5'):
        hexcode = hexcode[:-1] + digit
        return hexcode
    else:
        return None

def decode(hexcode):
    if hexcode[-1] in ('0', '1'):
        return hexcode[-1]
    else:
        return None

def hide(fileName, message):
    img = Image.open(fileName)
    if (imghdr.what(fileName) != 'png'):
        # Remove the file extension so can add new one
        newFileName = os.path.splitext(fileName)[0] + '.png'
        img.save(newFileName)
        img.close()
        img = Image.open(newFileName)
    binary = str2bin(message) + '1111111111111110'
    if img.mode in ('RGBA'):
        img = img.convert('RGBA')
        # returns all the pixels in the image
        datas = img.getdata()
        newData = []
        digit = 0
        temp = ''
        # item is each pixel from the image
        for item in datas:
            if (digit < len(binary)):
                newPix = encode(rgb2hex(item[0], item[1], item[2]), binary[digit])
                if (newPix == None):
                    newData.append(item)
                else:
                    r, g, b = hex2rgb(newPix)
                    newData.append((r, g, b, 255))
                    digit += 1
            else:
                newData.append(item)
        img.putdata(newData)
        img.save(fileName, "PNG")
        return "Completed!"
    return "Incorrect Image Mode. Couldn't hide"

def retrieve(fileName):
    img = Image.open(fileName)
    binary = ''
    if img.mode in ('RGBA'):
        img = img.convert('RGBA')
        datas = img.getdata()
        for item in datas:
            digit = decode(rgb2hex(item[0], item[1], item[2]))
            if (digit == None):
                pass
            else:
                binary = binary + digit
                # check to see if we find the delimiter
                if (binary[-16:] == '1111111111111110'):
                    print "Decoded Message:\n"
                    return bin2str(binary[:-16])
        return bin2str(binary)
    return  "Incorrect Image Mode. Couldn't retrieve"

def Main():
    parser = optparse.OptionParser('usage %prog ' +\
    '-e/ -d <target file>')
    parser.add_option('-e', dest='hide', type='string', \
        help='target picture path to hide text')
    parser.add_option('-d', dest='retrieve', type='string', \
    help='target picture path to retrieve text')
    (options, args) = parser.parse_args()
    if (options.hide != None):
        filePath = raw_input("Enter the path to the message you would like to hide: ")
        openedFile = open(filePath, 'r')
        message = openedFile.read()
        print hide(options.hide, message)
    elif (options.retrieve != None):
        print retrieve(options.retrieve)
    else:
        print parser.usage
        exit(0)
if __name__ == '__main__':
    Main()