pyinstaller --clean --icon=icon.ico --distpath . -F --hidden-import="pkg_resources.py2_warn" tool.py
