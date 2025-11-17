from compliance_checker import EPPComplianceChecker
import os

class ChatbotEPP:
    """
    Chatbot unificado: Responde normativas + Analiza imágenes
    """
    
    def __init__(self, model_path):
        self.checker = EPPComplianceChecker(model_path)
        self.last_analysis = None
        self.last_image = None
        print("🤖 Chatbot EPP inicializado")
        print("💡 Puedo responder preguntas sobre normativas")
        print("📸 También puedo analizar imágenes si me las das\n")
    
    def analizar_imagen(self, image_path):
        """Analiza una imagen y guarda resultados"""
        if not os.path.exists(image_path):
            return f"❌ No encontré la imagen: {image_path}"
        
        print(f"\n🔍 Analizando: {image_path}")
        self.last_analysis = self.checker.detect_compliance(image_path)
        self.last_image = image_path
        
        # Mostrar resumen breve
        total = self.last_analysis['total_persons']
        compliant = self.last_analysis['summary']['compliant']
        
        return (f"✅ Análisis completado\n"
                f"👥 {total} persona(s) detectada(s)\n"
                f"✓ {compliant} en cumplimiento\n\n"
                f"Ahora puedes preguntarme: '¿cumple?', '¿qué falta?', etc.")
    
    def responder(self, pregunta):
        """Responde preguntas (normativas o sobre la imagen analizada)"""
        
        pregunta_lower = pregunta.lower()
        
        # ============================================
        # PREGUNTAS SOBRE LA IMAGEN ANALIZADA
        # ============================================
        if self.last_analysis:
            
            # ¿Cumple?
            if any(word in pregunta_lower for word in ['cumple', 'cumplimiento', 'norma']):
                return self._responder_cumplimiento()
            
            # ¿Qué falta?
            if any(word in pregunta_lower for word in ['falta', 'necesita', 'le falta']):
                return self._responder_falta()
            
            # ¿Qué detectaste?
            if any(word in pregunta_lower for word in ['detectaste', 'viste', 'hay']):
                return self._responder_detecciones()
            
            # Reporte completo
            if any(word in pregunta_lower for word in ['reporte', 'resumen', 'todo']):
                return self._responder_reporte()
        
        # ============================================
        # PREGUNTAS SOBRE NORMATIVAS (GENERALES)
        # ============================================
        
        # Normativas obligatorias
        if any(word in pregunta_lower for word in ['normativa', 'obligatorio', 'requisito']):
            return ("📋 **NORMATIVAS EPP OBLIGATORIAS**\n\n"
                   "✅ Equipos obligatorios:\n"
                   "  • Casco de seguridad\n"
                   "  • Chaleco reflectivo\n"
                   "  • Calzado de seguridad\n\n"
                   "⭐ Recomendados según actividad:\n"
                   "  • Gafas de protección\n"
                   "  • Guantes de trabajo\n"
                   "  • Protección auditiva")
        
        # ¿Qué es un casco?
        if 'casco' in pregunta_lower:
            return ("⛑️ **CASCO DE SEGURIDAD**\n\n"
                   "Protección craneal obligatoria contra:\n"
                   "  • Impactos de objetos que caen\n"
                   "  • Golpes contra estructuras\n"
                   "  • Riesgos eléctricos (según tipo)\n\n"
                   "Uso: Obligatorio en zonas de construcción, "
                   "industrias y áreas con riesgo de caída de objetos")
        
        # ¿Qué es un chaleco?
        if any(word in pregunta_lower for word in ['chaleco', 'vest']):
            return ("🦺 **CHALECO REFLECTIVO**\n\n"
                   "Prenda de alta visibilidad obligatoria para:\n"
                   "  • Aumentar visibilidad del trabajador\n"
                   "  • Zonas con tráfico vehicular\n"
                   "  • Áreas de baja iluminación\n\n"
                   "Normativa: Debe cumplir ANSI 107 o ISO 20471")
        
        # ¿Qué son las gafas?
        if any(word in pregunta_lower for word in ['gafas', 'lentes', 'goggles']):
            return ("🥽 **GAFAS DE SEGURIDAD**\n\n"
                   "Protección ocular contra:\n"
                   "  • Partículas y polvo\n"
                   "  • Salpicaduras químicas\n"
                   "  • Proyecciones de materiales\n\n"
                   "Recomendado en: Corte, esmerilado, soldadura, "
                   "manejo de químicos")
        
        # ¿Qué son los guantes?
        if 'guante' in pregunta_lower:
            return ("🧤 **GUANTES DE TRABAJO**\n\n"
                   "Protección de manos contra:\n"
                   "  • Cortes y abrasiones\n"
                   "  • Químicos (según tipo)\n"
                   "  • Temperaturas extremas\n\n"
                   "Tipos: Cuero, nitrilo, látex, térmicos (según actividad)")
        
        # Ayuda
        if pregunta_lower in ['ayuda', 'help', '?']:
            return self._mostrar_ayuda()
        
        # Saludos
        if any(word in pregunta_lower for word in ['hola', 'buenos', 'hey']):
            return ("¡Hola! 👋 Soy tu asistente EPP.\n\n"
                   "Puedo ayudarte con:\n"
                   "• Preguntas sobre normativas EPP\n"
                   "• Analizar imágenes de trabajadores\n"
                   "• Verificar cumplimiento\n\n"
                   "¿Qué necesitas?")
        
        # No entendió
        return ("🤔 No entendí tu pregunta.\n\n"
               "Puedes preguntar:\n"
               "• 'normativas obligatorias'\n"
               "• '¿qué es un casco?'\n"
               "• '¿el trabajador cumple?' (después de analizar imagen)\n\n"
               "Escribe 'ayuda' para más opciones")
    
    def _responder_cumplimiento(self):
        """Responde si cumple con normativas"""
        total = self.last_analysis['total_persons']
        compliant = self.last_analysis['summary']['compliant']
        non_compliant = self.last_analysis['summary']['non_compliant']
        
        if total == 0:
            return "❌ No detecté personas en la imagen"
        
        rate = (compliant / total) * 100
        
        if rate == 100:
            return (f"✅ **¡SÍ CUMPLE!**\n\n"
                   f"Todos los trabajadores ({compliant}/{total}) "
                   f"portan los EPP obligatorios correctamente.")
        elif rate >= 50:
            return (f"⚠️ **CUMPLIMIENTO PARCIAL** ({rate:.0f}%)\n\n"
                   f"✓ En cumplimiento: {compliant}\n"
                   f"✗ Con violaciones: {non_compliant}\n\n"
                   f"Se requiere corrección inmediata")
        else:
            return (f"❌ **NO CUMPLE** ({rate:.0f}%)\n\n"
                   f"✓ En cumplimiento: {compliant}\n"
                   f"✗ Con violaciones: {non_compliant}\n\n"
                   f"🚨 URGENTE: Detener actividades hasta corregir")
    
    def _responder_falta(self):
        """Responde qué EPP falta"""
        missing_all = []
        
        for person in self.last_analysis['compliance_results']:
            if not person['complies']:
                missing_all.extend(person['missing_items'])
        
        if not missing_all:
            return "✅ No falta ningún equipo. Todos cumplen."
        
        # Contar faltantes
        from collections import Counter
        count = Counter(missing_all)
        
        response = "⚠️ **EQUIPOS FALTANTES**\n\n"
        for item, cantidad in count.items():
            response += f"❌ {item}: {cantidad} persona(s)\n"
        
        return response
    
    def _responder_detecciones(self):
        """Responde qué se detectó"""
        total = self.last_analysis['total_persons']
        detections = self.last_analysis['total_detections']
        
        # Contar por tipo
        counts = {}
        for person in self.last_analysis['compliance_results']:
            if person.get('has_helmet'):
                counts['Cascos'] = counts.get('Cascos', 0) + 1
            if person.get('has_vest'):
                counts['Chalecos'] = counts.get('Chalecos', 0) + 1
            if person.get('has_goggles'):
                counts['Gafas'] = counts.get('Gafas', 0) + 1
            if person.get('has_gloves'):
                counts['Guantes'] = counts.get('Guantes', 0) + 1
        
        response = f"🔍 **ELEMENTOS DETECTADOS**\n\n"
        response += f"👥 Personas: {total}\n"
        response += f"📦 Total detecciones: {detections}\n\n"
        response += "**Equipos:**\n"
        
        for item, count in counts.items():
            emoji = {"Cascos": "⛑️", "Chalecos": "🦺", "Gafas": "🥽", "Guantes": "🧤"}
            response += f"  {emoji.get(item, '•')} {item}: {count}\n"
        
        return response
    
    def _responder_reporte(self):
        """Genera reporte completo"""
        self.checker.generate_report(self.last_analysis)
        return "📊 Reporte mostrado arriba ⬆️"
    
    def _mostrar_ayuda(self):
        """Muestra ayuda"""
        help_text = "🆘 **COMANDOS DISPONIBLES**\n\n"
        
        if self.last_analysis:
            help_text += "**Sobre la imagen analizada:**\n"
            help_text += "  • '¿cumple?'\n"
            help_text += "  • '¿qué falta?'\n"
            help_text += "  • '¿qué detectaste?'\n"
            help_text += "  • 'reporte completo'\n\n"
        
        help_text += "**Preguntas generales:**\n"
        help_text += "  • 'normativas obligatorias'\n"
        help_text += "  • '¿qué es un casco?'\n"
        help_text += "  • '¿qué es un chaleco?'\n"
        help_text += "  • '¿qué son las gafas?'\n"
        
        return help_text


# ============================================
# FUNCIÓN PRINCIPAL - FÁCIL DE USAR
# ============================================
def ejecutar_chatbot():
    """Función principal para usar el chatbot"""
    
    print("\n" + "="*70)
    print("🤖 CHATBOT EPP - ASISTENTE DE SEGURIDAD")
    print("="*70)
    
    # Inicializar
    chatbot = ChatbotEPP('../runs/detect/train10/weights/best.pt')
    
    print("\n📸 PASO 1: ¿Quieres analizar una imagen? (s/n)")
    analizar = input("Respuesta: ").strip().lower()
    
    if analizar == 's':
        ruta = input("\n📁 Ruta de la imagen: ").strip()
        resultado = chatbot.analizar_imagen(ruta)
        print(f"\n{resultado}")
    
    # Chat loop
    print("\n" + "="*70)
    print("💬 MODO CHAT")
    print("="*70)
    print("Ahora puedes hacerme preguntas.")
    print("Escribe 'salir' para terminar\n")
    
    while True:
        pregunta = input("👤 Tú: ").strip()
        
        if not pregunta:
            continue
        
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("\n🤖 ¡Hasta luego! 👋 Recuerda usar siempre tu EPP.\n")
            break
        
        # Comando especial para analizar otra imagen
        if pregunta.lower().startswith('analizar '):
            ruta = pregunta.split('analizar ', 1)[1]
            respuesta = chatbot.analizar_imagen(ruta)
        else:
            respuesta = chatbot.responder(pregunta)
        
        print(f"\n🤖 Bot:\n{respuesta}\n")


if __name__ == "__main__":
    ejecutar_chatbot()
