import os
from hacktools import common, wii


def run():
    workfolder = "data/work_TPL/"
    outfolder = "data/repack/DATA/files/"
    outfolderarc = outfolder + "lytdemo/exp_data/"
    replacefolder = "data/replace_TPL/"
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
        tplfile = os.path.basename(file).replace(".png", ".tpl")
        if archive != "textures":
            folder = repackfolder
            if not os.path.isdir(folder + archive):
                common.copyFolder(extractfolder + archive, repackfolder + archive)
            archive += "/root/timg/"
            tpl = wii.readTPL(repackfolder + archive + tplfile)
            wii.writeTPL(repackfolder + archive + tplfile, tpl, workfolder + file)
        elif ".mm" not in file:
            format = "R565" if "TX900_0010" in tplfile or "TX900_0020" in tplfile else "R3"
            common.execute("wimgt -o ENCODE " + workfolder + file + " -D " + folder + archive + "/" + tplfile + " -x TPL." + format, False)

    common.logMessage("Repacking ARC from", repackfolder, "...")
    if os.path.isdir(replacefolder):
        common.mergeFolder(replacefolder, repackfolder)
    files = os.listdir(repackfolder)
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.execute("wszst -o CREATE " + repackfolder + file + " -D " + outfolderarc + file, False)
        # Blank out the 0xCC bytes that are different from the original
        with common.Stream(outfolderarc + file, "r+b") as f:
            f.seek(16)
            f.writeZero(16)
