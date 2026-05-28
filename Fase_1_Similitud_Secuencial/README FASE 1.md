# Fase 1: Análisis de Similitud Secuencial

Esta carpeta contiene los scripts responsables del tamizaje inicial. El objetivo es filtrar proteomas completos de diversos alimentos para encontrar secuencias con homología primaria a la Grelina.

## 📥 Inputs Principales
* **Lista de organismos/alimentos:** Términos de búsqueda para la consulta inicial.
* **Secuencia de consulta (Query):** Archivo FASTA con la secuencia de aminoácidos de la Grelina humana.

## 🔄 Flujo de Datos
1. `Importador_Secuencias_UniProt.py` interactúa con la API para descargar masivamente proteomas en `.fasta`.
2. `Organizador_Fastas.py` limpia la nomenclatura de los archivos.
3. `MakeBlastLocal.py` convierte los `.fasta` en bases de datos binarias (índices) para búsqueda rápida.
4. `Ejecutador_Alineamiento_Secuencial-Masivo.py` cruza la Grelina contra las bases de datos generadas usando `blastp-short`.

## 📤 Outputs Principales
* Carpetas jerárquicas por especie con sus respectivos archivos FASTA crudos y bases de datos BLAST.
* **Reporte Maestro (CSV/TXT):** Generado por `Compilador_Formatos_Alineamientos-Secuenciales.py`, contiene la lista unificada de todos los "hits" secuenciales (Accession IDs y métricas de BLAST). Este archivo es el **input directo para la Fase 2**.
