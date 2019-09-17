queststart = 26420
questnum = 438


def readUTFString(f):
    pos = f.tell()
    strlen = 0
    while True:
        byte = f.readByte()
        if byte == 0:
            break
        else:
            strlen += 1
    f.seek(pos)
    return f.read(strlen).decode("utf-8").replace("\n", "|")


def writeUTFString(f, s):
    f.write(s.replace("|", "\n").encode("utf-8"))
    f.writeByte(0x00)


def removeStringCode(s):
    codes = ""
    while s.startswith("%") and s.find("]") > 0:
        split = s.split("]", 1)
        codes += split[0] + "]"
        s = split[1]
    return s, codes
