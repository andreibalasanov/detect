pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --onefile  ./test/fdeval.py
pyinstaller --clean --onefile  ./fdserver.py
copy dist\fdeval.exe .
copy dist\fdserver.exe .
fdeval.exe
