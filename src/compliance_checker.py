from ultralytics import YOLO
import numpy as np


class EPPComplianceChecker:
    """
    Sistema de verificación de cumplimiento de EPP
    
    ============================================
    CRITERIOS DE CUMPLIMIENTO:
    ============================================
    OBLIGATORIOS (todos requeridos):
    - ⛑️ Casco (helmet)
    - 🦺 Chaleco (vest)  
    - 🧤 Guantes (gloves)
    - 🥽 Gafas (goggles)
    
    RECOMENDADOS (opcionales):
    - 🥾 Botas (boots)
    ============================================
    """
    
    def __init__(self, model_path):
        """Inicializar con el modelo entrenado"""
        self.model = YOLO(model_path)
        print(f"✅ Modelo cargado: {model_path}")
        print(f"📋 Clases: {self.model.names}")
    
    def check_overlap(self, person_box, item_boxes, threshold=0.3):
        """
        Verifica si algún item (casco, chaleco, etc.) se superpone con la persona
        
        Args:
            person_box: [x1, y1, x2, y2] - Caja de la persona
            item_boxes: Lista de cajas [x1, y1, x2, y2] - Items detectados
            threshold: % de superposición mínimo
        
        Returns:
            bool: True si hay superposición suficiente
        """
        if len(item_boxes) == 0:
            return False
        
        px1, py1, px2, py2 = person_box
        
        for item in item_boxes:
            ix1, iy1, ix2, iy2 = item
            
            # Calcular área de intersección
            x1 = max(px1, ix1)
            y1 = max(py1, iy1)
            x2 = min(px2, ix2)
            y2 = min(py2, iy2)
            
            if x2 > x1 and y2 > y1:
                intersection = (x2 - x1) * (y2 - y1)
                item_area = (ix2 - ix1) * (iy2 - iy1)
                
                # Si el item está al menos threshold% superpuesto
                if intersection / item_area > threshold:
                    return True
        
        return False
    
    def detect_compliance(self, image_path, conf_threshold=0.25):
        """
        Detecta EPP y verifica cumplimiento de normativa
        
        Args:
            image_path: Ruta de la imagen a analizar
            conf_threshold: Umbral de confianza mínimo
        
        Returns:
            dict: Resultados del análisis
        """
        # Hacer predicción
        results = self.model.predict(
            source=image_path,
            conf=conf_threshold,
            verbose=False
        )[0]
        
        # Extraer detecciones por clase
        persons = []
        helmets = []
        vests = []
        boots = []
        goggles = []
        gloves = []
        no_helmet = []
        no_vest = []
        no_boots = []
        
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            bbox = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            
            if class_name == 'Person':
                persons.append({'bbox': bbox, 'conf': conf})
            elif class_name == 'helmet':
                helmets.append(bbox)
            elif class_name == 'vest':
                vests.append(bbox)
            elif class_name == 'boots':
                boots.append(bbox)
            elif class_name == 'goggles':
                goggles.append(bbox)
            elif class_name == 'gloves':
                gloves.append(bbox)
            elif class_name == 'no_helmet':
                no_helmet.append(bbox)
            elif class_name == 'no_vest':
                no_vest.append(bbox)
            elif class_name == 'no_boots':
                no_boots.append(bbox)
        
        # Análisis de cumplimiento por persona
        compliance_results = []
        
        for i, person in enumerate(persons):
            person_bbox = person['bbox']
            
            # Verificar cada EPP
            has_helmet = self.check_overlap(person_bbox, helmets)
            has_vest = self.check_overlap(person_bbox, vests)
            has_boots = self.check_overlap(person_bbox, boots)
            has_goggles = self.check_overlap(person_bbox, goggles)
            has_gloves = self.check_overlap(person_bbox, gloves)
            
            # Verificar violaciones
            missing_helmet = self.check_overlap(person_bbox, no_helmet)
            missing_vest = self.check_overlap(person_bbox, no_vest)
            missing_boots = self.check_overlap(person_bbox, no_boots)
            
            # ============================================
            # CRITERIO DE CUMPLIMIENTO
            # ============================================
            # OBLIGATORIOS: casco + chaleco + guantes + gafas
            # OPCIONALES: botas
            complies = (has_helmet and has_vest and has_gloves and has_goggles)
            
            # Identificar elementos faltantes
            missing_items = []
            if not has_helmet:
                missing_items.append('casco')
            if not has_vest:
                missing_items.append('chaleco')
            if not has_gloves:
                missing_items.append('guantes')
            if not has_goggles:
                missing_items.append('gafas')
            
            # Botas son opcionales (recomendadas)
            if not has_boots:
                missing_items.append('botas (recomendado)')
            
            compliance_results.append({
                'person_id': i + 1,
                'complies': complies,
                'has_helmet': has_helmet,
                'has_vest': has_vest,
                'has_boots': has_boots,
                'has_goggles': has_goggles,
                'has_gloves': has_gloves,
                'missing_items': missing_items,
                'confidence': person['conf']
            })
        
        return {
            'image': image_path,
            'total_persons': len(persons),
            'total_detections': len(results.boxes),
            'compliance_results': compliance_results,
            'summary': {
                'compliant': sum(1 for r in compliance_results if r['complies']),
                'non_compliant': sum(1 for r in compliance_results if not r['complies'])
            }
        }
    
    def generate_report(self, compliance_data):
        """Genera reporte legible del análisis"""
        print("\n" + "="*70)
        print("📋 REPORTE DE CUMPLIMIENTO DE EPP")
        print("="*70)
        print(f"📁 Imagen: {compliance_data['image']}")
        print(f"👥 Personas detectadas: {compliance_data['total_persons']}")
        print(f"📦 Total de detecciones: {compliance_data['total_detections']}")
        print(f"✅ Personas en cumplimiento: {compliance_data['summary']['compliant']}")
        print(f"❌ Personas sin cumplimiento: {compliance_data['summary']['non_compliant']}")
        
        print("\n" + "📌 CRITERIOS DE CUMPLIMIENTO".center(70))
        print("Obligatorios: Casco + Chaleco + Guantes + Gafas")
        print("Recomendados: Botas")
        print("-"*70)
        
        for result in compliance_data['compliance_results']:
            status = "✅ CUMPLE" if result['complies'] else "❌ NO CUMPLE"
            print(f"\n👤 Persona {result['person_id']}: {status}")
            print(f"   Confianza: {result['confidence']:.2%}")
            print(f"   {'='*50}")
            print(f"   ⛑️  Casco:    {'✓ Detectado' if result['has_helmet'] else '✗ FALTA'}")
            print(f"   🦺 Chaleco:  {'✓ Detectado' if result['has_vest'] else '✗ FALTA'}")
            print(f"   🧤 Guantes:  {'✓ Detectado' if result['has_gloves'] else '✗ FALTA'}")
            print(f"   🥽 Gafas:    {'✓ Detectado' if result['has_goggles'] else '✗ FALTA'}")
            print(f"   🥾 Botas:    {'✓ Detectado' if result['has_boots'] else '○ No detectado (opcional)'}")
            
            if result['missing_items']:
                obligatorios = [x for x in result['missing_items'] if 'recomendado' not in x]
                recomendados = [x for x in result['missing_items'] if 'recomendado' in x]
                
                if obligatorios:
                    print(f"   ⚠️  FALTA (obligatorio): {', '.join(obligatorios)}")
                if recomendados:
                    print(f"   💡 Recomendado: {', '.join(recomendados)}")
        
        print("\n" + "="*70)


# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar sistema
    checker = EPPComplianceChecker('../runs/detect/train10/weights/best.pt')
    
    # Analizar imagen
    results = checker.detect_compliance('../datasets/images/val/image9.jpg')
    
    # Generar reporte
    checker.generate_report(results)
