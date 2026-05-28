#Gestor de Alineamiento Secuencial de Péptidos Cortos
#Objetivo y Fundamento
#Optimización para Péptidos: Utiliza la tarea específica blastp-short para ajustar los parámetros de búsqueda a la longitud de la Grelina (28 aa), evitando que el algoritmo ignore coincidencias pequeñas pero biológicamente significativas.
#Máxima Sensibilidad: Emplea un umbral de significancia estadística ($E$-value) de 10, permitiendo capturar un espectro amplio de posibles candidatos miméticos, desde coincidencias fuertes hasta sutiles.
#Procesamiento Multi-formato: Ejecuta cada análisis en tres formatos simultáneos (0, 4 y 7) para facilitar tanto la inspección visual humana como la extracción de datos automatizada mediante código.

#Resultados y Entregables
#Triada de Reportes Técnicos: Por cada organismo, se generan archivos de resultados en formato visual (Fmt 0), anclado (Fmt 4) y tabular (Fmt 7), almacenados de forma organizada en sus carpetas correspondientes.
#Cuantificación de "Hits": Un conteo dinámico en tiempo real de cuántas coincidencias se han encontrado en todo el universo de proteínas analizadas.
#Resumen Maestro (alignment_summary_Evalue10.txt): Un documento consolidado que funciona como el "mapa de ruta" final, detallando qué organismos son más ricos en fragmentos miméticos y cuáles no presentaron resultados.
import os
import subprocess

# Cumulative alignment counter / Contador acumulativo de alineamientos
total_hits = 0

def Fastas_Example(organism, index, total_organisms):
    global total_hits  # Using a global variable to accumulate hits / Usar una variable global para acumular hits
    organism_without_spaces = organism.replace(" ", "_")
    output_name = f'{organism_without_spaces}'

    if os.path.isdir(output_name):
        os.chdir(output_name)
        
        formats = ['0', '4', '7']  # Using three formats / Usando los tres formatos
        hit_counts = {}
        alignment_successful = True  # Flag to track successful alignments / Bandera para verificar éxito

        for fmt in formats:
            output_filename = f'Resultados_Evalue10_{organism_without_spaces}_Fmt{fmt}.txt'
            result = subprocess.run(
                ['blastp', '-task', 'blastp-short', '-query', '../Ghrelin.fasta', '-db', output_name, '-evalue', '10', '-out', output_filename, '-outfmt', fmt],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                alignment_successful = False  # If any format fails, mark as unsuccessful / Si algún formato falla, marcar como no exitoso

            # Counting hits only for format 7 / Contar hits solo en formato 7
            if fmt == '7' and result.returncode == 0:
                with open(output_filename) as f:
                    hits = sum(1 for line in f if not line.startswith('#'))
                hit_counts[organism] = hits
                total_hits += hits  # Accumulate hits / Acumular hits

        if alignment_successful:
            print(f"({index}/{total_organisms}) Alignments successfully completed for {organism} in formats 0, 4, and 7.")  # Added alignment counter / Se agregó el contador de alineación
            if organism in hit_counts:
                print(f"Successful alignments for {organism}: {hit_counts[organism]} hits. Total accumulated: {total_hits} hits.")
        else:
            print(f"Alignment error for {organism} in one or more formats.")

        os.chdir('..')
        return hit_counts if alignment_successful else False
    else:
        print(f"The folder {output_name} does not exist.")
        return False

# Read the list of organisms from a file / Leer la lista de organismos desde un archivo
with open("alimentosfake.txt") as file:
    organisms = file.read().splitlines()

# Get total number of organisms / Obtener número total de organismos
total_organisms = len(organisms)

# Initialize dictionaries for tracking results / Inicializar diccionarios para rastrear resultados
successful_organisms = {}
failed_organisms = []

# Process each organism / Procesar cada organismo
index = 1  # Initialize index counter / Inicializar contador de índices
for org in organisms:
    result = Fastas_Example(org, index, total_organisms)  # Pass index and total organisms / Pasar el índice y el total de organismos
    index += 1  # Increase counter / Incrementar contador
    if result:
        successful_organisms.update(result)
    else:
        failed_organisms.append(org)

# Build the summary string / Construir la cadena resumen
summary_str = "Alignment Summary\n\n"

summary_str += "Organisms with successful alignments:\n"
for org, hits in successful_organisms.items():
    summary_str += f" - {org}: {hits} hits\n"

summary_str += "\nOrganisms with alignment errors:\n"
for org in failed_organisms:
    summary_str += f" - {org}\n"

summary_str += f"\nTotal alignments obtained across all organisms: {total_hits} hits:\n"

# Display summary on screen / Mostrar resumen en pantalla
print("\n" + summary_str)

# Save summary to a file / Guardar resumen en un archivo
summary_filename = "alignment_summary_Evalue10.txt"
with open(summary_filename, "w") as summary_file:
    summary_file.write(summary_str)

print(f"Alignment summary saved to {summary_filename}.")
