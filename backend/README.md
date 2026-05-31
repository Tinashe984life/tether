# Backend (Flask)

Setup (Linux/macOS):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# generate secrets and update .env
flask db init && flask db migrate && flask db upgrade
flask run
```

Setup (Windows PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# generate secrets and update .env
flask db init ; flask db migrate ; flask db upgrade
flask run
```
