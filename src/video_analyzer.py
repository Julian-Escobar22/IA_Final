from ultralytics import YOLO
import cv2
import os


class VideoEPPAnalyzer:
    """
    Analizador de videos para detección de cumplimiento EPP
    
    ============================================
    CRITERIOS DE CUMPLIMIENTO:
    ============================================
    OBLIGATORIOS: Casco + Chaleco + Guantes + Gafas
    OPCIONALES: Botas
    ============================================
    """
    
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.violations = []
        self.compliant_frames = 0
        self.total_frames = 0
        print(f"✅ Modelo cargado: {model_path}")
    
    def analyze_video(self, video_path, output_dir=None):
        """Analiza video completo y genera reporte"""
        
        # Si no se especifica output_dir, crear uno por defecto
        if output_dir is None:
            output_dir = '../results/analyzed_videos'
        
        # Crear directorio de salida
        os.makedirs(output_dir, exist_ok=True)
        
        video_name = os.path.basename(video_path).split('.')[0]
        output_path = os.path.join(output_dir, f"{video_name}_analyzed.mp4")
        
        # Abrir video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ Error: No se pudo abrir el video {video_path}")
            return None
        
        # Configurar salida
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Usar codec mp4v para compatibilidad
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Verificar que el writer se abrió correctamente
        if not out.isOpened():
            print(f"❌ Error: No se pudo crear el video de salida en {output_path}")
            cap.release()
            return None
        
        print(f"\n📹 Procesando: {video_path}")
        print(f"🎬 FPS: {fps} | Resolución: {width}x{height} | Frames: {total_frames_video}")
        print(f"💾 Salida: {output_path}")
        print("⏳ Procesando frames...")
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detectar EPP
            results = self.model.predict(frame, conf=0.25, verbose=False)[0]
            
            # Contar detecciones por clase
            detections = {}
            for box in results.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                detections[class_name] = detections.get(class_name, 0) + 1
            
            # Verificar cumplimiento
            persons = detections.get('Person', 0)
            helmets = detections.get('helmet', 0)
            vests = detections.get('vest', 0)
            gloves = detections.get('gloves', 0)
            goggles = detections.get('goggles', 0)
            boots = detections.get('boots', 0)
            
            # ============================================
            # CRITERIO: casco + chaleco + guantes + gafas
            # ============================================
            complies = (persons > 0 and 
                       helmets >= persons and 
                       vests >= persons and 
                       gloves >= persons and 
                       goggles >= persons)
            
            if complies:
                self.compliant_frames += 1
            else:
                if persons > 0:  # Solo registrar si hay personas
                    self.violations.append({
                        'frame': frame_count,
                        'time': frame_count / fps,
                        'persons': persons,
                        'helmets': helmets,
                        'vests': vests,
                        'gloves': gloves,
                        'goggles': goggles,
                        'boots': boots
                    })
            
            # Dibujar detecciones
            annotated_frame = results.plot()
            
            # Agregar overlay con estado
            status_text = "CUMPLE" if complies else "VIOLACION"
            status_color = (0, 255, 0) if complies else (0, 0, 255)
            
            # Fondo semi-transparente para texto
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (10, 10), (300, 100), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, annotated_frame, 0.7, 0, annotated_frame)
            
            # Texto de estado
            cv2.putText(
                annotated_frame, 
                status_text, 
                (20, 50), 
                cv2.FONT_HERSHEY_DUPLEX,
                1.2, 
                status_color, 
                3
            )
            
            # Info del frame
            cv2.putText(
                annotated_frame, 
                f"Frame: {frame_count}/{total_frames_video}", 
                (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (255, 255, 255), 
                2
            )
            
            # Escribir frame procesado
            out.write(annotated_frame)
            
            # Progreso cada segundo
            if frame_count % fps == 0:
                progress = (frame_count / total_frames_video) * 100
                print(f"   {progress:.1f}% completado ({frame_count}/{total_frames_video} frames)")
        
        self.total_frames = frame_count
        
        # Cerrar archivos
        cap.release()
        out.release()
        
        # Verificar que el archivo se creó
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ Video procesado guardado en: {output_path}")
            print(f"📁 Tamaño: {file_size / (1024*1024):.2f} MB")
        else:
            print(f"\n❌ Error: El archivo no se creó en {output_path}")
            return None
        
        # Generar y mostrar reporte
        self.generate_report(video_path, output_path)
        
        return output_path  # ← IMPORTANTE: Retornar la ruta
    
    def generate_report(self, input_video, output_video):
        """Genera reporte detallado del análisis"""
        compliance_rate = (self.compliant_frames / self.total_frames) * 100 if self.total_frames > 0 else 0
        violation_rate = 100 - compliance_rate
        
        print("\n" + "="*70)
        print("📊 REPORTE DE ANÁLISIS DE VIDEO - CUMPLIMIENTO EPP")
        print("="*70)
        print(f"📁 Video original: {os.path.basename(input_video)}")
        print(f"💾 Video analizado: {os.path.basename(output_video)}")
        
        print("\n" + "📌 CRITERIOS DE CUMPLIMIENTO".center(70))
        print("Obligatorios: Casco + Chaleco + Guantes + Gafas")
        print("Recomendados: Botas")
        print("-"*70)
        
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   ├─ Total de frames procesados: {self.total_frames}")
        print(f"   ├─ Frames con cumplimiento: {self.compliant_frames} ({compliance_rate:.2f}%)")
        print(f"   ├─ Frames con violaciones: {len(self.violations)} ({violation_rate:.2f}%)")
        print(f"   └─ Tasa de cumplimiento: {'✅ ALTA' if compliance_rate > 80 else '⚠️ MEDIA' if compliance_rate > 50 else '❌ BAJA'}")
        
        if self.violations:
            print(f"\n⚠️  VIOLACIONES DETECTADAS ({len(self.violations)} frames):")
            print(f"   Mostrando primeras 10 violaciones:")
            print(f"   {'Frame':<8} {'Tiempo':<10} {'Pers':<6} {'Casco':<7} {'Chaleco':<9} {'Guantes':<9} {'Gafas'}")
            print(f"   {'-'*65}")
            
            for i, v in enumerate(self.violations[:10], 1):
                print(f"   {v['frame']:<8} {v['time']:.2f}s{' '*4} "
                      f"{v['persons']:<6} {v['helmets']:<7} {v['vests']:<9} "
                      f"{v.get('gloves', 0):<9} {v.get('goggles', 0)}")
            
            if len(self.violations) > 10:
                print(f"   ... y {len(self.violations) - 10} violaciones más")
        else:
            print(f"\n✅ ¡EXCELENTE! No se detectaron violaciones de EPP")
        
        print("="*70)
        print(f"💡 Recomendación: {'Mantener prácticas actuales' if compliance_rate > 90 else 'Reforzar capacitación en EPP'}")
        print("="*70 + "\n")


# EJEMPLO DE USO
if __name__ == "__main__":
    # Ruta del modelo entrenado
    model_path = '../runs/detect/train10/weights/best.pt'
    
    # Ruta del video a analizar
    video_path = '../data/test_videos/construccion_01.mp4'
    
    # Verificar que el video existe
    if not os.path.exists(video_path):
        print(f"❌ Error: No se encontró el video en {video_path}")
        print("\n💡 Coloca tu video en: data/test_videos/")
        print("   Formatos soportados: mp4, avi, mov, mkv")
    else:
        # Inicializar analizador
        analyzer = VideoEPPAnalyzer(model_path)
        
        # Analizar video
        output = analyzer.analyze_video(video_path)
        
        if output:
            print(f"\n🎉 ¡Análisis completado exitosamente!")
            print(f"📹 Video guardado en: {output}")
        else:
            print("\n❌ Error en el análisis")
