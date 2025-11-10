echo Building Project

.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/pyinstaller --onefile server.py
echo Built Server

.venv/Scripts/pyinstaller client.py
echo Built Client

echo Build Complete
