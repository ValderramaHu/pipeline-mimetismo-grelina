# Fase 3: Análisis de Ontología y Caracterización Funcional

Esta etapa final contextualiza biológicamente a las 279 proteínas candidatas que superaron los filtros secuenciales y estructurales. Responde a la pregunta: ¿Qué rol biológico cumplen estas proteínas en la naturaleza?

## 📥 Inputs Principales
* **Lista de Candidatos Finales:** Los 279 Accession IDs validados estructuralmente en la Fase 2.
* **Secuencias FASTA:** Recuperadas mediante consulta automatizada a la API de UniProtKB.

## 🔄 Flujo de Datos
1. Las secuencias actualizadas se procesan por lotes.
2. Se utiliza el modelo de Deep Learning **DeepGOWeb** (v.1.0.26) con un *threshold* de `0.3`.
3. Se extraen predicciones para tres dominios taxonómicos: Función Molecular, Proceso Biológico y Componente Celular.
4. El motor de consolidación normaliza los términos, identifica ancestros comunes en la jerarquía de la Ontología Génica (GO) y los traduce para su interpretación.

## 📤 Outputs Principales
* **Tabla de Anotación Funcional:** Base de datos depurada que asocia cada proteína candidata con su término GO más representativo.
* **Estadísticas de Distribución:** Conteos de frecuencia funcional que permiten correlacionar el mimetismo estructural con tendencias metabólicas o de señalización celular.
