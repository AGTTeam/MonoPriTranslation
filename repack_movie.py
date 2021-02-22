import codecs
import os
import game
from hacktools import common, wii


def run():
    infolder = "data/extract/DATA/files/movie/"
    outfolder = "data/repack/DATA/files/movie/"
    fontfile = "data/repack/DATA/files/resfont/font_jp.brfnt"
    infile = "data/movie_input.txt"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.logMessage("Repacking MOVIE from", infile, "...")
    glyphs = wii.getFontGlyphs(fontfile)
    with codecs.open(infile, "r", "utf-8") as movie:
        files = common.getFiles(infolder, ".bin")
        for file in common.showProgress(files):
            section = common.getSection(movie, file)
            if len(section) == 0:
                common.copyFile(infolder + file, outfolder + file)
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            common.logDebug("Processing", file, "...")
            with common.Stream(infolder + file, "rb", False) as fin:
                if file == "movie1001.bin":
                    # The credits subtitles are empty, so write them as new
                    with common.Stream(outfolder + file, "wb", False) as f:
                        f.writeUInt(len(section))
                        f.writeUInt(0)
                        for i in range(len(section)):
                            f.writeUInt(0)
                            f.writeUInt(0)
                            f.writeUInt(0)
                        strpos = f.tell()
                        f.seek(4)
                        f.writeUInt(strpos)
                        f.seek(strpos)
                        i = 0
                        for id in section:
                            subpos = f.tell()
                            line = section[id][0]
                            timecodes = line.split(":", 2)
                            substart = int(timecodes[0])
                            subend = int(timecodes[1])
                            line = timecodes[2]
                            line = common.centerLines("<<" + line.replace("|", "|<<"), glyphs, game.subcentering)
                            game.writeUTFString(f, line, -1)
                            newpos = f.tell()
                            f.seek(8 + i * 12)
                            f.writeUInt(substart)
                            f.writeUInt(subend)
                            f.writeUInt(subpos)
                            f.seek(newpos)
                            i += 1
                else:
                    strnum = fin.readUInt()
                    if strnum == 0:
                        common.copyFile(infolder + file, outfolder + file)
                        continue
                    with common.Stream(outfolder + file, "wb", False) as f:
                        f.writeUInt(strnum)
                        f.writeUInt(fin.readUInt())
                        pos = 8 + strnum * 12
                        for i in range(strnum):
                            fin.seek(8 + i * 12)
                            f.seek(fin.tell())
                            substart = fin.readUInt()
                            subend = fin.readUInt()
                            subpointer = fin.readUInt()
                            fin.seek(subpointer)
                            substr, strlen = game.readUTFString(fin)
                            moviestr = str(substart) + ":" + str(subend) + ":" + substr
                            line = substr
                            if moviestr in section and section[moviestr][0] != "":
                                line = section[moviestr][0]
                                if line.count(":") >= 2:
                                    timecodes = line.split(":", 2)
                                    substart = int(timecodes[0])
                                    subend = int(timecodes[1])
                                    line = timecodes[2]
                                line = common.centerLines("<<" + line.replace("|", "|<<"), glyphs, game.subcentering)
                            f.writeUInt(substart)
                            f.writeUInt(subend)
                            f.writeUInt(pos)
                            f.seek(pos)
                            game.writeUTFString(f, line, -1)
                            pos = f.tell()
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
