import codecs
import os
import game
from hacktools import common, wii


def run():
    infolder = "data/extract/DATA/files/"
    outfolder = "data/repack/DATA/files/"
    infile = "data/msbe_input.txt"
    fontfile = "data/extract/DATA/files/resfont/font_jp.brfnt"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.logMessage("Repacking MSBE from", infile, "...")
    glyphs = wii.getFontGlyphs(fontfile)
    with codecs.open(infile, "r", "utf-8") as msbe:
        files = common.getFiles(infolder + "script/", ".bscr") + common.getFiles(infolder + "text/", ".bin")
        for file in common.showProgress(files):
            subfolder = ("script/" if file.endswith(".bscr") else "text/")
            section = common.getSection(msbe, file)
            if len(section) == 0:
                common.copyFile(infolder + subfolder + file, outfolder + subfolder + file)
                continue
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
                        if newutfstr == "":
                            game.writeUTFString(f, utfstr, -1)
                        else:
                            newutfstr = common.wordwrap(newutfstr, glyphs, 482, None, 26)
                            game.writeUTFString(f, codes + newutfstr, -1)
                            if dataoffsets[i] > 0:
                                pos = f.tell()
                                f.seek(dataoffsets[i])
                                f.writeUShort(len(newutfstr) - newutfstr.count("\n"))
                                f.seek(pos)
        # Separate handling for quest.bin
        with common.Stream(infolder + "quest/quest.bin", "rb") as fin:
            with common.Stream(outfolder + "quest/quest.bin", "wb") as f:
                section = common.getSection(msbe, "quest.bin")
                chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
                f.write(fin.read(game.queststart))
                for i in range(game.questnum):
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
                        newlen = game.writeUTFString(f, codes + newutfstr, strlen)
                        if strlen > newlen:
                            for j in range(strlen - newlen):
                                f.writeByte(0x00)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
