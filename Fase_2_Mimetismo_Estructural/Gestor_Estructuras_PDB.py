#Gestor de Adquisición de Estructuras de proteínas PDB´s
#Objetivo y Fundamento
#Minería de Datos Estructurales: Descarga automáticamente los archivos 3D (formato .pdb) de cientos de proteínas utilizando una lista de IDs de UniProt como entrada.
#Consulta Multifuente: Utiliza una jerarquía de búsqueda inteligente; primero consulta la base de datos de AlphaFold (modelos por IA) y, si no existe, recurre a UniProt/RCSB (estructuras experimentales).
#Organización Automatizada: Crea un sistema de carpetas ordenado y limpia los datos de entrada para evitar errores de conexión o archivos duplicados.

#Resultados y Entregables
#Repositorio PDB Organizado: Una biblioteca de estructuras lista para ser procesada por los scripts de alineamiento.
#Control de Versiones: Detecta qué archivos ya fueron descargados para ahorrar tiempo y ancho de banda en descargas masivas.
#Diagnóstico de Disponibilidad: Genera un reporte en tiempo real sobre qué proteínas cuentan con modelos estructurales y cuáles fallaron, permitiendo identificar rápidamente los casos que requerirán modelado manual o por ESMFold.
import os
import requests

def descargar_estructuras_v2(ruta_archivo_ids):
    if not os.path.exists(ruta_archivo_ids):
        print(f"Error: No se encontró el archivo en: {ruta_archivo_ids}")
        return

    directorio_base = os.path.dirname(ruta_archivo_ids)

    print("Leyendo lista de IDs...")
    try:
        with open(ruta_archivo_ids, 'r') as f:
            # .strip() elimina espacios y saltos de línea invisibles que causan errores 404
            ids_raw = [line.strip() for line in f if line.strip()]
        
        ids_unicos = sorted(list(set(ids_raw)))
        print(f"IDs únicos a procesar: {len(ids_unicos)}")
        print("-" * 40)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    for uniprot_id in ids_unicos:
        # Limpieza extra por seguridad (elimina espacios dentro del ID si los hubiera)
        uniprot_id = uniprot_id.replace(" ", "")
        
        carpeta_id = os.path.join(directorio_base, uniprot_id)
        if not os.path.exists(carpeta_id):
            os.makedirs(carpeta_id)
        
        ruta_pdb_final = os.path.join(carpeta_id, f"{uniprot_id}.pdb")

        if os.path.exists(ruta_pdb_final):
            print(f"El archivo para {uniprot_id} ya existe. Saltando.")
            continue

        # --- CAMBIO IMPORTANTE: USAR LA API ---
        # Primero preguntamos a la base de datos dónde está el archivo
        api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
        
        try:
            # 1. Obtener la información de la proteína
            api_response = requests.get(api_url)
            
            if api_response.status_code == 200:
                data = api_response.json()
                
                # AlphaFold puede devolver varios resultados. Tomamos el primero (generalmente el mejor)
                if len(data) > 0:
                    # Buscamos el enlace que termina en .pdb
                    pdb_url = data[0]['pdbUrl']
                    
                    # 2. Descargar el archivo real usando ese enlace
                    pdb_response = requests.get(pdb_url)
                    
                    if pdb_response.status_code == 200:
                        with open(ruta_pdb_final, 'w') as pdb_file:
                            pdb_file.write(pdb_response.text)
                        print(f"Formato PDB obtenido de {uniprot_id}")
                    else:
                        print(f"Error al descargar el archivo PDB desde {pdb_url}")
                else:
                    print(f"ADVERTENCIA: La API no devolvió datos para {uniprot_id}. ¿Es un ID de UniProt válido?")
            
            elif api_response.status_code == 404:
                # Si falla en AlphaFold, intentamos UNIPROT PDB Export como respaldo
                # A veces AlphaFold no tiene la proteína, pero UniProt sí tiene una estructura de referencia
                print(f"No encontrado en AlphaFold (404). Intentando respaldo (RCSB/UniProt)...")
                url_respaldo = f"https://www.uniprot.org/uniprot/{uniprot_id}.pdb"
                respaldo_response = requests.get(url_respaldo)
                
                if respaldo_response.status_code == 200:
                    with open(ruta_pdb_final, 'w') as pdb_file:
                        pdb_file.write(respaldo_response.text)
                    print(f"Formato PDB obtenido de {uniprot_id} (Vía UniProt server)")
                else:
                    print(f"FALLO TOTAL: No se pudo obtener PDB para {uniprot_id} ni en AlphaFold ni en UniProt.")
                    try:
                        os.rmdir(carpeta_id) # Borrar carpeta vacía
                    except:
                        pass
            
            else:
                print(f"Error de conexión API ({api_response.status_code}) para {uniprot_id}")

        except Exception as e:
            print(f"Excepción ocurridá con {uniprot_id}: {e}")

# --- Ejecución ---
if __name__ == "__main__":
    ruta_input = "/Users/hugoadrianjuarezvalderrama/Desktop/Codigos/AccessionEncontrados.txt"
    descargar_estructuras_v2(ruta_input)