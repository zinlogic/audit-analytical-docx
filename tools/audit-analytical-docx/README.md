# audit-analytical-docx

## Cómo actualizar

Para obtener la última versión en Windows con PowerShell:

```powershell
git pull --ff-only
cd tools\audit-analytical-docx
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En `cmd`:

```bat
git pull --ff-only
cd tools\audit-analytical-docx
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

En Linux o macOS:

```bash
git pull --ff-only
cd tools/<nombre-del-skill>
source .venv/bin/activate
pip install -r requirements.txt
```

Si hay problemas con dependencias:

```bash
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
