import codecs
import csv
import filecmp
import os
import time
import click
import pyimgur
import requests
from hacktools import common, wii

version = "1.3.0"
isofile = "data/disc.iso"
infolder = "data/extract/"
outfolder = "data/repack/"
replacefolder = "data/replace/"
patchin = "data/extract/DATA/files/"
patchout = "data/repack/DATA/files/"
patchfolder = "data/patch/monopri/"
xmlfile = "data/patch/riivolution/monopri.xml"


@common.cli.command()
@click.option("--iso", is_flag=True, default=False)
@click.option("--msbe", is_flag=True, default=False)
@click.option("--movie", is_flag=True, default=False)
@click.option("--tpl", is_flag=True, default=False)
@click.option("--speaker", is_flag=True, default=False)
def extract(iso, msbe, movie, tpl, speaker):
    all = not iso and not msbe and not movie and not tpl
    if all or iso:
        wii.extractIso(isofile, infolder, outfolder)
    if all or msbe:
        import extract_msbe
        extract_msbe.run(speaker)
    if all or movie:
        import extract_movie
        extract_movie.run()
    if all or tpl:
        wii.extractARC("data/extract/DATA/files/lytdemo/exp_data/", "data/extract_TPL/")
        common.copyFolder("data/extract/DATA/files/textures/", "data/extract_TPL/textures/")
        wii.extractTPL("data/extract_TPL/", "data/out_TPL/")


@common.cli.command()
@click.option("--no-patch", is_flag=True, default=False)
@click.option("--msbe", is_flag=True, default=False)
@click.option("--movie", is_flag=True, default=False)
@click.option("--tpl", is_flag=True, default=False)
def repack(no_patch, msbe, movie, tpl):
    all = not msbe and not movie and not tpl
    if all or msbe:
        import repack_msbe
        repack_msbe.run()
    if all or movie:
        import repack_movie
        repack_movie.run()
    if all or tpl:
        import repack_tpl
        repack_tpl.run()
    if os.path.isdir(replacefolder):
        common.mergeFolder(replacefolder, outfolder)

    if not no_patch:
        common.makeFolders(patchfolder)
        common.makeFolder(patchfolder.replace("monopri/", "riivolution/"))
        common.logMessage("Creating patch folder in", patchfolder, "...")
        files = common.getFiles(patchin)
        for file in common.showProgress(files):
            if not filecmp.cmp(patchin + file, patchout + file):
                common.makeFolders(patchfolder + os.path.dirname(file))
                common.copyFile(patchout + file, patchfolder + file)
        with common.Stream(xmlfile, "w") as f:
            f.writeLine('<wiidisc version="1">')
            f.writeLine('\t<id game="RSEJGD"/>')
            f.writeLine('\t<options>')
            f.writeLine('\t\t<section name="Translation">')
            f.writeLine('\t\t\t<option name="Translation Patch">')
            f.writeLine('\t\t\t\t<choice name="Enabled">')
            f.writeLine('\t\t\t\t\t<patch id="monoprifolder"/>')
            f.writeLine('\t\t\t\t</choice>')
            f.writeLine('\t\t\t</option>')
            f.writeLine('\t\t</section>')
            f.writeLine('\t</options>')
            f.writeLine('\t<patch id="monoprifolder">')
            f.writeLine('\t\t<folder external="/monopri" recursive="false"/>')
            f.writeLine('\t\t<folder external="/monopri" disc="/"/>')
            f.writeLine('\t</patch>')
            f.writeLine('</wiidisc>')
        common.logMessage("Done!")


@common.cli.command()
@click.argument("clientid")
def generatepo(clientid):
    tplfolder = "data/work_TPL"
    tploriginal = "data/out_TPL"
    files = common.getFiles(tplfolder)
    im = pyimgur.Imgur(clientid)
    with common.Stream("data/tpl.po", "w") as f:
        for file in common.showProgress(files):
            uploaded = False
            while not uploaded:
                try:
                    image = im.upload_image(tploriginal + file, title="file")
                    f.writeLine("#. " + image.link)
                    f.writeLine("msgid \"" + file.split("/")[2] + "\"")
                    f.writeLine("msgstr \"\"")
                    f.writeLine("")
                    uploaded = True
                    time.sleep(30)
                except requests.HTTPError:
                    time.sleep(300)
    common.logMessage("Done!")


@common.cli.command()
def smartcat():
    click.confirm("Import Smartcat CSV will override the msbe_input.txt file, are you sure?", abort=True)
    common.logMessage("Importing Smartcat CSV ...")
    infiles = ["data/msbe_output (rearranged).csv", "data/msbe_events.csv", "data/msbe_system.csv"]
    section = {}
    commonsection = {}
    current = ""
    for file in infiles:
        with open(file, newline="", encoding="utf-8") as csvfile:
            rows = csv.reader(csvfile, delimiter=",", quotechar="\"")
            for row in rows:
                orig = row[0]
                trans = row[1]
                if orig == "ja" or ".png" in orig or "youtube.com" in orig or orig == "Table of Contents:" or orig == "!Images":
                    continue
                if orig.startswith("("):
                    orig = orig.split(") ", 1)[1]
                if orig != "":
                    if orig.startswith("!FILE:"):
                        current = orig.split(",")[0].replace("!FILE:", "")
                        section[current] = {}
                    elif current != "":
                        if orig in section[current]:
                            section[current][orig].append(trans)
                        else:
                            section[current][orig] = [trans]
                        if orig in commonsection:
                            commonsection[orig].append(trans)
                        else:
                            commonsection[orig] = [trans]
    with codecs.open("data/msbe_output.txt", "r", "utf-8") as fin:
        with codecs.open("data/msbe_input.txt", "w", "utf-8") as f:
            sectionname = ""
            for line in fin:
                line = line.rstrip("\r\n").replace("\ufeff", "")
                if line.startswith("!FILE:"):
                    sectionname = line.replace("!FILE:", "")
                    if sectionname not in section:
                        common.logWarning("Section", sectionname, "not found")
                        sectionname = ""
                    else:
                        f.write("!FILE:" + sectionname + "\n")
                elif sectionname != "":
                    line = line.replace("=", "")
                    sectionline = line
                    if line not in section[sectionname]:
                        if line.strip() in section[sectionname]:
                            sectionline = line.strip()
                        elif line in commonsection:
                            section[sectionname][line] = commonsection[line]
                        elif line.replace("<3D>", "=") in section[sectionname]:
                            sectionline = line.replace("<3D>", "=")
                    if sectionline in section[sectionname]:
                        f.write(line + "=" + section[sectionname][sectionline][0] + "\n")
                        if len(section[sectionname][sectionline]) > 1:
                            section[sectionname][sectionline].pop()
                    else:
                        common.logWarning("Line \"" + line + "\" in section", sectionname, "not found")
    common.logMessage("Done!")


if __name__ == "__main__":
    click.echo("MonoPriTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.cli()
