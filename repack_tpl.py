import os
import game
from hacktools import common, wii


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
    # Copy tweaked main screen layout file
    for file in common.getFiles(repackfolder, ".brlyt"):
        filename = file.split("/")
        filename = filename[len(filename) - 1]
        if os.path.isfile("data/brlyt/" + filename):
            common.copyFile("data/brlyt/" + filename, repackfolder + file)
    common.logMessage("Done!")

    common.logMessage("Repacking ARC from", repackfolder, "...")
    files = os.listdir(repackfolder)
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        game.repackARC(repackfolder + file, outfolderarc + file)
    common.logMessage("Done!")
    # Copy tweaked 3d model texture
    common.logMessage("Repacking 3D from", "data/work_3D", "...")
    common.copyFolder("data/extract_3D", "data/repack_3D")
    common.copyFile("data/work_3D/ID002_0000.brres", "data/repack_3D/item_od_all.arc/pac/ID002_0000.brres")
    game.repackARC("data/repack_3D/item_od_all.arc", "data/repack/DATA/files/3d/map/item_od_all.arc")
    common.logMessage("Done!")
    # Copy particle effects
    common.logMessage("Repacking EFF from", "data/work_EFF", "...")
    common.copyFolder("data/extract_EFF", "data/repack_EFF")
    common.makeFolder("data/repack_BREFT")
    files = common.getFiles("data/work_EFF", ".png")
    for file in common.showProgress(files):
        filesplit = file.split("/")
        arcfile = filesplit[1]
        breftfile = filesplit[2]
        pngfile = filesplit[3]
        common.copyFolder("data/extract_BREFT/" + arcfile + "/" + breftfile, "data/repack_BREFT/" + arcfile + "/" + breftfile)
        common.execute("wimgt -o ENCODE data/work_EFF" + file + " -D " + "data/repack_BREFT/" + arcfile + "/" + breftfile + "/files/" + pngfile.replace(".png", "") + " -x BTIMG", False)
        common.execute("wszst -o CREATE " + "data/repack_BREFT/" + arcfile + "/" + breftfile + " -D " + "data/repack_EFF/" + arcfile + "/" + arcfile.replace(".arc", "") + "/" + breftfile, False)
    common.logMessage("Repacking ARC from", "data/repack_EFF", "...")
    files = os.listdir("data/repack_EFF")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        game.repackARC("data/repack_EFF/" + file, outfolder + "effect/" + file)
    common.logMessage("Done!")
