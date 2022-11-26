
OSX installer:

pyinstaller --clean --onefile  ./exec.py


Win:


python -m venv localenv
localenv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --onefile  ./exec.py
