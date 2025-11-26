# 📧 GUÍA: Cómo Configurar Gmail para Enviar Emails

## ⚙️ Configuración Actual

Tu aplicación Django está configurada para enviar emails REALES por Gmail.
Sin embargo, necesitas completar algunos pasos para que funcione.

## 📝 PASOS PARA CONFIGURAR GMAIL:

### 1. Habilitar Verificación en 2 Pasos
   - Ve a: https://myaccount.google.com/security
   - Busca "Verificación en 2 pasos"
   - Si no está habilitada, actívala siguiendo las instrucciones

### 2. Crear una Contraseña de Aplicación
   - Ve a: https://myaccount.google.com/apppasswords
   - Si te pide iniciar sesión, usa tu cuenta de Gmail
   - En "Seleccionar app", elige "Correo"
   - En "Seleccionar dispositivo", elige "Otro (nombre personalizado)"
   - Escribe: "Django App" o "Sistema de Alumnos"
   - Haz clic en "Generar"
   - **IMPORTANTE**: Copia la contraseña de 16 caracteres que aparece
     (Ejemplo: abcd efgh ijkl mnop)

### 3. Configurar el Archivo .env
   Abre el archivo `.env` en la raíz del proyecto y edita:
   
   ```
   EMAIL_USER=tu-email@gmail.com
   EMAIL_PASSWORD=abcdefghijklmnop
   ```
   
   Reemplaza:
   - `tu-email@gmail.com` → Tu dirección de Gmail real
   - `abcdefghijklmnop` → La contraseña de aplicación que generaste (sin espacios)

### 4. Reiniciar el Servidor
   - Detén el servidor Django (Ctrl+C)
   - Vuelve a ejecutar: `python manage.py runserver`

## ✅ Probar que Funciona

1. Regístrate en la aplicación con un email válido
2. Deberías recibir un email de bienvenida en tu bandeja de entrada
3. Si hay errores, revisa la consola del servidor

## 🔒 Seguridad

- **NUNCA** compartas tu contraseña de aplicación
- **NUNCA** subas el archivo `.env` a GitHub o repositorios públicos
- El archivo `.env` solo debe existir en tu computadora local

## 🚨 SI NO FUNCIONA

Si no recibes emails, verifica:
1. ✅ Que la verificación en 2 pasos esté habilitada
2. ✅ Que la contraseña de aplicación sea correcta (16 caracteres, sin espacios)
3. ✅ Que el EMAIL_USER sea tu Gmail completo (con @gmail.com)
4. ✅ Que hayas reiniciado el servidor después de editar .env
5. ✅ Revisa la carpeta de SPAM en tu Gmail

## 💡 Alternativa: Modo Consola (Solo para Desarrollo)

Si prefieres NO configurar Gmail ahora y solo ver los emails en la consola:

Edita `mysite/settings.py` y comenta las líneas de SMTP:

```python
# Para desarrollo: usa console (imprime en terminal)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Para producción: usa Gmail SMTP (envía emails reales)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# ... (resto comentado)
```

De esta forma, los emails se mostrarán en la terminal donde corre el servidor.

---

✨ Una vez configurado correctamente, recibirás emails reales en tu Gmail!
