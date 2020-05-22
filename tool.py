import filecmp
import os
import click
import time
import pyimgur
import requests
from hacktools import common, wii

version = "1.2.5"
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
def extract(iso, msbe, movie, tpl):
    all = not iso and not msbe and not movie and not tpl
    if all or iso:
        wii.extractIso(isofile, infolder, outfolder)
    if all or msbe:
        import extract_msbe
        extract_msbe.run()
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
                    f.writeLine('#. ' + image.link)
                    f.writeLine('msgid "' + file.split("/")[2] + '"')
                    f.writeLine('msgstr ""')
                    f.writeLine('')
                    uploaded = True
                    time.sleep(30)
                except requests.HTTPError:
                    time.sleep(300)
    common.logMessage("Done!")


if __name__ == "__main__":
    click.echo("MonoPriTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.cli()
