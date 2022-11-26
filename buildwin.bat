python -m venv localenv
localenv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --onefile  ./eval.py
copy dist/eval.exe .
