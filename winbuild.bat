pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --onefile  ./eval.py
pyinstaller --clean --onefile  ./fdserver.py
copy dist\eval.exe .
copy dist\fdserver.exe .
eval.exe
