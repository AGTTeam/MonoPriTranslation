# MonoPri Translation
## Setup
Create a "data" folder and copy the iso as "disc.iso" in it.  
Install [WIT](https://wit.wiimm.de/download.html) and [SZS](https://szs.wiimm.de/download.html).  
## Run from binary
Download the latest [release](https://github.com/Illidanz/MonoPriTranslation/releases) outside the data folder.  
Run "tool extract" to extract everything and "tool repack" to repack after editing.  
Run "tool extract --help" or "tool repack --help" for more info.  
## Run from source
Install [Python 3.7](https://www.python.org/downloads/), pip and virtualenv.  
Pull [hacktools](https://github.com/Illidanz/hacktools) in the parent folder.  
```
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e ../hacktools
```
Run tool.py or build with "pyinstaller tool.spec".  
## Text Editing
Rename the \*\_output.txt files to \*\_input.txt (msbe_output.txt to msbe_input.txt, etc) and add translations for each line after the "=" sign.  
[TODO] The text in msbe_input is automatically wordwrapped, but a "|" can be used to force a line break.  
To blank out a line, use a single "!". If just left empty, the line will be left untranslated.  
Comments can be added at the end of lines by using #  
## Image Editing
Rename the out\_\* folders to work\_\* (out_TPL to work_TPL, etc).  
Edit the images in the work folder(s).  
If an image doesn't require repacking, it should be deleted from the work folder.  
