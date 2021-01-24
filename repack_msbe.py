import codecs
import os
import game
import json
from hacktools import common, wii


def run(onlyquest):
    infolder = "data/extract/DATA/files/"
    outfolder = "data/repack/DATA/files/"
    infile = "data/msbe_input.txt"
    configfile = "data/config.json"
    fontfile = "data/extract/DATA/files/resfont/font_jp.brfnt"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    if not os.path.isfile(configfile):
        common.logError("Config file", configfile, "not found")
        return

    with open(configfile, "r") as f:
        config = json.load(f)

    common.logMessage("Repacking MSBE from", infile, "...")
    glyphs = wii.getFontGlyphs(fontfile)
    with codecs.open(infile, "r", "utf-8") as msbe:
        if not onlyquest:
            commonsection = common.getSection(msbe, "COMMON", justone=False)
            chartot, transtot = common.getSectionPercentage(commonsection)
            files = common.getFiles(infolder + "script/", ".bscr") + common.getFiles(infolder + "text/", ".bin")
            for file in common.showProgress(files):
                subfolder = ("script/" if file.endswith(".bscr") else "text/")
                section = common.getSection(msbe, file)
                chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
                common.logDebug("Processing", file, "...")
                with common.Stream(infolder + subfolder + file, "rb", False) as fin:
                    header = fin.readString(4)
                    if header == "SCBE":
                        msbeoff = fin.readUInt()
                        if msbeoff == 0:
                            common.copyFile(infolder + subfolder + file, outfolder + subfolder + file)
                            continue
                        fin.seek(msbeoff)
                    elif header == "MSBE":
                        fin.seek(0)
                        msbeoff = 0
                    header = fin.readString(4)
                    if header != "MSBE":
                        common.copyFile(infolder + subfolder + file, outfolder + subfolder + file)
                        continue
                    with common.Stream(outfolder + subfolder + file, "wb", False) as f:
                        headerlen = fin.tell() + 4
                        fin.seek(0)
                        f.write(fin.read(headerlen))
                        strnum = fin.readUInt()
                        f.writeUInt(strnum)
                        f.writeUInt(fin.readUInt())  # constant
                        offsets = []
                        firstoff = 0
                        dataoffsets = []
                        # String offset
                        for i in range(strnum):
                            offsets.append(f.tell())
                            offset = fin.readUInt()
                            f.writeUInt(offset)
                            if i == 0:
                                firstoff = offset
                        # Data pointers
                        for i in range(strnum):
                            dataoffset = fin.readUInt()
                            dataoffsets.append(msbeoff + dataoffset)
                            f.writeUInt(dataoffset)
                        # Data
                        f.write(fin.read(msbeoff + firstoff - fin.tell()))
                        # Read strings
                        for i in range(strnum):
                            # Write offset
                            pos = f.tell()
                            f.seek(offsets[i])
                            f.writeUInt(pos - msbeoff)
                            f.seek(pos)
                            # Read string and re-apply codes before writing
                            utfstr, strlen = game.readUTFString(fin)
                            fin.seek(1, 1)
                            utfstripped, codes = game.removeStringCode(utfstr)
                            newutfstr = ""
                            if utfstripped in section:
                                newutfstr = section[utfstripped].pop(0)
                                if len(section[utfstripped]) == 0:
                                    del section[utfstripped]
                                if newutfstr == "!":
                                    newutfstr = " "
                            elif utfstripped in commonsection:
                                newutfstr = commonsection[utfstripped][0]
                            if newutfstr == "":
                                game.writeUTFString(f, utfstr, -1)
                            else:
                                newutfstr = common.wordwrap(newutfstr, glyphs, config["wordwrap_text"], game.detectTextCode, 26, strip=False)
                                game.writeUTFString(f, codes + newutfstr, -1)
                                if dataoffsets[i] > 0:
                                    pos = f.tell()
                                    f.seek(dataoffsets[i])
                                    f.writeUShort(len(newutfstr) - newutfstr.count("\n"))
                                    f.seek(pos)
        # Separate handling for quest.bin
        with common.Stream(infolder + "quest/quest.bin", "rb", False) as fin:
            with common.Stream(outfolder + "quest/quest.bin", "wb", False) as f:
                section = common.getSection(msbe, "quest.bin")
                chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
                # Get the pointers
                pointers = {}
                for i in range(game.questnum // 3):
                    fin.seek(0x5b4 + 0xac * i)
                    for j in range(3):
                        pos = fin.tell()
                        ptr = fin.readUInt()
                        pointers[ptr] = pos
                        fin.seek(4, 1)
                # Read the strings
                fin.seek(0)
                f.write(fin.read(game.queststart))
                j = 1
                for i in range(game.questnum):
                    inpos = fin.tell()
                    outpos = f.tell()
                    utfstr, strlen = game.readUTFString(fin)
                    fin.seek(1, 1)
                    utfstripped, codes = game.removeStringCode(utfstr)
                    newutfstr = ""
                    if utfstripped in section:
                        newutfstr = section[utfstripped].pop(0)
                        if len(section[utfstripped]) == 0:
                            del section[utfstripped]
                        if newutfstr == "!":
                            newutfstr = " "
                    if newutfstr == "":
                        game.writeUTFString(f, utfstr, -1)
                    else:
                        newutfstr = common.wordwrap(newutfstr, glyphs, config["wordwrap_quest" + str(j)], game.detectTextCode, 26, strip=False)
                        game.writeUTFString(f, codes + newutfstr, -1)
                    j += 1
                    if j > 3:
                        j = 1
                    endpos = f.tell()
                    if inpos in pointers:
                        f.seek(pointers[inpos])
                        f.writeUInt(outpos)
                        f.seek(endpos)
                    else:
                        common.logError("Pointer", common.toHex(inpos), "not found.")
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
