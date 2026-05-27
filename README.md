# Pipeline Bioinformático para la Identificación de Proteínas Alimentarias Miméticas a la Grelina

> Pipeline bioinformático automatizado en Python para identificar y caracterizar proteínas alimentarias con mimetismo molecular a la hormona Grelina. Integra análisis masivo de similitud secuencial (BLAST), superposición estructural 3D (Gesamt/ESMFold) y anotación funcional (DeepGO).

## 📋 Descripción del Proyecto
Este repositorio contiene el código fuente para el tamizaje y análisis bioinformático de 279 proteínas candidatas. El pipeline está diseñado para operar en tres fases consecutivas, permitiendo llevar el análisis desde secuencias primarias crudas hasta la validación de complementariedad química y el mapeo de ontología génica.

## 🛠️ Tecnologías y Requisitos
* **Lenguajes:** Python 3.x, R (para visualización con `ggplot2`)
* **Dependencias Principales:** `Biopython`, `pandas`, `requests` (API UniProt/PDB)
* **Software Externo Requerido:** BLAST+ local, algoritmo Gesamt, acceso al servidor DeepGOWeb.

## 🚀 Arquitectura del Pipeline

### Fase 1: Análisis de Similitud Secuencial
Descarga y generación de bases de datos locales para el filtrado inicial.
* `Importador_Secuencias_UniProt.py`
* `Organizador_Fastas.py`
* `MakeBlastLocal.py`
* `Ejecutador_Alineamiento_Secuencial-Masivo.py`
* `Compilador_Formatos_Alineamientos-Secuenciales.py`

### Fase 2: Análisis Estructural y Caracterización de Mimetismo
Validación tridimensional del mimetismo y evaluación de viabilidad fisicoquímica.
* `Gestor_Estructuras_PDB.py` / `Generador_Estructuras_ESMFold.py`
* `Verificador_Resultados-Faltantes.py`
* `Ejecutor_Alineamiento_Estructural-Masivo.py` / `Reintentar_Alineamientos-Estructural_Masivo.py`
* `Clasificador_Afinidad_Química.py`
* `Agrupación_Parches_Mimetismo.py`

### Fase 3: Análisis de Ontología y Caracterización Funcional
Recuperación y normalización de funciones moleculares y procesos biológicos.
* `Predicción Funciones_Deepgo.py`
Interacción con API UniProtKB.
Procesamiento batch en DeepGOWeb (v.1.0.26, threshold: 0.3).

## ⚙️ Instrucciones de Uso (Ejemplo)
1. Clonar este repositorio:
   ```bash
   git clone [https://github.com/TuUsuario/pipeline-mimetismo-grelina.git](https://github.com/TuUsuario/pipeline-mimetismo-grelina.git)

2. Ejecutar los scripts en orden secuencial por fases, asegurando que los directorios de output de la Fase 1 sirvan como input para la Fase 2.

✒️ Autores  
Hugo Adrian Juarez Valderrama - Investigación de Licenciatura  
Daniela Gómez Medina - Investigación de Licenciatura  
Victor Ignacio Mendoza Hernández - Investigación de Licenciatura

📄 Licencia
Este proyecto está bajo la Licencia MIT - mira el archivo LICENSE para detalles.
   
