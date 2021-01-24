import codecs
import os
import game
from hacktools import common


def run(speaker=False, merge=False):
    infolder = "data/extract/DATA/files/"
    outfile = "data/msbe_output.txt"
    commonfile = "data/common.txt"

    commonstr = {}
    # Read common strings from another file
    if os.path.isfile(commonfile):
        with codecs.open(commonfile, "r", "utf-8") as commonf:
            commonstr = common.getSection(commonf, "COMMON")
    if merge:
        mergescript = codecs.open("data/msbe_input.txt", "r", "utf-8")

    common.logMessage("Extracting MSBE to", outfile, "...")
    with codecs.open(outfile, "w", "utf-8") as out:
        if len(commonstr) > 0:
            out.write("!FILE:COMMON\n")
            for s in commonstr:
                out.write(s + "=\n")
        files = common.getFiles(infolder + "script/", ".bscr") + common.getFiles(infolder + "text/", ".bin")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            if merge:
                mergesection = common.getSection(mergescript, file)
            with common.Stream(infolder + ("script/" if file.endswith(".bscr") else "text/") + file, "rb", False) as f:
                header = f.readString(4)
                if header == "SCBE":
                    msbeoff = f.readUInt()
                    if msbeoff == 0:
                        continue
                    f.seek(msbeoff)
                elif header == "MSBE":
                    f.seek(0)
                    msbeoff = 0
                else:
                    f.seek(0)
                    common.logError("Unknown header", common.toHex(f.readUInt()))
                header = f.readString(4)
                if header != "MSBE":
                    f.seek(-4, 1)
                    common.logError("Header is", common.toHex(f.readUInt()))
                    continue
                out.write("!FILE:" + file + "\n")
                constant = f.readUInt()
                if constant != 512:
                    common.logError("Constant is", constant)
                strnum = f.readUInt()
                constant = f.readUInt()
                if constant != 0:
                    common.logError("Constant 2 is", constant)
                strings = []
                # String offset
                for i in range(strnum):
                    strings.append([f.readUInt(), 0, ""])
                # Data pointers
                for i in range(strnum):
                    strings[i][1] = f.readUInt()
                # Data
                for i in range(strnum):
                    if strings[i][1] == 0:
                        continue
                    check = f.tell()
                    f.seek(msbeoff + strings[i][1])
                    if check != f.tell():
                        common.logWarning("data diff", check, f.tell(), i)
                    f.seek(2, 1)
                    codelen = f.readUShort()
                    f.seek(-4, 1)
                    for j in range(codelen + 3):
                        strings[i][2] += ":" + common.toHex(f.readByte()) + common.toHex(f.readByte())
                # Read strings
                for i in range(strnum):
                    check = f.tell()
                    f.seek(msbeoff + strings[i][0])
                    if check != f.tell():
                        common.logWarning("str diff", check, f.tell(), i)
                    utfstr, strlen = game.readUTFString(f)
                    utfstr, codes = game.removeStringCode(utfstr)
                    f.seek(1, 1)
                    common.logDebug(strings[i][1], strings[i][2], utfstr)
                    if utfstr not in commonstr:
                        if "%_mk" in codes and speaker:
                            speakerid = codes.split("%_mk[")[1].split("]")[0]
                            out.write(utfstr + "=#" + speakerid + "\n")
                        else:
                            out.write(utfstr + "=")
                            if merge and utfstr in mergesection:
                                out.write(mergesection[utfstr].pop(0))
                                if len(mergesection[utfstr]) == 0:
                                    del mergesection[utfstr]
                            out.write("\n")
        # Separate handling for quest.bin
        with common.Stream(infolder + "quest/quest.bin", "rb") as f:
            out.write("!FILE:quest.bin\n")
            f.seek(game.queststart)
            for i in range(game.questnum):
                utfstr, strlen = game.readUTFString(f)
                utfstr, codes = game.removeStringCode(utfstr)
                out.write(utfstr + "=\n")
                f.seek(1, 1)
    common.logMessage("Done! Extracted", len(files) + 1, "files")
