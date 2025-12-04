# Guía de Despliegue en Streamlit Community Cloud

¡Felicidades! Tu aplicación está lista para ser desplegada. Sigue estos pasos para subirla a la nube de forma gratuita.

## 1. Preparar el Repositorio en GitHub
Asegúrate de que tu código está actualizado en tu repositorio de GitHub.
*   Si has hecho cambios locales, haz un **commit** y un **push** a tu rama principal (`master` o `main`).
*   Asegúrate de que el archivo `requirements.txt` está en la raíz (ya lo está).

## 2. Conectar Streamlit con GitHub
1.  Ve a [share.streamlit.io](https://share.streamlit.io/).
2.  Haz clic en el botón **"Sign in with GitHub"** (o "Continue with GitHub").
3.  Autoriza a Streamlit para acceder a tus repositorios públicos (y privados si es necesario).

## 3. Crear la App
1.  En el panel principal de Streamlit, haz clic en el botón azul **"New app"**.
2.  Selecciona **"Use existing repo"**.
3.  Rellena los campos:
    *   **Repository:** `ajabadia/TRYaG`
    *   **Branch:** `main`
    *   **Main file path:** `src/app.py` (¡Importante! No es `app.py` a secas, está dentro de `src`).
    *   **App URL:** Puedes personalizar el subdominio si está disponible (ej: `triaje-trauma-piloto.streamlit.app`).

## 4. Configurar Secretos (MUY IMPORTANTE)
Antes de darle a "Deploy", o inmediatamente después si falla:
1.  Haz clic en **"Advanced settings"** (o en los tres puntos de la app -> Settings -> Secrets).
2.  Verás un editor de texto para "Secrets".
3.  Copia el contenido de tu archivo local `.streamlit/secrets.toml` (o `.env` adaptado) y pégalo allí.
4.  Debe tener este formato TOML:

```toml
GOOGLE_API_KEY = "tu_clave_de_google_aqui"
MONGODB_URI = "tu_cadena_de_conexion_de_mongodb_atlas"
```

> **Nota:** No incluyas comillas extrañas ni espacios innecesarios.

## 5. Desplegar
1.  Haz clic en **"Deploy!"**.
2.  Streamlit empezará a "cocinar" tu app (instalando dependencias). Esto puede tardar unos minutos la primera vez.
3.  Si todo va bien, verás tu aplicación ejecutándose en la URL elegida.

## Solución de Problemas Comunes

*   **Error "ModuleNotFoundError":** Revisa que todas las librerías importadas estén en `requirements.txt`.
*   **Error de Conexión a Mongo:** Verifica que la IP `0.0.0.0/0` (acceso desde cualquier lugar) está permitida en la "Network Access" de tu panel de MongoDB Atlas, ya que las IPs de Streamlit Cloud cambian.
*   **Archivos no encontrados:** Recuerda que las rutas son relativas a la raíz del repositorio.
