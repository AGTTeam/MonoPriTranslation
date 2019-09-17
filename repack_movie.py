import codecs
import os
import game
from hacktools import common


def run():
    infolder = "data/extract/DATA/files/movie/"
    outfolder = "data/repack/DATA/files/movie/"
    infile = "data/movie_input.txt"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.logMessage("Repacking MOVIE from", infile, "...")
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
                        substr = game.readUTFString(fin)
                        moviestr = str(substart) + ":" + str(subend) + ":" + substr
                        f.writeUInt(substart)
                        f.writeUInt(subend)
                        f.writeUInt(pos)
                        f.seek(pos)
                        if moviestr in section and section[moviestr][0] != "":
                            game.writeUTFString(f, section[moviestr][0])
                        else:
                            game.writeUTFString(f, substr)
                        pos = f.tell()
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
