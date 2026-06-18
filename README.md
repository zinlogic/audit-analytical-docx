# audit-analytical-docx

Repositorio compartido para el skill `audit-analytical-docx`.

La implementación principal vive en:

`tools/audit-analytical-docx/`

Incluye:

- `scripts/` con el flujo determinístico de auditoría
- `requirements.txt` con las dependencias necesarias
- `SKILL.md` con el comportamiento y uso del skill
- `README.md` con el flujo de actualización

## Actualizar en Windows

Si trabajas desde PowerShell:

```powershell
git pull --ff-only
cd tools\audit-analytical-docx
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si trabajas desde `cmd`:

```bat
git pull --ff-only
cd tools\audit-analytical-docx
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Actualizar en Linux o macOS

```bash
git pull --ff-only
cd tools/audit-analytical-docx
source .venv/bin/activate
pip install -r requirements.txt
```
