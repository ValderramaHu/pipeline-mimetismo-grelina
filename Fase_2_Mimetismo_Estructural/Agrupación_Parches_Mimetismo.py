#Objetivo y Fundamento
#Identificación de Motivos: El script busca segmentos donde el mimetismo no es aislado, sino continuo (ej. residuos 5, 6 y 7 de la grelina), lo que aumenta la relevancia biológica del hallazgo.
#Lógica Consecutiva: Agrupa residuos cuya posición sea $n+1$. Si la secuencia se interrumpe, el script cierra el "parche" y analiza su calidad.
#Ranking de Importancia: Clasifica los resultados priorizando los parches más largos y con la menor distancia promedio (mayor precisión geométrica).

#Resultados y Entregables
#Excel de Parches (Resultados_Parches_Mimetismo.xlsx):
#Pestaña de Ranking: Selecciona solo los mimetismos "fuertes" o "compatibles" más extensos.
#Pestaña Global: Un inventario de todos los parches detectados para trazabilidad completa.
#Métricas Detalladas: Reporta para cada grupo: rango de inicio/fin, secuencias comparadas, tamaño exacto y calidad química predominante.
#Vista Rápida: Genera un "Top 10" en la consola para identificar inmediatamente los mejores candidatos del estudio.
import pandas as pd
import os

# --- CONFIGURACIÓN DE ARCHIVOS ---
# NOTA: Usamos el archivo CSV de respaldo que se generó junto al Excel.
NOMBRE_CSV_ENTRADA = "Respaldo_Csv_Global.csv"

# Nombre del archivo Excel de salida para los parches
NOMBRE_EXCEL_SALIDA = "Resultados_Parches_Mimetismo.xlsx"

def agrupar_parches(df):
    """
    Agrupa los residuos alineados en 'parches' basados en la secuencia consecutiva
    del péptido de referencia (Ghrelina).
    """
    parches = []
    
    # Agrupar por la ID de la proteína (archivo) para procesar una a una
    for id_proteina, grupo in df.groupby("ID_Proteina"):
        
        # Ordenamos por la posición del residuo en la Ghrelina (Query)
        grupo = grupo.sort_values("Query_Num")
        
        parche_actual = []
        
        for _, row in grupo.iterrows():
            # Convertir el índice a entero para la comparación consecutiva
            try:
                # Aseguramos que Query_Num es un string antes de intentar convertirlo a int
                current_idx = int(str(row["Query_Num"])) 
            except ValueError:
                continue

            if not parche_actual:
                parche_actual = [row]
            else:
                try:
                    prev_idx = int(str(parche_actual[-1]["Query_Num"]))
                except ValueError:
                    parche_actual = [row] # Reiniciar si el anterior era inválido
                    continue
                
                # Si el residuo actual es inmediatamente consecutivo (ej. 10 y 11)
                if current_idx == prev_idx + 1:
                    parche_actual.append(row)
                else:
                    # Se rompió la secuencia, guardamos el parche anterior y empezamos uno nuevo
                    if len(parche_actual) > 1: # Solo guardamos parches de 2 o más
                        parches.append(parche_actual)
                    parche_actual = [row]
        
        # Guardar el último parche si existe y tiene más de 1 residuo
        if parche_actual and len(parche_actual) > 1:
            parches.append(parche_actual)

    # --- Resumen de Parches ---
    resumen = []
    for parche in parches:
        id_prot = parche[0]["ID_Proteina"]
        inicio = parche[0]["Query_Num"] 
        fin = parche[-1]["Query_Num"]
        
        residuos_query = [f"{p['Query_Res']}{p['Query_Num']}" for p in parche]
        residuos_target = [f"{p['Target_Res']}{p['Target_Num']}" for p in parche]
        clasificaciones = [p["Clasificacion"] for p in parche]
        
        # Clasificación predominante (la que más se repite en el parche)
        clasif_pred = max(set(clasificaciones), key=clasificaciones.count)
        tamano = len(parche)
        dist_prom = sum(p["Distancia"] for p in parche) / tamano
        
        resumen.append({
            "ID_Proteina": id_prot,
            "Inicio_Query_Num": inicio,
            "Fin_Query_Num": fin,
            "Residuos_Query": ";".join(residuos_query),
            "Residuos_Target": ";".join(residuos_target),
            "Clasificacion_Predominante": clasif_pred,
            "Tamano_Parche": tamano,
            "Distancia_Promedio": round(dist_prom, 3)
        })
        
    return pd.DataFrame(resumen)

def main():
    if not os.path.exists(NOMBRE_CSV_ENTRADA):
        print(f"Error: No se encuentra el archivo de entrada '{NOMBRE_CSV_ENTRADA}'.")
        print("Asegúrate de haber corrido antes 'analisis_quimico_excel.py' para generarlo.")
        return

    # 1. Cargar datos
    print(f"Cargando datos desde '{NOMBRE_CSV_ENTRADA}'...")
    df = pd.read_csv(NOMBRE_CSV_ENTRADA)
    
    # 2. Generar el resumen de parches
    print("Agrupando residuos en parches de mimetismo...")
    resumen_df = agrupar_parches(df)

    if resumen_df.empty:
        print("No se encontraron parches de más de un residuo.")
        return
        
    # 3. Filtrar y generar Ranking
    ranking_filtrado = resumen_df[resumen_df["Clasificacion_Predominante"].isin(["fuerte", "compatible"])]
    ranking = ranking_filtrado.sort_values(by=["Tamano_Parche", "Distancia_Promedio"], ascending=[False, True])

    # 4. Guardar en Excel con múltiples hojas
    print(f"\nGuardando archivo Excel: {NOMBRE_EXCEL_SALIDA} ...")
    
    try:
        with pd.ExcelWriter(NOMBRE_EXCEL_SALIDA, engine='openpyxl') as writer:
            
            # Hoja 1: Ranking (Parches relevantes ordenados)
            ranking.to_excel(writer, sheet_name='Ranking_Parches_Relevantes', index=False)
            
            # Hoja 2: Resumen Completo (Todos los parches encontrados)
            resumen_df.to_excel(writer, sheet_name='Resumen_Todos_los_Parches', index=False)

        print(f"✅ ¡ÉXITO! Archivo Excel creado correctamente.")
        print(f"Ubicación: {os.path.abspath(NOMBRE_EXCEL_SALIDA)}")

    except Exception as e:
        print(f"❌ Error al guardar el Excel: {e}")
        print("Asegúrate de que el archivo no esté abierto en Excel.")


    # 5. Mostrar Top 10 en consola
    print("\n--- TOP 10 PARCHES MÁS LARGOS Y RELEVANTES ---")
    if ranking.empty:
        print("No se encontraron parches con clasificación 'fuerte' o 'compatible'.")
        return
        
    for _, row in ranking.head(10).iterrows():
        print(f"ID: {row['ID_Proteina']} | Rango Query: {row['Inicio_Query_Num']}-{row['Fin_Query_Num']} "
              f"| Tamaño: {row['Tamano_Parche']} res | Clasif: {row['Clasificacion_Predominante']} "
              f"| Dist. Prom: {row['Distancia_Promedio']}")
        print(f"    Residuos Query: {row['Residuos_Query']}")
        print(f"    Residuos Target: {row['Residuos_Target']}")
        print("-" * 20)

if __name__ == "__main__":
    main()