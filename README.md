# VIRALMIND AI

Aplicación local en Python + Streamlit para descubrir videos públicos de YouTube, generar ideas, crear videos MP4 de escenas de texto y guardar ideas en SQLite.

> No garantiza viralidad. Los resultados del generador local son propuestas creativas, no tendencias verificadas.

## 1. Requisitos

- Windows 10/11, macOS o Linux.
- Python 3.11 o superior.
- FFmpeg instalado y disponible en PATH para renderizar MP4.
- Conexión a internet para usar las APIs.
- Las credenciales de YouTube son opcionales para explorar el resto de la app.

## 2. Instalación en Windows

Abre PowerShell en la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m streamlit run app.py
```

Si PowerShell impide activar el entorno, puedes ejecutar directamente:
`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
y luego:
`.\.venv\Scripts\python.exe -m streamlit run app.py`

## 3. Configurar búsqueda real de YouTube

1. Abre Google Cloud Console y crea un proyecto.
2. Habilita YouTube Data API v3.
3. Crea una API key y aplica restricciones apropiadas.
4. Copia la clave en `.env`:
   `YOUTUBE_API_KEY=tu_clave`
5. Reinicia Streamlit.

La búsqueda obtiene metadatos públicos y estadísticas públicas disponibles. La cuota de API es limitada. La aplicación no simula resultados cuando falta la clave.

Documentación oficial: https://developers.google.com/youtube/v3/getting-started

## 4. Generación de ideas con IA opcional

Configura `OPENAI_API_KEY` y `OPENAI_MODEL` en `.env`. Esto puede generar cargos según tu proveedor y uso. Si no hay clave o falla el proveedor, se usa el generador local basado en plantillas.

No se verifica una tendencia real a menos que se ejecute una consulta al radar de YouTube.

## 5. Crear videos MP4

Instala FFmpeg desde su sitio oficial o mediante un gestor de paquetes confiable. Comprueba en PowerShell:

```powershell
ffmpeg -version
```

En la pestaña **Crear video**, separa escenas con una línea que contenga `---`. El programa crea un MP4 tipo slideshow con tarjetas gráficas. Esta versión no genera automáticamente escenas cinematográficas de video ni una narración hablada; para ello se debe integrar un proveedor de video/TTS adicional. El MP4 creado puede servir como borrador visual inicial.

## 6. Publicar en YouTube

1. En Google Cloud Console, configura la pantalla de consentimiento OAuth.
2. Crea credenciales OAuth de tipo **Desktop app**.
3. Guarda el archivo descargado como `client_secret.json` en la raíz del proyecto.
4. Abre la pestaña **Crear video**.
5. Revisa el MP4, completa título y descripción, selecciona visibilidad y marca la confirmación.
6. La primera vez se abrirá el navegador para autorizar el canal.

Los tokens se guardan en `token.json`; no compartas ni subas este archivo. Esta versión de OAuth está pensada principalmente para ejecutar Streamlit en tu computadora. En un despliegue alojado (por ejemplo, Streamlit Community Cloud), el flujo OAuth de escritorio puede requerir una arquitectura de autenticación distinta. La autorización puede requerir configuración adicional según el estado de verificación de tu proyecto de Google.

La API oficial de subida: https://developers.google.com/youtube/v3/docs/videos/insert

## 7. Base de datos

La aplicación inicializa `viralmind.db` automáticamente. Guarda las ideas en la tabla `ideas`. Puedes cambiar la ruta con `DATABASE_URL`.

## 8. Pruebas

```powershell
python -m pytest -q
# También puedes ejecutar: pytest -q
```

Las pruebas validan el generador de ideas, las entradas del creador de videos y el manejo de la falta de clave de YouTube. La prueba de renderizado se omite si FFmpeg no está instalado.

## 9. Limitaciones actuales

- El radar usa YouTube Data API; no es una medición global de tendencias ni revela métricas privadas de otros canales.
- No hay garantía de viralidad.
- El creador de video produce un slideshow textual MP4; no es un generador cinematográfico completo.
- La narración sintética y la generación de clips externos no están activadas en esta versión inicial.
- La publicación requiere credenciales OAuth, autorización del propietario del canal y cuotas disponibles.
- Debes comprobar los derechos de las imágenes, música, voz y demás recursos antes de publicar.

## Estructura

```text
VIRALMIND_AI/
  app.py
  config.py
  requirements.txt
  .env.example
  services/
    idea_generator.py
    youtube_service.py
    video_maker.py
    youtube_upload.py
    storage.py
  tests/
```
