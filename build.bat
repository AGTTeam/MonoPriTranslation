pipenv run pyinstaller --clean --icon=icon.ico --add-binary "brfnt2tpl.exe;." --distpath . -F --hidden-import="pkg_resources.py2_warn" tool.py
