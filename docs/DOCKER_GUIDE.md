# 🐳 Guía de Despliegue con Docker

Esta guía explica cómo ejecutar la aplicación completa (Frontend, Backend API, Base de Datos y Servidor Web) utilizando Docker y Docker Compose.

## 📋 Prerrequisitos

*   **Docker Desktop** instalado y ejecutándose.
*   **Git** (para clonar el repositorio).

---

## 🏗️ Arquitectura de Contenedores

El proyecto utiliza `docker-compose` para orquestar 4 servicios interconectados:

1.  **`web` (Streamlit):** La interfaz de usuario principal.
    *   Puerto interno: `8501`
2.  **`api` (FastAPI):** El backend para integraciones externas y lógica de negocio.
    *   Puerto interno: `8000`
3.  **`mongo` (MongoDB):** La base de datos NoSQL.
    *   Puerto interno: `27017`
    *   Volumen persistente: `mongo_data`
4.  **`nginx` (Reverse Proxy):** Servidor web seguro y balanceador de carga.
    *   Puertos externos: `80` (HTTP), `443` (HTTPS)

---

## 🚀 Ejecución Rápida

1.  Abre una terminal en la raíz del proyecto.
2.  Asegúrate de tener configurado tu archivo `.env` (especialmente `GOOGLE_API_KEY`).
    *   *Nota: Docker Compose lee las variables del entorno, pero puedes crear un `.env.docker` si lo prefiere.*

3.  Construye y levanta los servicios:

```bash
docker-compose up --build
```

4.  Espera a que finalice la construcción. Verás logs de los 4 servicios.

---

## 🌐 Acceso a la Aplicación

Una vez levantados los servicios, puedes acceder a:

*   **Aplicación Web (Streamlit):** [http://localhost:8501](http://localhost:8501)
*   **API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Acceso Seguro (Nginx):** [https://localhost](https://localhost) (Si tienes certificados configurados en `nginx/certs`)

---

## 🛠️ Comandos Útiles

### Parar los servicios
```bash
docker-compose down
```

### Parar y borrar volúmenes (⛔ ¡Cuidado! Borra la base de datos)
```bash
docker-compose down -v
```

### Ver logs de un servicio específico (ej. web)
```bash
docker-compose logs -f web
```

### Entrar a la consola de un contenedor
```bash
docker-compose exec web /bin/bash
```

---

## 📝 Notas sobre SSL (Nginx)

El servicio `nginx` espera certificados SSL en la carpeta `./nginx/certs`.
*   `fullchain.pem`: Certificado público.
*   `privkey.pem`: Clave privada.

Si no tienes certificados reales, puedes generar unos **autofirmados** para desarrollo:

```bash
mkdir -p nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/certs/privkey.pem -out nginx/certs/fullchain.pem
```
