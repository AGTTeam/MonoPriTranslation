import os
from hacktools import common


def run():
    workfolder = "data/work_TPL/"
    outfolder = "data/repack/DATA/files/"
    outfolderarc = outfolder + "lytdemo/exp_data/"
    extractfolder = "data/extract_TPL/"
    repackfolder = "data/repack_TPL/"
    common.makeFolder(repackfolder)

    common.logMessage("Copying original TPL files...")
    common.copyFolder(outfolderarc.replace("repack/", "extract/"), outfolderarc)
    common.copyFolder(outfolder.replace("repack/", "extract/") + "textures", outfolder + "textures")
    common.logMessage("Repacking TPL from", workfolder, "...")
    files = common.getFiles(workfolder, ".png")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        archive = file.split("/")[0]
        folder = outfolder
        format = ""
        if archive != "textures":
            folder = repackfolder
            if not os.path.isdir(folder + archive):
                common.copyFolder(extractfolder + archive, repackfolder + archive)
            archive += "/root/timg"
            format = " -x TPL.C8.P3"
        elif "mm1" in file:
            continue
        common.execute("wimgt -o ENCODE " + workfolder + file + " -D " + folder + archive + "/" + os.path.basename(file).replace(".png", ".tpl") + format, False)

    common.logMessage("Repacking ARC from", repackfolder, "...")
    files = os.listdir(repackfolder)
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.execute("wszst -o CREATE " + repackfolder + file + " -D " + outfolderarc + file, False)
        # Blank out the 0xCC bytes that are different from the original
        with common.Stream(outfolderarc + file, "r+b") as f:
            f.seek(16)
            f.writeZero(16)
