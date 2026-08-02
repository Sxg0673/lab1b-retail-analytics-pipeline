# Lab 1B – ETL Pipeline: Plataforma de Analítica de Retail

**Curso:** ETL (G01) — Facultad de Ingeniería y Ciencias Básicas
**Integrantes:** Santiago Castillo Martinez, Valeria Jiménez Bedoya

> Este README se completa progresivamente a medida que se desarrollan las actividades del taller.

## 1. Project Overview
<!-- Breve descripción del proyecto: qué problema de negocio resuelve, qué hace el pipeline. -->

## 2. System Architecture (Pipeline Diagram)
<!-- Insertar aquí el diagrama de bloques (docs/pipeline_diagram.png) y una breve explicación del flujo. -->

## 3. Selected Business Requirements
<!-- Tabla con los 6 requisitos priorizados (Activity 1), tomados de Lab 1A. -->

## 4. ETL Pipeline Description
<!-- Descripción de cada bloque: Extract, Profile, Clean/Harmonize, Transform/Integrate, Validate, Load, Query. -->

## 5. Project Structure
```
Lab1B_ETL/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
│
├── database/
│   └── retail_analytics.db
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── queries.py
│   └── main.py
│
├── docs/
│   └── pipeline_diagram.png
│
├── README.md
├── requirements.txt
└── .gitignore
```

## 6. Execution Instructions
```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd Lab1B_ETL

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el pipeline completo
python src/main.py
```

## 7. Technologies Used
- Python 3.x
- pandas
- sqlite3
- (agregar el resto a medida que se usen: json, xml.etree, etc.)

## 8. Example Analytical Results
<!-- Ejemplos de resultados de las queries de la Activity 9, con su interpretación de negocio. -->
