from ultralytics import YOLO
import os

# Cargar el mejor modelo entrenado
model_path = '../runs/detect/train10/weights/best.pt'
model = YOLO(model_path)

print(f"✅ Modelo cargado desde: {model_path}")
print(f"📊 Clases del modelo: {model.names}")

# Probar con una imagen del dataset de validación
test_image = '../datasets/images/val/image9.jpg'  

print(f"\n🔍 Haciendo predicción en: {test_image}")

# Hacer predicción
results = model.predict(
    source=test_image,
    conf=0.25,          # Confianza mínima 25%
    save=True,          # Guardar imagen con detecciones
    show_labels=True,
    show_conf=True
)

# Mostrar resultados
print(f"\n📦 Detecciones encontradas: {len(results[0].boxes)}")

for i, box in enumerate(results[0].boxes):
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    confidence = float(box.conf[0])
    print(f"  {i+1}. {class_name}: {confidence:.2%}")

print(f"\n💾 Resultado guardado en: runs/detect/predict/")
