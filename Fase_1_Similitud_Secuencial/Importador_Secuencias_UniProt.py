#Adquisición Masiva de Secuencias UniProt
#Objetivo y Fundamento
#Minería Automatizada: Obtiene masivamente secuencias de proteínas mediante la API de UniProt, eliminando procesos manuales y errores de integridad.
#Robustez Técnica: Utiliza una lógica de reintento automático para superar inestabilidades de red y completar la lista de organismos de forma autónoma.
#Validación en Tiempo Real: Emplea los delimitadores del formato FASTA para contabilizar y validar estadísticamente las proteínas conforme se descargan.

#Resultados y Entregables
#Librería FASTA: Archivos individuales por organismo con sus secuencias completas de aminoácidos.
#Reportes de Control: * protein_counts.txt: Resumen tabular con el conteo exacto de proteínas por organismo.
#organisms_with_error.txt: Bitácora de fallos para depuración de nombres científicos o fuentes.
#Monitoreo de Progreso: Visualización en consola del avance porcentual de la descarga masiva.
import requests

def download_proteins_for_organism(organism, index, total_organisms):
    try:
        # Replace spaces with '+' / Reemplazar espacios con '+'
        organism_no_spaces = organism.replace(" ", "+")

        # Build the UniProt URL / Construir la URL de UniProt
        url = f"https://rest.uniprot.org/uniprotkb/stream?format=fasta&query={organism_no_spaces}"

        # Download protein information using the URL / Descargar la información de proteínas usando la URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP 4xx/5xx status codes / Generar una excepción para códigos de estado HTTP 4xx/5xx

        # Count the number of proteins in the response / Contar el número de proteínas en la respuesta
        protein_count = response.text.count(">")  # Each protein entry starts with '>' / Cada entrada de proteína comienza con '>'

        # Print organism collection message / Imprimir mensaje de recolección del organismo
        print(f"({index}/{total_organisms}) Collecting sequences for {organism} from UniProt")  

        # Save protein sequences to a file / Guardar las secuencias de proteínas en un archivo
        file_name = f"{organism}_proteins.fasta"
        with open(file_name, "w") as file:
            file.write(response.text)

        print(f"Protein sequences for {organism} have been downloaded to {file_name}. Total proteins found: {protein_count}")

        return organism, protein_count

    except requests.exceptions.RequestException as e:
        print(f"Error downloading protein sequences for {organism}: {e}")
        return organism, None

# Read the list of organisms from a file / Leer la lista de organismos desde un archivo
with open("alimentosfake.txt") as file:
    organisms = file.read().splitlines()

# Get total number of organisms / Obtener número total de organismos
total_organisms = len(organisms)

# Initialize error counter, list of errors, and total protein count / Inicializar contador de errores, lista de errores y cuenta total de proteínas
error_count = 0
organisms_with_error = []
total_proteins = 0
protein_data = {}

# Download protein sequences for each organism / Descargar secuencias de proteínas para cada organismo
index = 1  # Initialize index counter / Inicializar contador de índices
while organisms:  # Continue until there are no organisms left / Continuar hasta que no queden organismos
    for org in organisms:
        organism, protein_count = download_proteins_for_organism(org, index, total_organisms)  # Call function with index / Llamar a la función con índice
        index += 1  # Increase counter / Incrementar contador
        if protein_count is None:
            error_count += 1
            organisms_with_error.append(org)
        else:
            total_proteins += protein_count
            protein_data[organism] = protein_count

    # Update the list to retry only the failed organisms / Actualizar la lista para reintentar solo con los organismos fallidos
    organisms = organisms_with_error
    organisms_with_error = []

# Save protein count summary to a file / Guardar el resumen de conteo de proteínas en un archivo
with open("protein_counts.txt", "w") as protein_file:
    protein_file.write("Organism\tProteins Found\n")
    for organism, protein_count in protein_data.items():
        protein_file.write(f"{organism}\t{protein_count}\n")

print("\nProtein count summary saved to 'protein_counts.txt'.")

# Show error summary / Mostrar resumen de errores
if error_count > 0:
    print(f"\nThere were errors downloading sequences for {error_count} organisms:")
    for organism in organisms:
        print(f" - {organism}")

    # Save organisms with errors to a file / Guardar organismos con errores en un archivo
    with open("organisms_with_error.txt", "w") as error_file:
        for organism in organisms:
            error_file.write(organism + "\n")
    print("List of organisms with errors saved to 'organisms_with_error.txt'.")

else:
    print("\nAll sequences were successfully downloaded.")

# Show total protein count with a per-organism summary / Mostrar cuenta total de proteínas con un resumen por organismo
print("\nSummary of proteins found per organism:")
for organism, protein_count in protein_data.items():
    print(f"{organism}: {protein_count} proteins found")

print(f"\nTotal number of proteins found across all organisms: {total_proteins}")
