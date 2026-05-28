#Clasificador de Afinidad Química y Mimetismo Molecular
#Objetivo y Fundamento
#Interpretación de la Complementariedad Química: El script no solo mira qué tan cerca están los aminoácidos, sino si sus "personalidades" químicas coinciden. Clasifica los residuos en 5 grupos fundamentales: Positivos, Negativos, Polares, Hidrofóbicos y Aromáticos.
#Lógica de Clasificación de Pares: Establece una jerarquía de mimetismo basada en la probabilidad de mantener interacciones similares a las de la Grelina:
#Fuerte: Los dos aminoácidos pertenecen a la misma clase química (ej. un aminoácido cargado positivamente en la Grelina coincide con uno cargado positivamente en la proteína objetivo).
#Compatible: Combinaciones con lógica fisicoquímica (ej. un residuo cargado con uno polar, o un aromático con un hidrofóbico).
#Débil/No Relevante: Combinaciones que probablemente no mantendrían la misma función biológica.
#Criterio de Proximidad Espacial: Aplica un filtro estricto de 3.5 A. Este es el fundamento de los enlaces no covalentes y las interacciones de contacto; cualquier residuo más alejado se descarta para evitar falsos positivos.

#Resultados y Entregables
#Dataset Maestro de Mimetismo (Resultados_Mimetismo_Global_v2.xlsx):
#Resumen_Clasificacion: Un censo estadístico que cuantifica cuántos pares "Fuertes" y "Compatibles" se encontraron en todo el estudio.
#Detalle_Completo: Una hoja de cálculo exhaustiva que desglosa cada par alineado, su distancia exacta en Ångströms, sus clases químicas y su clasificación final.
#Top_Proteinas_Fuerte: Un ranking de los mejores candidatos basado estrictamente en la cantidad de interacciones de mimetismo "Fuerte".
#Reporte de Interpretación Automática: El script imprime directamente en la consola un análisis técnico que resume el porcentaje de relevancia del estudio e identifica al candidato más prometedor para futuros estudios de dinámica molecular o modelado 3D.
#Archivo de Respaldo (Respaldo_Csv_Global.csv): Un archivo ligero diseñado para ser procesado rápidamente por otros scripts (como el generador de parches o el de huellas digitales).
import os
import pandas as pd
import glob
import time

# --- CONFIGURACIÓN DE RUTAS ---
RUTA_CARPETAS_BASE = r"\\Mac\Home\Desktop\Codigos\Alineamientos_Estructurales\ID_PDB_ALING"
DIST_MAX = 3.5
NOMBRE_EXCEL = "Resultados_Mimetismo_Global_v2.xlsx" # Nuevo nombre para evitar sobrescribir

# --- LÓGICA DE CLASIFICACIÓN QUÍMICA ---
POS = {"LYS","ARG","HIS"}
NEG = {"ASP","GLU"}
POL = {"SER","THR","ASN","GLN","CYS"}
HYD = {"ALA","VAL","LEU","ILE","MET","PRO"}
ARO = {"PHE","TYR","TRP"}

def clase_residuo(res: str) -> str:
    r = res.upper().replace("A:", "").strip()
    if r in POS: return "positivo"
    if r in NEG: return "negativo"
    if r in POL: return "polar"
    if r in HYD: return "hidrofóbico"
    if r in ARO: return "aromático"
    return "otro"

def clasificacion_par(qclass, tclass):
    if qclass == tclass and qclass != "otro":
        return "fuerte"
    compatibles = {
        ("positivo","polar"), ("polar","positivo"),
        ("negativo","polar"), ("polar","negativo"),
        ("aromático","hidrofóbico"), ("hidrofóbico","aromático")
    }
    if (qclass,tclass) in compatibles:
        return "compatible"
    return "débil/no relevante"

# --- PROCESAMIENTO CSV ---

def procesar_archivo_csv_gesamt(ruta_archivo, id_proteina):
    # ... (La lógica de procesamiento de CSV se mantiene igual) ...
    resultados_locales = []
    if not os.path.exists(ruta_archivo):
        return []

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "Dist" in line: continue
                
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 5: continue

            try:
                dist = float(parts[0])
                if dist > DIST_MAX: continue

                query_parts = parts[3].split()
                target_parts = parts[4].split()

                if len(query_parts) < 2 or len(target_parts) < 2: continue

                qres_raw = query_parts[1] if len(query_parts) >= 2 else query_parts[0]
                tres_raw = target_parts[1] if len(target_parts) >= 2 else target_parts[0]
                
                try:
                    qidx = query_parts[-1]
                    tidx = target_parts[-1]
                except:
                    qidx = "?"
                    tidx = "?"

                qclass = clase_residuo(qres_raw)
                tclass = clase_residuo(tres_raw)
                clasif = clasificacion_par(qclass, tclass)

                # Nombres de columna más descriptivos para el DataFrame
                resultados_locales.append({
                    "ID_Proteina": id_proteina,
                    "Distancia_Angstrom": round(dist, 3), # Nombre más claro para la distancia
                    "Residuo_Query": qres_raw.replace("A:", ""),
                    "Num_Residuo_Query": qidx,
                    "Clase_Quimica_Query": qclass,
                    "Residuo_Target": tres_raw.replace("A:", ""),
                    "Num_Residuo_Target": tidx,
                    "Clase_Quimica_Target": tclass,
                    "Clasificacion_Mimetismo": clasif
                })

            except ValueError:
                continue
            except Exception:
                continue

    return resultados_locales

# --- FUNCIÓN DE INTERPRETACIÓN ---
def generar_reporte_interpretacion(df, resumen_df):
    """Genera la descripción analítica de los resultados."""
    print("\n" + "="*80)
    print("🔬 ANÁLISIS DE RESULTADOS: MIMETISMO QUÍMICO-ESTRUCTURAL")
    print("="*80)

    total_pares = len(df)
    total_proteinas = df["ID_Proteina"].nunique()
    
    # Obtener el total de pares "Fuerte" y "Compatible"
    pares_fuertes = resumen_df[resumen_df["Tipo_Mimetismo"] == "fuerte"]["Cantidad_de_Pares_Alineados"].sum()
    pares_compatibles = resumen_df[resumen_df["Tipo_Mimetismo"] == "compatible"]["Cantidad_de_Pares_Alineados"].sum()
    total_relevante = pares_fuertes + pares_compatibles
    
    # Identificar la proteína con más mimetismos 'fuerte'
    top_prot = df[df["Clasificacion_Mimetismo"] == "fuerte"]["ID_Proteina"].value_counts().head(1)
    
    print(f"## 📊 Lo que se obtiene:")
    print(f"* **El resultado principal es una tabla (Detalle_Completo en Excel)** que consolida todos los pares de aminoácidos alineados estructuralmente (distancia <= {DIST_MAX} Å) de las {total_proteinas} proteínas analizadas.")
    print(f"* **Cada par** está clasificado según su similitud química (Fuerte, Compatible o Débil/No Relevante).")
    print(f"* **Se obtiene un resumen estadístico** de la distribución de estas clasificaciones y un ranking de las proteínas más miméticas (Top_Proteinas).")

    print(f"\n## 🎯 Importancia de los Resultados:")
    print(f"* **El Mimetismo Molecular** (similitud estructural y química) es clave para identificar análogos funcionales.")
    print(f"* **Clasificación 'Fuerte':** Ocurre cuando un residuo de la Ghrelina (ej. un LYS) se alinea espacialmente con otro de la misma clase química (ej. LYS, ARG, HIS en el target). Esto sugiere una alta probabilidad de mantener una interacción molecular similar.")
    print(f"* **Clasificación 'Compatible':** Ocurre en combinaciones plausibles (ej. Positivo/Polar o Aromático/Hidrofóbico). Sugiere que la función puede ser imitada, aunque la identidad química sea diferente.")
    print(f"* **Filtro Espacial ({DIST_MAX} Å):** Garantiza que solo analizamos residuos que están en contacto o muy cercanos en el alineamiento, eliminando coincidencias triviales.")
    
    print(f"\n## 📈 Resumen Estadístico Clave:")
    print(f"* **Total de Pares Alineados (Relevantes):** {total_pares} pares.")
    print(f"* **Pares con Mimetismo Relevante (Fuerte + Compatible):** {total_relevante} pares.")
    print(f"* **Porcentaje de Relevancia:** {round((total_relevante / total_pares) * 100, 2)}%")

    if not top_prot.empty:
        id_top = top_prot.index[0]
        conteo_top = top_prot.values[0]
        print(f"* **La proteína más mimética (Top ID):** {id_top} con {conteo_top} pares de mimetismo 'fuerte'. Este es el mejor candidato para un análisis detallado 3D.")
        
    print("="*80)

def main():
    print("--- INICIANDO ANÁLISIS (SALIDA EN EXCEL V2) ---")
    
    todos_los_datos = []
    
    if not os.path.exists(RUTA_CARPETAS_BASE):
        print("Error: No existe la ruta base.")
        return

    carpetas = [d for d in os.listdir(RUTA_CARPETAS_BASE) if os.path.isdir(os.path.join(RUTA_CARPETAS_BASE, d))]
    total_carpetas = len(carpetas)
    
    print(f"Procesando {total_carpetas} carpetas...")

    archivos_procesados = 0
    for i, id_prot in enumerate(carpetas, 1):
        ruta_csv = os.path.join(RUTA_CARPETAS_BASE, id_prot, f"{id_prot}_results.csv")
        
        if os.path.exists(ruta_csv):
            if i % 50 == 0: print(f"[{i}/{total_carpetas}] ...")
            datos_prot = procesar_archivo_csv_gesamt(ruta_csv, id_prot)
            todos_los_datos.extend(datos_prot)
            archivos_procesados += 1

    # Crear DataFrame Principal
    df = pd.DataFrame(todos_los_datos)
    
    if df.empty:
        print("No se encontraron datos.")
        return

    # Crear DataFrame de Resumen (Ajustando columna para la claridad)
    resumen = df["Clasificacion_Mimetismo"].value_counts().reset_index()
    resumen.columns = ["Tipo_Mimetismo", "Cantidad_de_Pares_Alineados"] # Encabezado mejorado

    # --- GUARDAR EN EXCEL ---
    print(f"\nGuardando archivo Excel: {NOMBRE_EXCEL} ...")
    
    try:
        with pd.ExcelWriter(NOMBRE_EXCEL, engine='openpyxl') as writer:
            
            # Hoja 1: Resumen
            resumen.to_excel(writer, sheet_name='Resumen_Clasificacion', index=False)
            
            # Hoja 2: Detalle Completo (Con encabezados mejorados)
            df.to_excel(writer, sheet_name='Detalle_Completo', index=False)
            
            # Hoja 3: Ranking (Bonus)
            try:
                ranking = df[df["Clasificacion_Mimetismo"] == "fuerte"]["ID_Proteina"].value_counts().reset_index()
                ranking.columns = ["ID_Proteina", "Total_Pares_Fuerte"] # Encabezado mejorado
                ranking.head(50).to_excel(writer, sheet_name='Top_Proteinas_Fuerte', index=False)
            except:
                pass

        print(f"✅ ¡ÉXITO! Archivo Excel creado correctamente.")
        print(f"Ubicación: {os.path.abspath(NOMBRE_EXCEL)}")
        
        # Guardamos el CSV de respaldo con los nombres de columna nuevos
        df.to_csv("Respaldo_Csv_Global.csv", index=False)
        print("   (También se generó o actualizó un respaldo CSV)")

    except Exception as e:
        print(f"❌ Error al guardar el Excel: {e}")
        print("Asegúrate de que el archivo no esté abierto en Excel.")

    # 4. Generar el reporte de interpretación
    generar_reporte_interpretacion(df, resumen)


if __name__ == "__main__":
    main()