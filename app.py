import streamlit as st
import pandas as pd
import os
import sqlite3
from datetime import datetime, date
from io import BytesIO

# Configuração da página corporativa
st.set_page_config(page_title="Controle de Amostras LIMS", layout="wide", page_icon="🔬")

# ==================== CONFIGURAÇÃO DE SEGURANÇA ====================
SENHA_CORRETA = "lab123" 

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #3b82f6; margin-top: 50px;'>🔬 Sistema de Controle de Amostras</h2>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        with st.container(border=True):
            senha_inserida = st.text_input("Senha do Laboratório:", type="password", placeholder="Digite a senha...")
            if st.button("Entrar no Painel", use_container_width=True, type="primary"):
                if senha_inserida == SENHA_CORRETA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
    st.stop()

# ==================== BANCO DE DADOS ADAPTADO PARA A WEB (CORRIGIDO) ====================
# Ajuste técnico: salvando direto no ambiente de execução em nuvem, eliminando o erro de Desktop
DB_FILE = "biobanco_laboratorio.db"

def inicializar_banco():
    conexao = sqlite3.connect(DB_FILE)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoramento (
            code TEXT PRIMARY KEY, ponto TEXT, origin TEXT, area TEXT, 
            sample TEXT, collection_point TEXT, sampling TEXT, method TEXT, 
            frequencia TEXT, analista TEXT, data_coleta TEXT, resultado_final TEXT,
            form TEXT, affirmation TEXT, margin TEXT,
            pigment TEXT, gram_stain TEXT, catalase TEXT, koh TEXT,
            oxidase TEXT, outsourced_method TEXT, identification TEXT,
            report TEXT, company TEXT, end_date TEXT
        )
    """)
    conexao.commit()
    conexao.close()

inicializar_banco()

def carregar_dados():
    colunas_oficiais = [
        "CODE", "AREA", "COLLECTION POINT", "DATA", "FORM", "MARGIN", 
        "PIGMENT", "GRAM STAIN", "CATALASE", "KOH", "OXIDASE", 
        "OUTSOURCED METHOD", "IDENTIFICATION", "REPORT", "COMPANY", "END DATE"
    ]
    try:
        conexao = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM monitoramento", conexao)
        conexao.close()
        
        if not df.empty:
            df.columns = [
                "CODE", "PONTO", "ORIGIN", "AREA", "SAMPLE", 
                "COLLECTION POINT", "SAMPLING", "METHOD", "FREQUÊNCIA", 
                "ANALISTA", "DATA", "RESULTADO FINAL", "FORM", "AFFIRMATION", "MARGIN",
                "PIGMENT", "GRAM STAIN", "CATALASE", "KOH", "OXIDASE", 
                "OUTSOURCED METHOD", "IDENTIFICATION", "REPORT", "COMPANY", "END DATE"
            ]
            return df[colunas_oficiais]
    except Exception:
        pass
        
    return pd.DataFrame(columns=colunas_oficiais)

df = carregar_dados()

# Cabeçalhos superiores
st.markdown("<h1 style='margin-bottom: 0px;'>🔬 Rastreabilidade de Amostras e Monitoramento</h1>", unsafe_allow_html=True)
st.markdown("---")

# Abas horizontais
aba_dash, aba_cadastro, aba_visualizacao, aba_identificacao, aba_suporte = st.tabs([
    "📊 DASHBOARD", "📝 REGISTER (CADASTRAR)", "📋 LIST / ESTOQUE GERAL", "🧫 IDENTIFICATION (LAB)", "🔧 SUPORTE"
])

# --- ABA 1: DASHBOARD ---
with aba_dash:
    st.metric(label="Total de Amostras Registradas", value=len(df))
    st.info("ℹ️ Sistema ativo. Preencha os registros na aba de cadastro.")

# --- ABA 2: REGISTER (CADASTRAR) ---
with aba_cadastro:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form(key="form_lims_corporativo"):
        st.markdown("##### ⬇️ Preencha os campos abaixo e clique no botão para salvar:")
        botao_salvar = st.form_submit_button(label="💾 SALVAR REGISTRO DE AMOSTRA", type="primary", use_container_width=True)
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("##### 📋 Identificação Inicial")
            code = st.text_input("CODE * (Ex: L5-26-150)")
            ponto = st.text_input("PONTO")
            analista = st.text_input("ANALISTA", value="Natalia")
            frequencia = st.selectbox("FREQUÊNCIA", ["Mensal", "Semanal", "Quinzenal", "Anual", "Pontual"])
            data_coleta = st.date_input("DATA", value=date.today(), key="data_reg")
        with col2:
            st.markdown("##### 📍 Origem e Coleta")
            origin = st.selectbox("ORIGIN", ["Environmental Monitoring", "Storage Tanks", "Amostra", "Processes"])
            area = st.selectbox("AREA", ["Laboratory", "Dissolution", "Line 2", "Line 3", "Line 4", "Line 5", "SBTA 1", "SBTA 2", "Autoclave"])
            sample = st.selectbox("SAMPLE", ["Inoculation Room", "Flow Room", "Dissolution", "Preparation", "Weighing", "Team Member", "Sterile"])
            collection_point = st.selectbox("COLLECTION POINT", ["Laminar Flow FLA001", "Dissolution Room", "Floor", "Wall", "Collection Point"])
        with col3:
            st.markdown("##### 🧪 Análise Macro")
            sampling = st.selectbox("SAMPLING", ["Swab", "Passive", "MAS-100", "Palating"])
            method = st.selectbox("METHOD", ["Petrifilm AC", "Petrifilm EB", "TSAC"])
            form = st.selectbox("FORM", ["Punctiform", "Circular", "Filamentous", "Irregular"])
            affirmation = st.selectbox("AFFIRMATION", ["Negative", "Positive", "N/A"])
            margin = st.selectbox("MARGIN", ["Round", "Wavy", "Lobulated"])
            resultado_final = st.selectbox("RESULTADO FINAL", ["", "Positive", "Negative", "Sem results"])

    if botao_salvar:
        if code.strip() == "":
            st.error("❌ Erro: O campo CODE é obrigatório!")
        else:
            conexao = sqlite3.connect(DB_FILE)
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM monitoramento WHERE code=?", (code,))
            cursor.execute("""
                INSERT INTO monitoramento (code, ponto, origin, area, sample, collection_point, sampling, method, frequencia, analista, data_coleta, resultado_final, form, affirmation, margin, pigment, gram_stain, catalase, koh, oxidase, outsourced_method, identification, report, company, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', '', '', '', '', '', '', '', '')
            """, (code, ponto, origin, area, sample, collection_point, sampling, method, frequencia, analista, str(data_coleta), resultado_final, form, affirmation, margin))
            conexao.commit()
            conexao.close()
            st.success("✅ Registro inserido com sucesso!")
            st.rerun()

# --- ABA 3: LISTA / ESTOQUE GERAL ---
with aba_visualizacao:
    st.markdown("<br>", unsafe_allow_html=True)
    busca_estoque = st.text_input("🔍 Sistema de Filtro e Busca Rápida (Digite o CODE ou AREA):", placeholder="Ex: L5-26-150...")
    
    if not df.empty:
        df_filtrado_estoque = df[df["CODE"].astype(str).str.contains(busca_estoque, case=False, na=False) | df["AREA"].astype(str).str.contains(busca_estoque, case=False, na=False)] if busca_estoque else df
        st.dataframe(df_filtrado_estoque, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Nenhuma amostra cadastrada no banco de dados até o momento.")

# --- ABA 4: IDENTIFICATION ---
with aba_identificacao:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧫 Laudos Microbiológicos das Amostras Registradas")
    
    colunas_imagem = ["CODE", "AREA", "COLLECTION POINT", "DATA", "FORM", "MARGIN", "PIGMENT", "GRAM STAIN", "CATALASE", "KOH", "OXIDASE", "OUTSOURCED METHOD", "IDENTIFICATION", "REPORT", "COMPANY", "END DATE"]
    st.dataframe(df[colunas_imagem], use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("##### 🧪 Preencher Análise de Identificação de Amostra")
    
    code_selecionado = st.text_input("Digite o CODE da amostra para lançar o laudo (Ex: L5-26-150):")

    with st.form(key="form_id_final_novo"):
        col_id1, col_id2, col_id3 = st.columns(3)
        with col_id1:
            pigment = st.selectbox("PIGMENT", ["", "Cream", "Yellow", "White", "Pink", "Orange", "N/A"])
            gram_stain = st.selectbox("GRAM STAIN", ["", "Gram-positive", "Gram-negative", "N/A"])
            catalase = st.selectbox("CATALASE", ["", "Positive", "Negative", "N/A"])
        with col_id2:
            koh = st.selectbox("KOH", ["", "Positive", "Negative", "N/A"])
            oxidase = st.selectbox("OXIDASE", ["", "Positive", "Negative", "N/A"])
            outsourced_method = st.text_input("OUTSOURCED METHOD")
        with col_id3:
            identification = st.text_input("IDENTIFICATION")
            report = st.text_input("REPORT")
            company = st.text_input("COMPANY")
            end_date = st.date_input("END DATE", value=date.today(), key="data_end")
            
        st.markdown("<br>", unsafe_allow_html=True)
        botao_salvar_id = st.form_submit_button(label="💾 CONCLUIR E ATUALIZAR INFORMAÇÕES", type="primary", use_container_width=True)
        
    if botao_salvar_id and code_selecionado.strip() != "":
        conexao = sqlite3.connect(DB_FILE)
        cursor = conexao.cursor()
        cursor.execute("UPDATE monitoramento SET pigment=?, gram_stain=?, catalase=?, koh=?, oxidase=?, outsourced_method=?, identification=?, report=?, company=?, end_date=? WHERE code=?", (pigment, gram_stain, catalase, koh, oxidase, outsourced_method, identification, report, company, str(end_date), code_selecionado.strip()))
        conexao.commit()
        conexao.close()
