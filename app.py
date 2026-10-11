from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from services.idea_generator import generate_ideas
from services.youtube_service import search_videos, youtube_configured
from services.video_maker import create_video
from services.storage import init_db, save_idea, list_ideas
from services.youtube_upload import upload_video

load_dotenv()
init_db()
st.set_page_config(page_title="VIRALMIND AI", page_icon="🎬", layout="wide")

st.markdown("""
<style>
.stApp { background: #0A192F; color: #F4F7FB; }
[data-testid="stSidebar"] { background: #071323; }
.block-container { padding-top: 1.6rem; }
.vm-card { background: #102640; border: 1px solid #24445f; padding: 1rem; border-radius: 14px; }
h1,h2,h3 { color: #F4F7FB; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 VIRALMIND AI")
st.caption("Descubre oportunidades, crea videos y prepara contenido para YouTube.")
with st.sidebar:
    st.header("Tu estudio")
    niche = st.text_input("Nicho o tema principal", "curiosidades y ciencia")
    audience = st.selectbox("Audiencia", ["General", "Adolescentes y jóvenes", "Estudiantes", "Tecnología", "Entretenimiento"])
    country = st.selectbox("Región de búsqueda", ["US", "MX", "ES", "CO", "VE", "AR", "CL"])
    language = st.selectbox("Idioma del contenido", ["Español", "English"])
    fmt = st.radio("Formato", ["Shorts vertical 9:16", "Video largo 16:9"])
    duration = st.slider("Duración objetivo (segundos)", 15, 600, 45 if "Shorts" in fmt else 180, step=15)
    st.divider()
    st.caption("La viralidad no se puede garantizar. Las puntuaciones son orientativas.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📡 Radar YouTube", "💡 Ideas IA", "🎞️ Crear video", "🗂️ Mis ideas", "⚙️ Configuración"])

with tab1:
    st.subheader("Radar de videos públicos")
    st.write("Busca videos reales usando YouTube Data API cuando configures una clave. Sin clave, no se inventan resultados.")
    query = st.text_input("Buscar videos", value=niche, key="yt_query")
    col1, col2 = st.columns([1, 2])
    with col1:
        max_results = st.slider("Cantidad de resultados", 5, 25, 10)
        order = st.selectbox("Orden", ["relevance", "date", "viewCount", "rating"])
    with col2:
        st.info("Los datos públicos no muestran retención ni impresiones privadas de otros canales.")
    if st.button("Buscar en YouTube", type="primary"):
        if not youtube_configured():
            st.error("Falta YOUTUBE_API_KEY en tu archivo .env. Consulta README.md para configurarla.")
        else:
            with st.spinner("Consultando YouTube..."):
                try:
                    results = search_videos(query, country, max_results, order)
                    if not results:
                        st.warning("No se encontraron resultados para esa búsqueda.")
                    for item in results:
                        with st.container(border=True):
                            st.markdown(f"**[{item['title']}]({item['url']})**")
                            st.write(f"Canal: {item['channel']} · Publicado: {item['published']}")
                            stats = item.get("stats", {})
                            st.write(f"Visualizaciones: {stats.get('viewCount', 'No disponible')} · Me gusta: {stats.get('likeCount', 'No disponible')} · Comentarios: {stats.get('commentCount', 'No disponible')}")
                            st.caption("Fuente: YouTube Data API. Las estadísticas pueden no estar disponibles en todos los casos.")
                except Exception as exc:
                    st.error(f"No se pudo completar la búsqueda: {exc}")

with tab2:
    st.subheader("Generador de ideas para creadores pequeños")
    c1, c2, c3 = st.columns(3)
    with c1:
        budget = st.selectbox("Presupuesto", ["Cero o casi cero", "Bajo", "Medio"])
    with c2:
        style = st.selectbox("Estilo", ["Curiosidades", "Historia original", "Tutorial", "Explicación educativa", "Animación narrada", "Comparación"])
    with c3:
        count = st.slider("Número de ideas", 3, 12, 6)
    if st.button("Generar ideas", type="primary"):
        ideas = generate_ideas(niche, audience, fmt, duration, budget, style, count, language)
        st.session_state["ideas"] = ideas
    for i, idea in enumerate(st.session_state.get("ideas", [])):
        with st.container(border=True):
            st.markdown(f"### {i+1}. {idea['title']}")
            st.write(idea["concept"])
            st.write(f"**Gancho:** {idea['hook']}")
            st.write(f"**Estructura:** {idea['structure']}")
            st.write(f"**Miniatura:** {idea['thumbnail']}")
            st.write(f"**Esfuerzo:** {idea['effort']} · **Puntuación heurística:** {idea['score']}/100")
            st.caption(idea["score_note"])
            if st.button("Guardar idea", key=f"save_{i}"):
                save_idea(idea, niche, fmt)
                st.success("Idea guardada.")

with tab3:
    st.subheader("Crear un video sencillo con escenas y texto")
    st.write("Genera un MP4 tipo slideshow con tarjetas visuales. La narración por voz es opcional y requiere instalar/configurar un motor compatible.")
    idea_list = st.session_state.get("ideas", [])
    options = ["Escribir mi propio guion"] + [f"{i+1}. {x['title']}" for i, x in enumerate(idea_list)]
    selected = st.selectbox("Idea base", options)
    default_script = ""
    if selected != options[0] and idea_list:
        idx = options.index(selected) - 1
        default_script = idea_list[idx]["title"] + "\n\n" + idea_list[idx]["hook"] + "\n\n" + idea_list[idx]["structure"]
    script = st.text_area("Guion: separa las escenas con una línea que contenga ---", value=default_script, height=220,
                          placeholder="Una pregunta que pocos se hacen...\n\n---\n\nPrimera explicación...\n\n---\n\nConclusión...")
    video_title = st.text_input("Título del archivo", "mi_video_viralmind")
    if st.button("Renderizar MP4", type="primary"):
        if len(script.strip()) < 20:
            st.warning("Escribe un guion un poco más largo para crear escenas útiles.")
        else:
            with st.spinner("Creando escenas y renderizando video..."):
                try:
                    output = create_video(script, video_title, vertical=("Shorts" in fmt), duration=duration)
                    st.success(f"Video creado: {output}")
                    st.video(str(output))
                    st.download_button("Descargar MP4", data=Path(output).read_bytes(), file_name=Path(output).name, mime="video/mp4")
                    st.session_state["last_video"] = str(output)
                except Exception as exc:
                    st.error(f"No se pudo crear el video: {exc}")
                    st.info("Comprueba que FFmpeg esté instalado y disponible en PATH. Consulta README.md.")

    st.divider()
    st.subheader("Publicar en tu canal")
    st.warning("La subida es una acción externa. Revisa el video y confirma antes de continuar. La API puede subirlo como privado o no listado según tu selección.")
    video_path = st.text_input("Ruta del MP4", st.session_state.get("last_video", ""))
    yt_title = st.text_input("Título para YouTube", "")
    yt_desc = st.text_area("Descripción", "")
    visibility = st.selectbox("Visibilidad", ["private", "unlisted", "public"])
    confirm = st.checkbox("Confirmo que tengo derechos para usar todo el contenido y quiero subir este video.")
    if st.button("Subir a YouTube", disabled=not confirm):
        if not video_path or not Path(video_path).is_file():
            st.error("Indica una ruta de video existente.")
        elif not yt_title.strip():
            st.error("Escribe un título.")
        else:
            try:
                with st.spinner("Abriendo autorización de YouTube..."):
                    result = upload_video(video_path, yt_title, yt_desc, visibility)
                st.success(f"Subida iniciada/completada. Video ID: {result}")
                st.link_button("Abrir video", f"https://www.youtube.com/watch?v={result}")
            except Exception as exc:
                st.error(f"No se pudo subir el video: {exc}")
                st.info("Revisa las credenciales OAuth y las instrucciones del README.")

with tab4:
    st.subheader("Ideas guardadas")
    saved = list_ideas()
    if not saved:
        st.info("Todavía no has guardado ideas.")
    else:
        for item in saved:
            with st.container(border=True):
                st.markdown(f"**{item['title']}**")
                st.caption(f"{item['niche']} · {item['format']} · {item['created_at']}")
                st.write(item["concept"])

with tab5:
    st.subheader("Configuración de integraciones")
    st.markdown("""
    **YouTube Data API:** añade `YOUTUBE_API_KEY` en `.env` para buscar videos públicos.

    **Publicación:** descarga un archivo OAuth de tipo Desktop app desde Google Cloud Console y guárdalo como `client_secret.json` en la carpeta del proyecto. La primera subida abrirá el flujo de autorización.

    **Generación de ideas con LLM:** configura opcionalmente `OPENAI_API_KEY` y `OPENAI_MODEL` en `.env`. Si no están configurados, se usa el generador local basado en plantillas.

    **Video local:** instala FFmpeg y verifica que el comando `ffmpeg -version` funcione en la terminal.
    """)
    st.code("python -m pip install -r requirements.txt\npython -m streamlit run app.py", language="powershell")
