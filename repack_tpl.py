import os
from hacktools import common


def run():
    workfolder = "data/work_TPL/"
    outfolder = "data/repack/DATA/files/"
    outfolderarc = outfolder + "lytdemo/exp_data/"
    extractfolder = "data/extract_TPL/"
    repackfolder = "data/repack_TPL/"
    common.makeFolder(repackfolder)

    common.logMessage("Repacking TPL from", workfolder, "...")
    files = common.getFiles(workfolder, ".png")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        archive = file.split("/")[0]
        folder = outfolder
        if archive != "textures":
            folder = repackfolder
            if not os.path.isdir(folder + archive):
                common.copyFolder(extractfolder + archive, repackfolder + archive)
            archive += "/root/timg"
        common.execute("wimgt -o ENCODE " + workfolder + file + " -D " + folder + archive + "/" + os.path.basename(file).replace(".png", ".tpl"), False)

    common.logMessage("Repacking ARC from", repackfolder, "...")
    files = os.listdir(repackfolder)
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.execute("wszst -o CREATE " + repackfolder + file + " -D " + outfolderarc + file, False)
