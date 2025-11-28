# 🚀 Guía para subir el proyecto a GitHub

Sigue estos pasos para subir tu proyecto a un repositorio de GitHub.

## 1. Preparación (Ya realizada)
Hemos verificado que tu archivo `.gitignore` está correctamente configurado para **ignorar**:
- ❌ Archivos temporales y de sistema (`__pycache__`, `.DS_Store`)
- ❌ Secretos y claves (`.env`, `.streamlit/secrets.toml`)
- ❌ Archivos obsoletos (`Deprecated/`)
- ❌ Entornos virtuales (`venv/`, `.venv/`)

## 2. Crear el Repositorio en GitHub
1. Ve a [github.com/new](https://github.com/new).
2. **Nombre del repositorio:** `triaje-ia-piloto` (o el que prefieras).
3. **Descripción:** (Opcional) "Sistema de Triaje Inteligente con Streamlit y Gemini".
4. **Visibilidad:** Elige **Público** o **Privado**.
5. **NO** marques "Initialize this repository with a README" (ya tenemos uno).
6. Haz clic en **Create repository**.

## 3. Inicializar y Subir (Desde tu terminal)
Abre una terminal en la carpeta de tu proyecto (`c:\Users\ajaba\Downloads\master\ftm\piloto ABD\nuevo\web`) y ejecuta los siguientes comandos uno por uno:

### A. Inicializar Git
```bash
git init
```

### B. Añadir archivos
```bash
git add .
```
*Esto preparará todos los archivos para la subida (respetando el .gitignore).*

### C. Crear el primer commit
```bash
git commit -m "Initial commit: Sistema de Triaje IA v1.0"
```

### D. Conectar con GitHub
Copia el comando que te da GitHub en la sección **"…or push an existing repository from the command line"**. Será algo así:
```bash
git branch -M main
git remote add origin https://github.com/TU_USUARIO/triaje-ia-piloto.git
git push -u origin main
```
*(Reemplaza `TU_USUARIO` y `triaje-ia-piloto` con tus datos reales)*.

## 4. Actualizaciones Futuras
Cuando hagas más cambios y quieras subirlos:
```bash
git add .
git commit -m "Descripción de los cambios"
git push
```
