import os
import urllib.request
import zipfile

# URL del dataset Construction-PPE
url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/construction-ppe.zip"
zip_path = "construction-ppe.zip"
extract_path = "datasets/"

print("Descargando Construction-PPE dataset...")
urllib.request.urlretrieve(url, zip_path)

print("Extrayendo archivos...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

print("Dataset descargado exitosamente en:", extract_path)
os.remove(zip_path)
print("Archivo ZIP eliminado.")
