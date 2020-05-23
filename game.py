from hacktools import common

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
    return f.read(strlen).decode("utf-8").replace("\n", "|").replace("\r", ""), strlen


def writeUTFString(f, s, maxlen):
    encoded = s.replace("|", "\n").encode("utf-8")
    if maxlen != -1 and len(encoded) > maxlen:
        common.logError("String", s, "is too long.")
        encoded = encoded[:maxlen]
    f.write(encoded)
    f.writeByte(0x00)
    return len(encoded)


def removeStringCode(s):
    codes = ""
    while s.startswith("%") and s.find("]") > 0 and not s.startswith("%_d["):
        if s.startswith("%_tr") or s.startswith("%_te"):
            split = [s[:4], s[4:]]
        else:
            split = s.split("]", 1)
            split[0] += "]"
        codes += split[0]
        s = split[1]
    return s, codes
