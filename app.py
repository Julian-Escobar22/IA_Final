import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
from PIL import Image
import time

# Agregar src al path
sys.path.append(str(Path(__file__).parent / 'src'))

from compliance_checker import EPPComplianceChecker
from video_analyzer import VideoEPPAnalyzer
from chatbot_final import ChatbotEPP

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Sistema EPP - Detección Inteligente",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    /* Fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fondo con gradiente */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Títulos */
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center;
        padding: 1rem 0;
    }
    
    h2 {
        color: #667eea;
        font-weight: 700;
    }
    
    h3 {
        color: #764ba2;
        font-weight: 600;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 2rem;
        border: 2px dashed #667eea;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZACIÓN DE SESIÓN
# ============================================
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Inicializar chatbot una sola vez
@st.cache_resource
def init_chatbot():
    model_path = 'runs/detect/train10/weights/best.pt'
    return ChatbotEPP(model_path)

# ============================================
# HEADER
# ============================================
st.markdown("<h1>🦺 Sistema de Detección EPP</h1>", unsafe_allow_html=True)
st.markdown("---")

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/construction-helmet.png", width=80)
    st.title("📊 Panel de Control")
    
    st.info("""
    **Sistema de Detección Inteligente**
    
    Detecta automáticamente:
    - ✅ Cascos de seguridad
    - ✅ Chalecos reflectivos
    - ✅ Gafas de protección
    - ✅ Guantes de trabajo
    """)
    
    st.markdown("---")
    
    st.subheader("📈 Métricas del Modelo")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Precisión", "71.2%")
        st.metric("Velocidad", "12ms")
    with col2:
        st.metric("mAP50", "56.5%")
        st.metric("Recall", "54.4%")
    
    st.markdown("---")
    st.caption("Desarrollado con YOLOv8 + Streamlit")

# ============================================
# TABS PRINCIPALES
# ============================================
tab1, tab2, tab3 = st.tabs(["📸 Análisis de Imágenes", "🎥 Análisis de Videos", "💬 Chatbot EPP"])

# ============================================
# TAB 1: ANÁLISIS DE IMÁGENES
# ============================================
with tab1:
    st.header("📸 Análisis de Imágenes")
    st.write("Sube una imagen de un trabajador para verificar el cumplimiento de EPP")
    
    # Upload de imagen
    uploaded_image = st.file_uploader(
        "Arrastra o selecciona una imagen",
        type=['jpg', 'jpeg', 'png'],
        help="Formatos soportados: JPG, JPEG, PNG"
    )
    
    if uploaded_image:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 Imagen Original")
            image = Image.open(uploaded_image)
            st.image(image, use_container_width=True)
        
        # Botón analizar
        if st.button("🔍 Analizar Imagen", key="analyze_image"):
            with st.spinner("Analizando imagen..."):
                # Guardar imagen temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    image.save(tmp_file.name)
                    tmp_path = tmp_file.name
                
                # Analizar
                checker = EPPComplianceChecker('runs/detect/train10/weights/best.pt')
                results = checker.detect_compliance(tmp_path)
                
                # Guardar en sesión
                st.session_state.last_analysis = results
                
                # Obtener imagen con detecciones
                from ultralytics import YOLO
                model = YOLO('runs/detect/train10/weights/best.pt')
                detection_results = model.predict(tmp_path, conf=0.25, save=False)
                annotated_image = detection_results[0].plot()
                
                # Mostrar resultado
                with col2:
                    st.subheader("✅ Resultado del Análisis")
                    st.image(annotated_image, channels="BGR", use_container_width=True)
                
                # Limpiar archivo temporal
                os.unlink(tmp_path)
            
            # Métricas
            st.markdown("---")
            st.subheader("📊 Estadísticas de Cumplimiento")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "👥 Personas",
                    results['total_persons'],
                    help="Total de personas detectadas"
                )
            
            with col2:
                st.metric(
                    "✅ Cumplimiento",
                    results['summary']['compliant'],
                    help="Personas que cumplen normativas"
                )
            
            with col3:
                st.metric(
                    "❌ Violaciones",
                    results['summary']['non_compliant'],
                    delta=f"-{results['summary']['non_compliant']}",
                    delta_color="inverse",
                    help="Personas con violaciones"
                )
            
            with col4:
                compliance_rate = (results['summary']['compliant'] / results['total_persons'] * 100) if results['total_persons'] > 0 else 0
                st.metric(
                    "📈 Tasa",
                    f"{compliance_rate:.0f}%",
                    help="Porcentaje de cumplimiento"
                )
            
            # Reporte detallado
            st.markdown("---")
            st.subheader("📋 Reporte Detallado")
            
            for i, person in enumerate(results['compliance_results'], 1):
                status = "✅ CUMPLE" if person['complies'] else "❌ NO CUMPLE"
                status_color = "green" if person['complies'] else "red"
                
                with st.expander(f"👤 Persona {i}: {status}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Equipos detectados:**")
                        st.write(f"⛑️ Casco: {'✓' if person['has_helmet'] else '✗'}")
                        st.write(f"🦺 Chaleco: {'✓' if person['has_vest'] else '✗'}")
                    
                    with col2:
                        st.write(f"🥽 Gafas: {'✓' if person['has_goggles'] else '✗'}")
                        st.write(f"🧤 Guantes: {'✓' if person['has_gloves'] else '✗'}")
                    
                    if person['missing_items']:
                        st.error(f"⚠️ Falta: {', '.join(person['missing_items'])}")

# ============================================
# TAB 2: ANÁLISIS DE VIDEOS
# ============================================
with tab2:
    st.header("🎥 Análisis de Videos")
    st.write("Sube un video para analizar el cumplimiento frame por frame")
    
    # Upload de video
    uploaded_video = st.file_uploader(
        "Arrastra o selecciona un video",
        type=['mp4', 'avi', 'mov'],
        help="Formatos soportados: MP4, AVI, MOV",
        key="video_uploader"
    )
    
    if uploaded_video:
        # Mostrar video original
        st.subheader("📥 Video Original")
        st.video(uploaded_video)
        
        # Botón analizar
        if st.button("🔍 Analizar Video", key="analyze_video"):
            
            with st.spinner("⏳ Analizando video... Esto puede tomar varios minutos."):
                
                # Nombre del video
                original_video_name = uploaded_video.name
                video_name_without_ext = Path(original_video_name).stem
                
                # Crear directorio temporal
                output_dir = tempfile.mkdtemp()
                
                # Guardar video temporal
                temp_video_path = os.path.join(output_dir, original_video_name)
                with open(temp_video_path, 'wb') as f:
                    f.write(uploaded_video.getvalue())
                
                try:
                    # Analizar
                    analyzer = VideoEPPAnalyzer('runs/detect/train10/weights/best.pt')
                    output_video_path = analyzer.analyze_video(temp_video_path, output_dir=output_dir)
                    
                    if output_video_path and os.path.exists(output_video_path):
                        st.success("✅ Video analizado correctamente")
                        
                        # Métricas del video
                        st.markdown("---")
                        st.subheader("📊 Estadísticas del Video")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("🎬 Frames", analyzer.total_frames)
                        
                        with col2:
                            st.metric("✅ Cumplimiento", analyzer.compliant_frames)
                        
                        with col3:
                            st.metric("❌ Violaciones", len(analyzer.violations))
                        
                        with col4:
                            compliance_rate = (analyzer.compliant_frames / analyzer.total_frames * 100) if analyzer.total_frames > 0 else 0
                            st.metric("📈 Tasa", f"{compliance_rate:.1f}%")
                        
                        # Detalle de violaciones
                        if analyzer.violations:
                            st.markdown("---")
                            st.subheader("⚠️ Violaciones Detectadas")
                            
                            with st.expander(f"Ver detalles ({len(analyzer.violations)} frames)"):
                                st.write("**Primeras 10 violaciones:**")
                                for i, v in enumerate(analyzer.violations[:10], 1):
                                    st.write(f"**Frame {v['frame']}** (t={v['time']:.2f}s): "
                                           f"{v['persons']} personas, {v['helmets']} cascos, "
                                           f"{v['vests']} chalecos, {v.get('gloves', 0)} guantes, "
                                           f"{v.get('goggles', 0)} gafas")
                                
                                if len(analyzer.violations) > 10:
                                    st.info(f"... y {len(analyzer.violations) - 10} violaciones más")
                        else:
                            st.success("🎉 ¡Excelente! Todos los frames cumplen con las normativas EPP")
                        
                        # Botón de descarga (único visualizador)
                        st.markdown("---")
                        st.subheader("💾 Descargar Video Analizado")
                        
                        with open(output_video_path, 'rb') as f:
                            video_bytes = f.read()
                            st.download_button(
                                label="⬇️ Descargar Video con Detecciones",
                                data=video_bytes,
                                file_name=f"{video_name_without_ext}_analyzed.mp4",
                                mime="video/mp4",
                                key="download_video",
                                use_container_width=True
                            )
                        
                        st.info("💡 Descarga el video para verlo con las detecciones y cajas dibujadas")
                    
                    else:
                        st.error("❌ Error: No se pudo generar el video analizado")
                
                except Exception as e:
                    st.error(f"❌ Error durante el análisis: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                
                finally:
                    # Limpiar archivos temporales
                    try:
                        import shutil
                        if os.path.exists(output_dir):
                            shutil.rmtree(output_dir)
                    except Exception as e:
                        print(f"No se pudo eliminar directorio temporal: {e}")
        
        # Información adicional
        with st.expander("ℹ️ Información del proceso"):
            st.markdown("""
            **¿Qué hace el análisis?**
            
            1. Procesa cada frame del video
            2. Detecta personas y EPP en cada frame
            3. Verifica cumplimiento frame por frame
            4. Genera un video con las detecciones dibujadas
            5. Crea un reporte de violaciones
            
            **Criterios de cumplimiento:**
            - ✅ Obligatorios: Casco + Chaleco + Guantes + Gafas
            - 💡 Recomendado: Botas
            
            **Tiempo estimado:**
            - Video de 10 segundos: ~30 segundos
            - Video de 30 segundos: ~1-2 minutos
            - Video de 1 minuto: ~2-3 minutos
            
            **Nota:** El video procesado incluye:
            - Cajas delimitadoras de detecciones
            - Etiquetas con confianza
            - Estado de cumplimiento por frame
            - Contador de frames
            """)

# ============================================
# TAB 3: CHATBOT
# ============================================
with tab3:
    st.header("💬 Asistente Virtual EPP")
    st.write("Pregunta sobre normativas o sobre los análisis realizados")
    
    # Inicializar chatbot
    if st.session_state.chatbot is None:
        with st.spinner("Inicializando chatbot..."):
            st.session_state.chatbot = init_chatbot()
    
    # Si hay análisis previo, informar
    if st.session_state.last_analysis:
        st.info("ℹ️ Hay un análisis de imagen disponible. Puedes preguntarme sobre él.")
    
    # Historial de chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        # Agregar mensaje del usuario
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Establecer contexto si hay análisis
        if st.session_state.last_analysis:
            st.session_state.chatbot.last_analysis = st.session_state.last_analysis
        
        # Obtener respuesta
        response = st.session_state.chatbot.responder(prompt)
        
        # Agregar respuesta del bot
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Botón para limpiar chat
    if st.button("🗑️ Limpiar Chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Ejemplos de preguntas
    with st.expander("💡 Ejemplos de preguntas"):
        st.markdown("""
        **Sobre análisis realizados:**
        - ¿El trabajador cumple con las normativas?
        - ¿Qué EPP le falta?
        - ¿Qué detectaste en la imagen?
        
        **Sobre normativas generales:**
        - ¿Cuáles son los EPP obligatorios?
        - ¿Qué es un casco de seguridad?
        - ¿Cuándo usar chaleco reflectivo?
        """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Sistema de Detección EPP | Desarrollado con YOLOv8 + Streamlit | "
    f"© 2025"
    "</div>",
    unsafe_allow_html=True
)
