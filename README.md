# MonoPri Translation
This repository is for the tool used to translate the game. If you're looking for the English patch, click [here](https://agtteam.net/monopri).  
## Setup
Install [Python 3](https://www.python.org/downloads/).  
Install [WIT](https://wit.wiimm.de/download.html) and [SZS](https://szs.wiimm.de/download.html).  
Download this repository by downloading and extracting it, or cloning it.  
Copy the original Japanese rom into the same folder and rename it as `disc.iso`.  
Run `run_windows.bat` (for Windows) or `run_bash` (for OSX/Linux) to run the tool.  
## Text Editing
Rename the \*\_output.txt files to \*\_input.txt (msbe_output.txt to msbe_input.txt, etc) and add translations for each line after the "=" sign.  
The text in msbe_input is automatically wordwrapped, but a "|" can be used to force a line break.  
To blank out a line, use a single "!". If just left empty, the line will be left untranslated.  
Comments can be added at the end of lines by using #  
## Image Editing
Rename the out\_\* folders to work\_\* (out_TPL to work_TPL, etc).  
Edit the images in the work folder(s).  
If an image doesn't require repacking, it should be deleted from the work folder.  
## Smartcat import
To import the translate lines, download the .csv files from Smartcat (Export -> Special Formats -> Multilingual CSV) and put them in the data folder, then run `tool smartcat`.  
Note that this will override the msbe_input.txt file.  
## Run from command line
This is not recommended if you're not familiar with Python and the command line.  
After following the Setup section, run `pipenv sync` to install dependencies.  
Run `pipenv run python tool.py extract` to extract everything, and `pipenv run python tool.py repack` to repack.  
You can use switches like `pipenv run python tool.py repack --bin` to only repack certain parts to speed up the process.  
