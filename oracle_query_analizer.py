import streamlit as st
import oracledb
import pandas as pd
import sqlparse
import re
import uuid

# Configuración de la página
st.set_page_config(page_title="Oracle SQL Optimizer", layout="wide")

st.title("🔍 Validador y Optimizador de Consultas ORACLE")

# --- BARRA LATERAL: CONEXIÓN ---
st.sidebar.header("1. Configuración de Conexión")
db_host = st.sidebar.text_input("Host", "localhost")
db_port = st.sidebar.text_input("Puerto", "1521")
db_service = st.sidebar.text_input("Service Name (SID)", "ORCL")
db_user = st.sidebar.text_input("Usuario", "system")
db_pass = st.sidebar.text_input("Contraseña", type="password")

def get_connection():
    try:
        dsn_tns = oracledb.makedsn(db_host, db_port, service_name=db_service)
        return oracledb.connect(user=db_user, password=db_pass, dsn=dsn_tns)
    except Exception as e:
        st.sidebar.error(f"Error de conexión: {e}")
        return None

# --- LÓGICA DE ANÁLISIS ---
def analyze_static_rules(query):
    warnings = []
    if re.search(r"SELECT\s+\*", query, re.IGNORECASE):
        warnings.append({"Nivel": "Alto", "Problema": "Uso de 'SELECT *'", "Consejo": "Selecciona solo columnas necesarias."})
    if re.search(r"LIKE\s+['\"]%.*['\"]", query, re.IGNORECASE):
        warnings.append({"Nivel": "Alto", "Problema": "LIKE empieza con %", "Consejo": "Inhabilita índices. Evítalo."})
    if re.search(r"TRUNC\(\s*\w+\s*\)", query, re.IGNORECASE) and "WHERE" in query.upper():
        warnings.append({"Nivel": "Medio", "Problema": "Función TRUNC() en filtro", "Consejo": "Impide uso de índices en fechas."})
    return warnings

def analyze_execution_plan(df_plan):
    warnings = []
    for index, row in df_plan.iterrows():
        operation = str(row.get('OPERATION', ''))
        options = str(row.get('OPTIONS', ''))
        obj_name = str(row.get('OBJECT_NAME', 'Desconocido'))
        cost = row.get('COST', 0)
        
        if operation == 'TABLE ACCESS' and options == 'FULL':
            warnings.append({"Nivel": "Crítico", "Tabla": obj_name, "Problema": "FULL TABLE SCAN", "Consejo": "Lectura completa de tabla. Revisa índices."})
        if 'CARTESIAN' in options or 'CARTESIAN' in operation:
            warnings.append({"Nivel": "Crítico", "Tabla": "N/A", "Problema": "PRODUCTO CARTESIANO", "Consejo": "Falta condición de JOIN."})
        if 'SKIP SCAN' in options:
            warnings.append({"Nivel": "Medio", "Tabla": obj_name, "Problema": "INDEX SKIP SCAN", "Consejo": "Índice no óptimo para este filtro."})
            
    return warnings

# --- INTERFAZ ---
st.header("2. Ingresa tu Consulta SQL (Oracle)")
query = st.text_area("Consulta SQL", height=150, placeholder="SELECT * FROM employees")

if st.button("Validar y Analizar"):
    if not query.strip():
        st.warning("Escribe una consulta.")
    else:
        conn = get_connection()
        if conn:
            # Formateo
            st.code(sqlparse.format(query, reindent=True, keyword_case='upper'), language='sql')
            
            # Análisis
            static_warnings = analyze_static_rules(query)
            dynamic_warnings = []
            explain_df = pd.DataFrame()
            
            try:
                cursor = conn.cursor()
                stmt_id = str(uuid.uuid4())[:30]
                
                # Explain Plan
                cursor.execute(f"EXPLAIN PLAN SET STATEMENT_ID = '{stmt_id}' FOR {query}")
                
                # Leer Plan
                cursor.execute(f"SELECT OPERATION, OPTIONS, OBJECT_NAME, COST, CARDINALITY FROM PLAN_TABLE WHERE STATEMENT_ID = '{stmt_id}' ORDER BY ID ASC")
                columns = [col[0] for col in cursor.description]
                explain_df = pd.DataFrame(cursor.fetchall(), columns=columns)
                
                # Limpiar
                cursor.execute(f"DELETE FROM PLAN_TABLE WHERE STATEMENT_ID = '{stmt_id}'")
                conn.commit()
                conn.close()
                
                dynamic_warnings = analyze_execution_plan(explain_df)
            except Exception as e:
                st.error(f"Error: {e}")

            # Resultados
            st.divider()
            if not explain_df.empty:
                st.subheader("Plan de Ejecución")
                st.dataframe(explain_df, use_container_width=True)

            st.subheader("Reporte")
            all_warnings = static_warnings + dynamic_warnings
            if not all_warnings:
                st.success("No se detectaron problemas graves.")
            else:
                for w in all_warnings:
                    color = "red" if w['Nivel'] == "Crítico" else "orange"
                    st.markdown(f":{color}[**[{w['Nivel']}] {w['Problema']}**] - {w['Consejo']}")