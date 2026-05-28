#Ejecutor de Alineamiento Estructural Masivo
#Objetivo y Fundamento
#Alineamiento Estructural por IA: Automatiza el software Gesamt para comparar tridimensionalmente 353 proteínas contra el molde de la Grelina Alpha 28.
#Superposición Espacial: Su función es mover y rotar cada proteína en el espacio 3D hasta encontrar el punto donde sus átomos coinciden mejor con la Grelina, permitiendo identificar mimetismos estructurales.
#Optimización de Flujo: Incluye una función de "memoria" que detecta archivos ya procesados para no repetir el trabajo, permitiendo retomar el análisis en caso de interrupciones.

#Resultados y Entregables
#El script organiza automáticamente tres archivos clave por cada proteína en su carpeta correspondiente:
#Coordenadas Alineadas (_superposed.pdb): La estructura lista para ser visualizada en programas como PyMOL o Chimera.
#Matriz de Datos (_results.csv): La tabla técnica que indica qué aminoácido de la Grelina se "toca" con la proteína analizada (base para los scripts químicos).
#Reporte de Métricas (_reporte.txt): El documento que contiene el RMSD y el Q-score, valores que demuestran científicamente si el parecido es real o casual.
import os
import subprocess
import time

# --- CONFIGURACIÓN DE RUTAS (VERIFICA ESTO) ---

# 1. Ruta al ejecutable de Gesamt (Tal cual la enviaste)
RUTA_GESAMT = r"C:\Program Files (x86)\CCP4MG\pythondist\Lib\site-packages\ccp4mg\CCP4\bin\gesamt.exe"

# 2. Ruta a tu archivo QUERY (Ghrelina)
# Nota: Si estás en Parallels, asegúrate que esta ruta sea accesible desde Windows
RUTA_QUERY = r"C:\Mac\Home\Desktop\GHRELIN_alpha28.pdb"

# 3. Ruta a la CARPETA MADRE donde están las 353 carpetas de proteínas
# IMPORTANTE: He convertido tu ruta de Mac a formato Windows de Parallels/VM.
# Si falla, cámbiala por la ruta que Windows usa para ver esa carpeta (ej. Z:\Users\...)
RUTA_CARPETAS = r"\\Mac\Home\Desktop\Codigos\Alineamientos_Estructurales\ID_PDB_ALING"

def realizar_alineamientos():
    # Verificar que el ejecutable y el query existan antes de empezar
    if not os.path.exists(RUTA_GESAMT):
        print(f"ERROR CRÍTICO: No se encuentra gesamt.exe en: {RUTA_GESAMT}")
        return
    if not os.path.exists(RUTA_QUERY):
        print(f"ERROR CRÍTICO: No se encuentra el archivo Ghrelina en: {RUTA_QUERY}")
        return
    if not os.path.exists(RUTA_CARPETAS):
        print(f"ERROR CRÍTICO: No se encuentra la carpeta de alineamientos en: {RUTA_CARPETAS}")
        return

    print("--- INICIANDO PROCESO DE ALINEAMIENTO MASIVO ---")
    print(f"Ejecutable: Gesamt")
    print(f"Query: Ghrelina Alpha 28")
    print("-" * 50)

    # Obtener lista de carpetas (IDs)
    try:
        entradas = os.listdir(RUTA_CARPETAS)
        # Filtramos para quedarnos solo con carpetas
        lista_ids = [d for d in entradas if os.path.isdir(os.path.join(RUTA_CARPETAS, d))]
        total_proteinas = len(lista_ids)
        
        print(f"Se encontraron {total_proteinas} carpetas para procesar.")
        time.sleep(2) # Pausa breve para leer

    except Exception as e:
        print(f"Error al leer el directorio: {e}")
        return

    # Contadores
    exitos = 0
    errores = 0

    # BUCLE PRINCIPAL
    for i, id_proteina in enumerate(lista_ids, 1):
        
        # Definir rutas específicas para esta iteración
        dir_actual = os.path.join(RUTA_CARPETAS, id_proteina)
        archivo_target = os.path.join(dir_actual, f"{id_proteina}.pdb")
        
        # Archivos de salida
        salida_pdb = os.path.join(dir_actual, f"{id_proteina}_superposed.pdb")
        salida_csv = os.path.join(dir_actual, f"{id_proteina}_results.csv")
        salida_txt = os.path.join(dir_actual, f"{id_proteina}_reporte.txt") # Para guardar el RMSD/Texto

        # Mensaje de progreso en terminal
        mensaje_progreso = f"[{i}/{total_proteinas}] ID: {id_proteina}"
        
        # Verificar si existe el PDB objetivo
        if not os.path.exists(archivo_target):
            print(f"{mensaje_progreso} -> SALTADO (No existe el archivo .pdb)")
            errores += 1
            continue

        # Verificar si YA se hizo (para no repetir trabajo si reinicias el script)
        if os.path.exists(salida_pdb) and os.path.exists(salida_csv):
            print(f"{mensaje_progreso} -> YA EXISTE (Saltando...)")
            exitos += 1
            continue

        try:
            # Construcción del comando para subprocess (maneja espacios en rutas automáticamente)
            # Estructura: gesamt QUERY TARGET -o OUT_PDB -csv OUT_CSV
            comando = [
                RUTA_GESAMT,
                RUTA_QUERY,
                archivo_target,
                "-o", salida_pdb,
                "-csv", salida_csv
            ]

            # Ejecutar comando y capturar la salida de texto (stdout)
            resultado = subprocess.run(comando, capture_output=True, text=True)

            if resultado.returncode == 0:
                # Guardar el reporte de texto (donde viene el RMSD y Q-score explicado)
                with open(salida_txt, "w") as f:
                    f.write(resultado.stdout)
                
                print(f"{mensaje_progreso} -> LISTO (Alineamiento completado)")
                exitos += 1
            else:
                print(f"{mensaje_progreso} -> ERROR al ejecutar gesamt")
                print(resultado.stderr) # Mostrar error si hubo
                errores += 1

        except Exception as e:
            print(f"{mensaje_progreso} -> EXCEPCIÓN DE PYTHON: {e}")
            errores += 1

    print("-" * 50)
    print(f"PROCESO TERMINADO.")
    print(f"Exitosos: {exitos}")
    print(f"Errores/Faltantes: {errores}")

if __name__ == "__main__":
    realizar_alineamientos()