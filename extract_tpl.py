import os
from hacktools import common


def run():
    infolder = "data/extract/DATA/files/"
    infolderarc = infolder + "lytdemo/exp_data/"
    outfolder = "data/out_TPL/"
    extractfolder = "data/extract_TPL/"
    common.makeFolder(outfolder)
    common.makeFolder(extractfolder)

    # Copy the TPL files
    common.copyFolder(infolder + "textures/", extractfolder + "textures/")
    # Extract the .arc files
    common.logMessage("Extracting ARC to", extractfolder, "...")
    files = common.getFiles(infolderarc, ".arc")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.execute("wszst EXTRACT " + infolderarc + file + " -D " + extractfolder + file, False)
    common.logMessage("Done! Extracted", len(files), "files")

    # Convert TPL to PNG
    common.logMessage("Extracting TPL to", outfolder, "...")
    files = common.getFiles(extractfolder, ".tpl")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.execute("wimgt DECODE " + extractfolder + file + " -D " + outfolder + file.split("/")[0] + "/" + os.path.basename(file).replace(".tpl", ".png"), False)
    common.logMessage("Done! Extracted", len(files), "files")
