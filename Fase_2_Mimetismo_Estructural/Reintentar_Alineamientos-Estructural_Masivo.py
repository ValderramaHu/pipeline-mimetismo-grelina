#Generador de Alineamiento Estructural Masivo
#Objetivo y Fundamento
#Automatización Estructural: Coordina el software Gesamt para alinear masivamente cientos de proteínas contra el molde de la Grelina en un espacio tridimensional.
#Superposición 3D: Su función es encontrar la posición espacial donde la proteína analizada se parece más a la Grelina, calculando la rotación y traslación óptimas.
#Recuperación de Datos: Está diseñado para procesar específicamente listas de archivos faltantes o errores previos, asegurando que tu dataset esté completo al 100%.

#Resultados y Entregables
#Por cada proteína analizada, el script entrega:
#Archivo de Coordenadas (_superposed.pdb): La estructura lista para visualizar el mimetismo en programas 3D como PyMOL.
#Matriz de Correspondencia (_results.csv): El archivo clave que indica qué aminoácido de la Grelina coincide con el de la proteína objetivo (insumo para el análisis químico).
#Reporte de Calidad (_reporte.txt): Contiene los valores científicos (RMSD y Q-score) que validan si el alineamiento es confiable.
import os
import subprocess
import time

# --- CONFIGURACIÓN DE RUTAS ---
# 1. Ruta al ejecutable de Gesamt
RUTA_GESAMT = r"C:\Program Files (x86)\CCP4MG\pythondist\Lib\site-packages\ccp4mg\CCP4\bin\gesamt.exe"

# 2. Archivo de REFERENCIA (El molde contra el que alineas)
RUTA_PDB_REFERENCIA = r"C:\Mac\Home\Desktop\GHRELIN_alpha28.pdb"

# 3. Carpeta donde están las subcarpetas de cada proteína
RUTA_CARPETAS_BASE = r"\\Mac\Home\Desktop\Codigos\Alineamientos_Estructurales\ID_PDB_ALING"

# 4. Archivo que contiene los IDs que fallaron o están incompletos
RUTA_LISTA_FALTANTES = r"\\Mac\Home\Desktop\Codigos\Alineamientos_Estructurales\IDs_Faltantes_Gesamt.txt"

def ejecutar_alineamiento_estructural(pdb_referencia, pdb_query, id_proteina):
    """
    Ejecuta el comando real de Gesamt mediante subprocess.
    """
    dir_salida = os.path.dirname(pdb_query)
    
    # Definir rutas de salida específicas
    salida_pdb = os.path.join(dir_salida, f"{id_proteina}_superposed.pdb")
    salida_csv = os.path.join(dir_salida, f"{id_proteina}_results.csv")
    salida_txt = os.path.join(dir_salida, f"{id_proteina}_reporte.txt")

    try:
        # Construcción del comando para Gesamt
        # gesamt QUERY TARGET -o OUT_PDB -csv OUT_CSV
        comando = [
            RUTA_GESAMT,
            pdb_referencia,  # Ghrelina (Referencia)
            pdb_query,       # Proteína descargada/cortada (Target)
            "-o", salida_pdb,
            "-csv", salida_csv
        ]

        # Ejecutar y capturar salida
        resultado = subprocess.run(comando, capture_output=True, text=True)

        if resultado.returncode == 0:
            # Guardar el reporte de texto (stdout)
            with open(salida_txt, "w") as f:
                f.write(resultado.stdout)
            return True
        else:
            print(f"  [!] Error en Gesamt para {id_proteina}: {resultado.stderr}")
            return False

    except Exception as e:
        print(f"  [!] Excepción al procesar {id_proteina}: {e}")
        return False

def re_alinear_estructuras():
    # Verificaciones iniciales
    if not os.path.exists(RUTA_GESAMT):
        print(f"ERROR: No se halla gesamt.exe en: {RUTA_GESAMT}")
        return
    if not os.path.exists(RUTA_LISTA_FALTANTES):
        print(f"ERROR: No existe el archivo de faltantes: {RUTA_LISTA_FALTANTES}")
        return

    # 1. Leer los IDs faltantes
    with open(RUTA_LISTA_FALTANTES, 'r') as f:
        ids_a_procesar = [line.strip() for line in f if line.strip()]
    
    total = len(ids_a_procesar)
    if total == 0:
        print("No hay IDs para procesar en el archivo de faltantes.")
        return

    print(f"--- INICIANDO RE-ALINEAMIENTO DE {total} PROTEÍNAS CON GESAMT ---")
    print("-" * 60)

    exitos = 0
    fallos = 0

    # 2. Bucle de procesamiento
    for i, uniprot_id in enumerate(ids_a_procesar, 1):
        carpeta_id = os.path.join(RUTA_CARPETAS_BASE, uniprot_id)
        ruta_pdb_target = os.path.join(carpeta_id, f"{uniprot_id}.pdb")
        
        mensaje_progreso = f"[{i}/{total}] ID: {uniprot_id}"

        # Verificar si el PDB de la proteína existe (generado por el script de corte)
        if not os.path.exists(ruta_pdb_target):
            print(f"{mensaje_progreso} -> SALTADO (No existe el PDB base en la carpeta)")
            fallos += 1
            continue

        # Ejecutar alineamiento
        if ejecutar_alineamiento_estructural(RUTA_PDB_REFERENCIA, ruta_pdb_target, uniprot_id):
            print(f"{mensaje_progreso} -> OK (Alineamiento exitoso)")
            exitos += 1
        else:
            print(f"{mensaje_progreso} -> FALLO (Error en la ejecución)")
            fallos += 1

    print("-" * 60)
    print(f"PROCESO FINALIZADO.")
    print(f"Exitosos: {exitos} | Fallos: {fallos}")

if __name__ == "__main__":
    reintentar_alineamientos()