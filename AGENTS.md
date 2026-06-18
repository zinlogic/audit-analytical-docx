# AGENTS.md

## Actualización del skill compartido

Instrucciones para Codex:

1. Antes de usar el skill, verificar que el repositorio local esté actualizado:

   ```bash
   git status
   git pull --ff-only
   ```

2. Si hubo cambios en:

   * `tools/<nombre-del-skill>/scripts/`
   * `tools/<nombre-del-skill>/requirements.txt`
   * `tools/<nombre-del-skill>/pyproject.toml`
   * `tools/<nombre-del-skill>/README.md`

   entonces actualizar dependencias:

   ```bash
   cd tools/<nombre-del-skill>
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Si el entorno virtual no existe, recrearlo:

   ```bash
   cd tools/<nombre-del-skill>
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Nunca modificar scripts compartidos directamente en `main`.

   * Crear una rama nueva.
   * Hacer los cambios.
   * Probar el skill.
   * Abrir pull request.

5. Para mejoras del skill, usar este flujo:

   ```bash
   git checkout -b codex/update-shared-skill
   # editar scripts o dependencias
   # probar
   git add tools/<nombre-del-skill> AGENTS.md
   git commit -m "Update shared Codex skill"
   git push -u origin codex/update-shared-skill
   ```

6. Al finalizar, reportar:

   * Qué archivos cambiaron.
   * Qué pruebas se ejecutaron.
   * Si hubo cambios en dependencias.
   * Si los usuarios deben recrear o actualizar su `.venv`.
