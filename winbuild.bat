pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --onefile  ./test/fdeval.py
#pyinstaller --clean --collect-all "flask_swagger_ui" --onefile   --add-data "saved_model.pb:."  --add-data "openapi.json:."  ./fdserver.py
pyinstaller --clean --collect-all "flask_swagger_ui" --onefile   --add-data "saved_model.pb;."  --add-data "openapi.json;."  ./fdserver.py
copy dist\fdeval.exe .
copy dist\fdserver.exe .
