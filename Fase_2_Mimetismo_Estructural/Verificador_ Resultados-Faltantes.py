#Verificador de resultados y archivos de alineamientos estructurales
#Objetivo y Fundamento
#Control de Calidad del Workflow: El script tiene como objetivo principal realizar un barrido exhaustivo en el sistema de archivos para confirmar que cada proteína analizada cuente con su "triada de resultados" completa.
#Fundamento de Validación Cruzada: Se basa en la verificación de tres archivos críticos que representan las diferentes fases del análisis estructural:
#Geometría: Presencia del archivo .pdb superpuesto.
#Métricas: Disponibilidad del archivo .csv con los datos numéricos.
#Validación Técnica: Existencia del reporte .txt generado por el motor de alineamiento.
#Detección de Archivos Corruptos: No solo verifica que el archivo exista, sino que comprueba que su tamaño sea mayor a 0 KB, filtrando ejecuciones que fallaron silenciosamente o archivos dañados durante la transferencia de datos.

#Resultados y Entregables
#Reporte de Omisiones (IDs_Faltantes_Final.txt): Genera automáticamente una "lista negra" de IDs que requieren atención. 
#Cuadro de Mando del Proyecto: Imprime en consola un resumen estadístico de alto nivel:
#Total de Proteínas: El universo completo del estudio.
#Éxitos Confirmados: Cantidad de candidatos con datos robustos para el reporte final.
#Pendientes/Fallidos: El margen de error que aún debe ser gestionado.
#Certificación de Estatus: Si todas las carpetas están correctas, el script elimina automáticamente las listas de faltantes anteriores, certificando que el proyecto está listo para la fase de redacción y publicación.
import os
import time

# --- CONFIGURACIÓN DE RUTAS ---

# Ruta a la CARPETA MADRE donde están todas las carpetas de IDs
RUTA_CARPETAS_BASE = r"\\Mac\Home\Desktop\Codigos\Alineamientos_Estructurales\ID_PDB_ALING"

# Nombre del archivo de salida donde se guardarán los IDs que aún estén faltantes
NOMBRE_ARCHIVO_SALIDA = "IDs_Faltantes_Final.txt"

# Lista de extensiones de archivos que *deben* estar presentes (resultados de Gesamt)
EXTENSIONES_REQUERIDAS = [
    "_superposed.pdb", # Archivo de la estructura superpuesta
    "_results.csv",  # Archivo CSV con las métricas
    "_reporte.txt"   # Archivo TXT con el reporte de terminal
]

def verificar_archivos_faltantes():
    if not os.path.exists(RUTA_CARPETAS_BASE):
        print(f"Error: No se encuentra la carpeta de resultados en: {RUTA_CARPETAS_BASE}")
        return

    ids_incompletos = []
    
    # Obtener lista de carpetas (IDs)
    try:
        entradas = os.listdir(RUTA_CARPETAS_BASE)
        lista_ids = [d for d in entradas if os.path.isdir(os.path.join(RUTA_CARPETAS_BASE, d))]
        total_proteinas = len(lista_ids)
        print(f"--- INICIANDO VERIFICACIÓN FINAL ---")
        print(f"Verificando {total_proteinas} carpetas...")
        print("-" * 50)
    except Exception as e:
        print(f"Error al leer el directorio: {e}")
        return

    # Contadores para el resumen final
    completos = 0
    incompletos = 0

    # BUCLE PRINCIPAL DE VERIFICACIÓN
    for i, id_proteina in enumerate(lista_ids, 1):
        
        dir_actual = os.path.join(RUTA_CARPETAS_BASE, id_proteina)
        
        faltantes = []
        
        # 1. Verificar la existencia de cada archivo de resultado
        for extension in EXTENSIONES_REQUERIDAS:
            nombre_archivo = f"{id_proteina}{extension}"
            ruta_archivo = os.path.join(dir_actual, nombre_archivo)
            
            if not os.path.exists(ruta_archivo) or os.path.getsize(ruta_archivo) == 0:
                faltantes.append(nombre_archivo)
        
        # 2. Registrar los IDs con resultados incompletos
        if faltantes:
            ids_incompletos.append(id_proteina)
            incompletos += 1
            print(f"[{i}/{total_proteinas}] ID: {id_proteina} -> ⚠️ INCOMPLETO (Faltan: {', '.join(faltantes)})")
        else:
            completos += 1
            # Imprimimos el progreso de los que están OK
            if i % 50 == 0 or i == total_proteinas:
                print(f"[{i}/{total_proteinas}] ID: {id_proteina} -> OK")

    # 3. Guardar la lista de IDs incompletos en un archivo de texto
    ruta_salida_txt = os.path.join(os.path.dirname(RUTA_CARPETAS_BASE), NOMBRE_ARCHIVO_SALIDA)

    if ids_incompletos:
        with open(ruta_salida_txt, 'w') as f:
            for id_faltante in ids_incompletos:
                f.write(f"{id_faltante}\n")
                
        print("-" * 50)
        print(f"⚠️ VERIFICACIÓN TERMINADA. Se encontraron {len(ids_incompletos)} IDs incompletos.")
        print(f"La lista final de IDs pendientes fue guardada en:")
        print(f"-> {ruta_salida_txt}")
    else:
        # Si el archivo existe de una corrida anterior, lo borramos
        if os.path.exists(ruta_salida_txt):
             os.remove(ruta_salida_txt)
        print("-" * 50)
        print("✅ VERIFICACIÓN TERMINADA. ¡Todos los IDs tienen sus resultados completos!")

    # Resumen general del proyecto
    print("\n--- RESUMEN FINAL DEL PROYECTO ---")
    print(f"Total de Proteínas en Proyecto: {total_proteinas}")
    print(f"Procesos Completados con Éxito: {completos}")
    print(f"Pendientes/Fallidos Definitivos: {incompletos}")


# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    verificar_archivos_faltantes()