# 🔍 Oracle SQL Optimizer & Validator

Una aplicación web construida con **Python** y **Streamlit** que ayuda a desarrolladores y DBAs a analizar consultas SQL para Oracle Database.

La herramienta realiza dos tipos de validaciones:
1.  **Análisis Estático:** Detecta malas prácticas de sintaxis antes de la ejecución (ej. `SELECT *`, `LIKE '%...'`, funciones en columnas filtradas).
2.  **Análisis Dinámico:** Conecta a la base de datos, genera un `EXPLAIN PLAN` y detecta cuellos de botella críticos como *Full Table Scans* o *Productos Cartesianos*.

## 📋 Requisitos Previos

*   Python 3.8 o superior.
*   Acceso a una base de datos Oracle (Host, Puerto, Service Name/SID, Usuario y Contraseña).
*   El usuario de base de datos debe tener permisos para escribir en la tabla `PLAN_TABLE` (estándar en Oracle para generar planes de ejecución).

## 🚀 Instalación

Sigue estos pasos para configurar el proyecto en tu máquina local.

### 1. Clonar el repositorio
Descarga el código en tu máquina

2. Crear un Entorno Virtual
Es altamente recomendado usar un entorno virtual para evitar conflictos con las librerías del sistema.

En Linux / macOS:

python3 -m venv venv
source venv/bin/activate

En Windows:

python -m venv venv
.\venv\Scripts\activate

4. Instalar Dependencias
Instala las librerías necesarias (streamlit, oracledb, pandas, sqlparse) ejecutando:

pip install -r requirements.txt
(Si no tienes el archivo requirements.txt, puedes instalar manualmente con: pip install streamlit oracledb pandas sqlparse)

🛠️ Uso
Asegúrate de tener el entorno virtual activado.
Ejecuta la aplicación con Streamlit:

streamlit run app.py

Se abrirá automáticamente una pestaña en tu navegador (usualmente en http://localhost:8501).

En la barra lateral, ingresa las credenciales de tu base de datos Oracle.
Escribe tu consulta en el área de texto y presiona "Validar y Analizar".

🛡️ Qué detecta esta herramienta
Reglas Estáticas (Sintaxis)

⛔ SELECT *: Uso ineficiente de I/O.

⛔ LIKE '%valor': Comodines al inicio que invalidan índices.

⚠️ TRUNC(fecha) en WHERE: Funciones que impiden el uso de índices en fechas.
Reglas Dinámicas (Explain Plan)

🔥 TABLE ACCESS FULL: Lectura completa de la tabla (índices faltantes).

❌ CARTESIAN JOIN: Falta de condiciones de unión (riesgo de rendimiento severo).

⚠️ INDEX SKIP SCAN: Uso subóptimo de índices compuestos.

📝 Notas sobre Oracle
Librería: Este proyecto usa python-oracledb en modo "Thin", por lo que no necesitas instalar el Oracle Instant Client en la mayoría de los casos.
PLAN_TABLE: La aplicación genera un STATEMENT_ID único (UUID) para cada análisis, inserta el plan, lo lee y luego lo borra para mantener la tabla limpia.

📄 Licencia
Este proyecto está bajo la licencia MIT.
