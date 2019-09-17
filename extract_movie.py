import codecs
import game
from hacktools import common


def run():
    infolder = "data/extract/DATA/files/movie/"
    outfile = "data/movie_output.txt"

    common.logMessage("Extracting MOVIE to", outfile, "...")
    with codecs.open(outfile, "w", "utf-8") as out:
        files = common.getFiles(infolder, ".bin")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            with common.Stream(infolder + file, "rb", False) as f:
                strnum = f.readUInt()
                if strnum == 0:
                    continue
                out.write("!FILE:" + file + "\n")
                for i in range(strnum):
                    f.seek(8 + i * 12)
                    substart = f.readUInt()
                    subend = f.readUInt()
                    subpointer = f.readUInt()
                    f.seek(subpointer)
                    substr = game.readUTFString(f)
                    out.write(str(substart) + ":" + str(subend) + ":" + substr + "=\n")
    common.logMessage("Done! Extracted", len(files), "files")
