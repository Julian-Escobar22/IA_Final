from ultralytics import YOLO
import os

# Este script descarga automáticamente el dataset Construction-PPE
print("Descargando dataset Construction-PPE...")

# Crear directorio para datasets si no existe
os.makedirs("../datasets", exist_ok=True)

# La primera vez que entrenes con este dataset, YOLO lo descargará automáticamente
# desde: https://github.com/ultralytics/assets/releases/download/v0.0.0/construction-ppe.zip

print("""
El dataset se descargará automáticamente cuando ejecutes el entrenamiento.
Contiene:
- 11 clases de EPP y violaciones
- Imágenes de construcción reales
- Formato YOLO listo para usar

Dataset ubicación: ../datasets/construction-ppe/
""")
