# Fase 2: Análisis Estructural y Caracterización de Mimetismo

Esta fase transfiere los candidatos secuenciales (obtenidos en la Fase 1) a un entorno tridimensional. Se evalúa si el plegamiento y la química de los residuos permiten un mimetismo espacial real con la Grelina.

## 📥 Inputs Principales
* **Reporte Maestro de la Fase 1:** Lista de Accession IDs de los candidatos.
* **Estructura Molde:** Archivo `.pdb` de la Grelina activa.

## 🔄 Flujo de Datos
1. `Gestor_Estructuras_PDB.py` descarga las estructuras experimentales disponibles.
2. `Generador_Estructuras_ESMFold.py` predice *de novo* las estructuras faltantes (región N-terminal, max 400 aa).
3. Los algoritmos de `Ejecutor...` realizan el alineamiento espacial 3D utilizando **Gesamt**.
4. Posteriormente, módulos como `Clasificador_Afinidad_Química.py` y `Agrupación_Parches_Mimetismo.py` evalúan la viabilidad bioquímica de la superposición espacial.

## 📤 Outputs Principales
* **Directorio de Estructuras:** Archivos `.pdb` (experimentales y predichos) de todas las proteínas candidatas.
* **Tabla de Métricas Estructurales:** Generada por el `Consolidador`, reporta valores de RMSD, Q-score y N_align para cada candidato.
* **Mapa de Hotspots:** Reportes tabulares y "Fingerprint Plots" que identifican las regiones más susceptibles a ser mimetizadas y su clasificación de afinidad química.
