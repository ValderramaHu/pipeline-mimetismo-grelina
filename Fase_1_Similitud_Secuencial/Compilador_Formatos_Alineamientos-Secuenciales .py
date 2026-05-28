#Compilador de Alineamientos de secuencias, información resumida, Unir formatos
#Objetivo y Fundamento
#Integración de Resultados: Resuelve la fragmentación de datos al consolidar cientos de archivos dispersos en un solo documento maestro, facilitando una "vista de pájaro" de todo el experimento.
#Facilitación de la Curación Manual: Se enfoca en el Formato 0 (alineamiento por pares), el cual es vital para inspeccionar visualmente barras de identidad, similitudes y huecos (gaps) entre la Grelina y los candidatos.
#Trazabilidad Técnica: Utiliza una lógica de etiquetado por encabezados para vincular inequívocamente cada bloque de resultados con su organismo y carpeta de origen, evitando confusiones en el análisis masivo.

#Resultados y Entregables
#Reporte Maestro Unificado (all_format0_results.txt): Un archivo único y ligero que contiene la totalidad de los alineamientos, optimizado para búsquedas globales (Ctrl + F) de motivos conservados.
#Auditoría de Integridad: Reporta automáticamente dentro del documento si algún organismo carece de resultados o si su carpeta no fue localizada, actuando como un último filtro de control de calidad.
#Estructura de Lectura Rápida: Presenta un formato estandarizado con separadores visuales claros, transformando miles de líneas de datos técnicos en un documento navegable y organizado.
import os

# Nombre del archivo que contiene la lista de organismos / File containing the list of organisms
input_filename = "alimentosfake.txt"

# Nombre del archivo de salida unificado / Unified output filename
unified_filename = "all_format0_results.txt"

# Leer la lista de organismos desde un archivo / Read the list of organisms from a file
with open(input_filename) as f:
    organisms = f.read().splitlines()

# Abrir el archivo de salida en modo escritura / Open the output file for writing
with open(unified_filename, "w") as out_file:
    for organism in organisms:
        organism_without_spaces = organism.replace(" ", "_")
        folder = organism_without_spaces
        # Se asume que el archivo formato 0 se llama: "Resultados_Evalue10_{organism_without_spaces}_Fmt0.txt"
        result_filename = f"Resultados_Evalue10_{organism_without_spaces}_Fmt0.txt"
        full_path = os.path.join(folder, result_filename)
        
        out_file.write("-----------------------------------------------------------------\n")
        out_file.write(f"Results for {organism} (Folder: {folder})\n")
        out_file.write("-----------------------------------------------------------------\n")
        
        if os.path.isdir(folder):
            if os.path.isfile(full_path):
                with open(full_path, "r") as result_file:
                    content = result_file.read()
                    out_file.write(content)
                    out_file.write("\n\n")
            else:
                out_file.write("Result file not found for this organism.\n\n")
        else:
            out_file.write("Folder not found for this organism.\n\n")

print(f"Unified format 0 results saved to {unified_filename}.")
