#Generador de Estructuras por ESMFold
#Objetivo y Fundamento
#Modelado por Inteligencia Artificial: Utiliza la API de ESMFold (Meta AI) para predecir la estructura tridimensional de proteínas a partir de su secuencia de aminoácidos.
#Recuperación Automática: Conecta con UniProt para extraer las secuencias oficiales de forma masiva, asegurando que los datos de entrada sean exactos.
#Optimización de Longitud: Implementa un recorte estratégico a 400 residuos (enfocado en el N-terminal) para cumplir con los límites técnicos de la IA, priorizando la zona con mayor probabilidad de mimetismo funcional.

#Resultados y Entregables
#Archivos Estructurales (.pdb): Genera los modelos 3D necesarios para realizar los alineamientos estructurales posteriores.
#Dataset Ampliado: Permite incluir en tu estudio proteínas que antes eran imposibles de analizar por falta de datos cristalográficos.
#Trazabilidad de Corte: Reporta qué estructuras fueron generadas completas y cuáles fueron truncadas, garantizando el rigor metodológico.
import os
import requests
import time
import urllib3

# Desactivar las advertencias de seguridad SSL (necesario para entornos virtuales)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURACIÓN DE RUTAS ---
RUTA_CARPETAS_BASE = r"\\Mac\Home\Desktop\Codigos\Alineamientos_Estructurales\ID_PDB_ALING"
RUTA_LISTA_FALTANTES = r"\\Mac\Home\Desktop\Codigos\Alineamientos_Estructurales\IDs_Faltantes_Gesamt.txt"

# Límite de aminoácidos impuesto por la API de ESMFold
LIMITE_AA_ESMFOLD = 400 

# Headers para simular un navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'text/plain'
}

def obtener_secuencia_uniprot(uniprot_id):
    """Consulta la API de UniProt para obtener la secuencia de aminoácidos."""
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    try:
        response = requests.get(url, timeout=10, verify=False) 
        if response.status_code == 200:
            lineas = response.text.splitlines()
            secuencia = "".join([line.strip() for line in lineas if not line.startswith(">")])
            return secuencia
        else:
            return None
    except Exception:
        return None

def predecir_con_esmfold(secuencia, id_proteina):
    """Envía la secuencia a la API de ESMFold y retorna el contenido del PDB."""
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    
    # 1. Aplicar la lógica de corte si la secuencia es demasiado larga
    secuencia_original_len = len(secuencia)
    if secuencia_original_len > LIMITE_AA_ESMFOLD:
        # Cortar al límite permitido (obtenemos el N-terminal)
        secuencia_a_enviar = secuencia[:LIMITE_AA_ESMFOLD]
        corte = f" (CORTADA: {secuencia_original_len}->{LIMITE_AA_ESMFOLD}aa)"
    else:
        secuencia_a_enviar = secuencia
        corte = ""

    try:
        response = requests.post(url, data=secuencia_a_enviar, headers=HEADERS, timeout=60, verify=False) 
        
        if response.status_code == 200:
            contenido = response.text
            if "ATOM" in contenido or "REMARK" in contenido:
                return contenido, f"ÉXITO{corte}"
            else:
                return None, "Respuesta vacía o formato incorrecto de PDB"
        else:
            return None, f"Error API ({response.status_code}): {response.text[:100]}" 
    except Exception as e:
        return None, f"Excepción Python: {e}"

def ejecutar_predicciones():
    if not os.path.exists(RUTA_LISTA_FALTANTES):
        print("Error: No se encuentra el archivo de IDs faltantes.")
        return

    with open(RUTA_LISTA_FALTANTES, 'r') as f:
        ids_a_procesar = [line.strip() for line in f if line.strip()]

    total = len(ids_a_procesar)
    print(f"--- INICIANDO PREDICCIÓN CON MANEJO DE LÍMITE DE 400aa ---")
    print(f"Total: {total}")
    print("-" * 60)

    exitos = 0
    fallos = 0

    for i, uniprot_id in enumerate(ids_a_procesar, 1):
        mensaje_progreso = f"[{i}/{total}] ID: {uniprot_id}"
        
        carpeta_id = os.path.join(RUTA_CARPETAS_BASE, uniprot_id)
        ruta_pdb_final = os.path.join(carpeta_id, f"{uniprot_id}.pdb")

        # 1. Obtener Secuencia
        secuencia = obtener_secuencia_uniprot(uniprot_id)
        
        if not secuencia:
            print(f"{mensaje_progreso} -> FALLO: No se pudo obtener secuencia de UniProt.")
            fallos += 1
            continue

        # 2. Predecir
        time.sleep(1) # Pausa
        pdb_content, mensaje_resultado = predecir_con_esmfold(secuencia, uniprot_id)

        if "ÉXITO" in mensaje_resultado:
            if not os.path.exists(carpeta_id):
                os.makedirs(carpeta_id)
                
            with open(ruta_pdb_final, 'w') as f:
                f.write(pdb_content)
            
            print(f"{mensaje_progreso} -> {mensaje_resultado}. PDB guardado.")
            exitos += 1
        else:
            print(f"{mensaje_progreso} -> FALLO: {mensaje_resultado}")
            fallos += 1

    print("-" * 60)
    print(f"PROCESO TERMINADO. Estructuras Generadas (completas o cortadas): {exitos} | Fallos persistentes: {fallos}")

if __name__ == "__main__":
    ejecutar_predicciones()