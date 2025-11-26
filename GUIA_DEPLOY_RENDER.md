# 🚀 GUÍA DE DESPLIEGUE EN RENDER

Sigue estos pasos para subir tu aplicación a Internet usando Render.com.

## 📦 PASO 1: Subir tu código a GitHub

Antes de ir a Render, asegúrate de que tu código en GitHub esté actualizado. Abre tu terminal y ejecuta:

```bash
git add .
git commit -m "Listo para deploy en Render"
git push origin main
```

## 🌐 PASO 2: Crear Base de Datos (Recomendado)

Para que tus datos no se borren cada vez que reinicies la app, necesitas una base de datos real.

1. Ve a [dashboard.render.com](https://dashboard.render.com/)
2. Haz clic en **"New +"** y selecciona **"PostgreSQL"**.
3. **Name:** `db-alumnos` (o el nombre que quieras)
4. **Database:** (Déjalo en blanco o pon un nombre simple)
5. **User:** (Déjalo en blanco)
6. **Region:** `Oregon (US West)` (o la más cercana)
7. **Instance Type:** `Free` (Gratis)
8. Haz clic en **"Create Database"**.
9. **IMPORTANTE:** Cuando se cree, busca la sección **"Internal Database URL"** y cópiala. La necesitarás en el paso 4.

## 🚀 PASO 3: Crear el Web Service

1. En el dashboard de Render, haz clic en **"New +"** y selecciona **"Web Service"**.
2. Conecta tu repositorio de GitHub (`GestionDeAlumnos`).
3. Llena los campos con esta información exacta:

| Campo | Valor a poner |
|-------|---------------|
| **Name** | `gestion-alumnos` (o tu nombre preferido) |
| **Region** | `Oregon (US West)` (Misma que la DB) |
| **Branch** | `main` |
| **Root Directory** | (Déjalo en blanco) |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn mysite.wsgi` |
| **Instance Type** | `Free` |

## 🔑 PASO 4: Configurar Variables de Entorno

Antes de darle a "Create Web Service", baja hasta la sección **"Environment Variables"** y agrega las siguientes.

Haz clic en **"Add Environment Variable"** para cada una:

| Key (Clave) | Value (Valor) |
|-------------|---------------|
| `PYTHON_VERSION` | `3.10.5` |
| `SECRET_KEY` | Escribe una contraseña larga y rara (ej: `k39d#k93j!s92...`) |
| `RENDER` | `true` |
| `EMAIL_USER` | `rodriguezchristian067@gmail.com` |
| `EMAIL_PASSWORD` | `zgpdztxwgufiihhy` |
| `DATABASE_URL` | Pega aquí la **Internal Database URL** que copiaste en el PASO 2 |

> **Nota:** Si no creaste la base de datos en el Paso 2, no pongas `DATABASE_URL`. La app funcionará, pero **perderás todos los alumnos registrados** cada vez que Render reinicie el servidor (aprox. cada 15 min de inactividad).

## ✅ PASO 5: Finalizar

1. Haz clic en el botón **"Create Web Service"** al final de la página.
2. Render empezará a construir tu aplicación. Verás los logs en pantalla.
3. Espera unos minutos. Cuando diga **"Live"** en verde, ¡tu app estará online! 🌍
4. Arriba a la izquierda verás la URL de tu app (ej: `https://gestion-alumnos.onrender.com`).

---

### 🚨 Solución de Problemas Comunes

- **Error "Build Failed":** Revisa que `build.sh` tenga permisos de ejecución (Render lo suele hacer automático) y que `requirements.txt` tenga todas las librerías.
- **Error de Base de Datos:** Asegúrate de que copiaste la `Internal Database URL` correctamente.
- **No envía correos:** Verifica que `EMAIL_USER` y `EMAIL_PASSWORD` estén bien escritos en las variables de entorno.
