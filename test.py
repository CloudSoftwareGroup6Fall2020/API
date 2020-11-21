image_path = 'C:\\Users\\matti\\Pictures\\booty.jpg' # **get from user via post**

def escape(str1):
    global newStr
    for character in str1:
        if (character == ':'):
            split = str1.split(':')
            newStr = split[0] + '&#58;' + split[1]
            escape(newStr)
            break
        if (character == '\\'):
            split = str1.split('\\')
            index = 0
            temp = ''
            for slash in split:
                if (index == len(split)):
                    continue
                if (index > 0):
                    temp += '&#92;' + split[index]
                    index += 1
                else:
                    temp += split[index] + '&#92;' + split[index + 1]
                    index += 2
            newStr = temp
            escape(newStr)
            break
        if (character == '.'):
            split = str1.split('.')
            newStr = split[0] + '&#46;' + split[1]
            return newStr
escape(image_path)

print (newStr)