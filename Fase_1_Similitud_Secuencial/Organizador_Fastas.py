#Organizador y Normalizador de FASTAs
#Objetivo y Fundamento
#Estandarización Técnica: Elimina espacios en los nombres de archivos para garantizar la compatibilidad con herramientas de consola (como BLAST+), donde los espacios suelen causar errores de ejecución.
#Aislamiento de Datos: Implementa la filosofía de "un organismo, una carpeta", permitiendo que cada análisis se ejecute en un espacio aislado para evitar la sobrescritura y mejorar la trazabilidad.
#Optimización de Rutas: Prepara y ubica los archivos en directorios específicos de trabajo, asegurando que los motores de búsqueda localicen las secuencias de forma inmediata y sin fallos de lectura.

#Resultados y Entregables
#Workspace Estructurado: Un árbol de directorios técnico donde cada especie posee su propia carpeta de trabajo (ej. .../BLAST+/Triticum_aestivum/).
#Archivos FASTA Sanitizados: Archivos con nomenclatura normalizada (usando guiones bajos) listos para el procesamiento por lotes.
#Sistema de Contenedores: Carpetas automatizadas que sirven como receptáculos organizados tanto para las secuencias de entrada como para los futuros reportes de alineamiento.
import os

def sin_espacios(organism):
    try:
        # File paths / Rutas de archivos
        folder = "C:/Users/lab.biomedicina/Documents/TW_Bioinformática/BLAST+"
        file = f"{folder}/{organism}_proteins.fasta"
        organism_no_spaces = organism.replace(" ", "_")
        new_name = f"{folder}/{organism_no_spaces}_proteins.fasta"

        # Rename the file / Renombrar el archivo
        os.rename(file, new_name)

        # Name of the folder to create / Nombre de la carpeta a crear
        folder_name = f"{folder}/{organism_no_spaces}"

        # Create the folder / Crear la carpeta
        os.makedirs(folder_name, exist_ok=True)

        # Move the file to the target folder / Mover el archivo a la carpeta de destino
        os.replace(new_name, f"{folder_name}/{organism_no_spaces}_proteins.fasta")

        print(f"Folder '{folder_name}' successfully created and file moved. / Carpeta '{folder_name}' creada exitosamente y archivo movido.")
   
    except Exception as e:
        print(f"Error processing the organism '{organism}': {e} / Error al procesar el organismo '{organism}': {e}")

# Read the list of organisms from a file / Leer la lista de organismos desde un archivo
with open("alimentosfake.txt") as file:
    organisms = file.read().splitlines()

# Download protein sequences for each organism / Descargar secuencias de proteínas para cada organismo
for org in organisms:
    sin_espacios(org)
