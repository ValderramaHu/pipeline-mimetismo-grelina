#Constructor de Bases de Datos Proteómicas Locales
#Objetivo y Fundamento
#Indexación de Búsqueda: Transforma archivos FASTA de texto en formatos binarios optimizados para que el algoritmo BLAST+ localice coincidencias de forma ultrarrápida.
#Automatización por Lotes: Gestiona la navegación automática entre carpetas para ejecutar el comando makeblastdb de forma masiva sin intervención manual.
#Integridad de Secuencias: Asegura que los identificadores de UniProt se conserven íntegros, permitiendo una trazabilidad precisa durante los alineamientos finales.

#Resultados y Entregables
#Archivos de Índice Binario: Genera el set de archivos técnicos (.phr, .pin, .psq) necesarios para realizar búsquedas locales por cada organismo.
#Servidor de Búsqueda Local: Convierte tu repositorio de archivos en una infraestructura de datos lista para el procesamiento intensivo sin depender de servidores externos.
#Normalización Operativa: Produce bases de datos con nombres estandarizados, garantizando que los scripts de alineamiento posteriores funcionen sin errores de ruta.
import os
import subprocess

def Fastas_Example(organism):
    # List all directories in the current location / Listar todos los directorios en la ubicación actual
    for dir in os.listdir('.'):
        if os.path.isdir(dir):
            # Change into the directory / Cambiar al directorio
            os.chdir(dir)
            
            organism_no_spaces = organism.replace(" ", "_")
            output_name = f'{organism_no_spaces}'
            input_folder = f'{organism_no_spaces}_proteins.fasta'  # Specify the name of the folder / Especificar el nombre de la carpeta
            
            # Run the BLAST command / Ejecutar el comando BLAST
            # Replace `your_fasta_file.fasta` and `your_database_name` with actual values / Reemplazar `your_fasta_file.fasta` y `your_database_name` con valores reales
            subprocess.run(['makeblastdb', '-in', input_folder, '-dbtype', 'prot', '-parse_seqids', '-out', output_name])
            
            # Return to the parent directory / Regresar al directorio principal
            os.chdir('..')

# Read the list of organisms from a file / Leer la lista de organismos desde un archivo
with open("alimentosfake.txt") as file:
    organisms = file.read().splitlines()
    
    # Process each organism / Procesar cada organismo
    for org in organisms:
        Fastas_Example(org)
