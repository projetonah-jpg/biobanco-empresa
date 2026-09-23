import streamlit as st
import pandas as pd
import os
import sqlite3
from datetime import datetime, date
from io import BytesIO
import plotly.express as px

# Configuração da página corporativa
st.set_page_config(page_title="Controle de Amostras LIMS", layout="wide", page_icon="🔬")

# --- ESTILIZAÇÃO CUSTOMIZADA EM CSS ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

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

# ==================== BANCO DE DADOS ADAPTADO PARA A NUVEM ====================
# CORREÇÃO PARA FILTRAR O ERRO DO SERVIDOR LINUX
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
            return df
    except Exception:
        pass
        
    return pd.DataFrame(columns=colunas_oficiais)

df = carregar_dados()

# Cabeçalhos superiores
st.markdown("<h1 style='margin-bottom: 0px;'>🔬 Rastreabilidade de Amostras e Monitoramento</h1>", unsafe_allow_html=True)
st.markdown("---")

# Abas horizontais oficiais mantidas estáveis
aba_dash, aba_cadastro, aba_visualizacao, aba_identificacao, aba_suporte = st.tabs([
    "📊 DASHBOARD", "📝 REGISTER (CADASTRAR/EDITAR)", "📋 LIST / ESTOQUE GERAL", "🧫 IDENTIFICATION (LAB)", "🔧 SUPORTE"
])

# --- ABA 1: DASHBOARD ---
with aba_dash:
    st.markdown("<br>", unsafe_allow_html=True)
    if not df.empty and "RESULTADO FINAL" in df.columns:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(label="Total de Amostras Registradas", value=len(df))
        
        qtd_positives = len(df[df["RESULTADO FINAL"] == "Positive"])
        qtd_negatives = len(df[df["RESULTADO FINAL"] == "Negative"])
        col_m2.metric(label="Total de Casos Positivos", value=qtd_positives)
        col_m3.metric(label="Total de Casos Negativos", value=qtd_negatives)
        
        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("##### 📊 Amostras Monitoradas por Área")
            df_area_grafico = df["AREA"].value_counts().reset_index()
            df_area_grafico.columns = ["AREA", "Quantidade"]
            fig_barras = px.bar(df_area_grafico, x="AREA", y="Quantidade", template="plotly_dark", color="AREA", text_auto=True)
            st.plotly_chart(fig_barras, use_container_width=True)
            
        with col_g2:
            st.markdown("##### 🧫 Proporção de Resultados (Positive / Negative / Sem results)")
            df_pie = df["RESULTADO FINAL"].replace("", "Sem results").fillna("Sem results").value_counts().reset_index()
            df_pie.columns = ["Resultado", "Quantidade"]
            fig_pizza = px.pie(df_pie, values="Quantidade", names="Resultado", template="plotly_dark", hole=0.4, color_discrete_map={"Positive":"#ef4444", "Negative":"#10b981", "Sem results":"#64748b"})
            st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.info("ℹ️ Nenhuma amostra cadastrada no sistema para renderizar os gráficos.")

# --- ABA 2: REGISTER (CADASTRAR OU EDITAR) ---
with aba_cadastro:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 DICA DE EDIÇÃO: Para alterar uma amostra existente, basta digitar o mesmo CODE dela, modificar as informações desejadas e clicar no botão de salvar!")

    with st.form(key="form_lims_corporativo"):
        st.markdown("##### ⬇️ Preencha os campos abaixo e clique no botão para salvar/atualizar:")
        botao_salvar = st.form_submit_button(label="💾 SALVAR OU ATUALIZAR REGISTRO", type="primary", use_container_width=True)
        
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
            
            cursor.execute("SELECT pigment, gram_stain, catalase, koh, oxidase, outsourced_method, identification, report, company, end_date FROM monitoramento WHERE code=?", (code.strip(),))
            dados_antigos = cursor.fetchone()
            
            pig, gram, cat, k, ox, out, iden, rep, comp, dt_end = "", "", "", "", "", "", "", "", "", ""
            if dados_antigos:
                pig, gram, cat, k, ox, out, iden, rep, comp, dt_end = dados_antigos
            
            cursor.execute("DELETE FROM monitoramento WHERE code=?", (code.strip(),))
            cursor.execute("""
                INSERT INTO monitoramento (code, ponto, origin, area, sample, collection_point, sampling, method, frequencia, analista, data_coleta, resultado_final, form, affirmation, margin, pigment, gram_stain, catalase, koh, oxidase, outsourced_method, identification, report, company, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code.strip(), ponto, origin, area, sample, collection_point, sampling, method, frequencia, analista, str(data_coleta), resultado_final, form, affirmation, margin, pig, gram, cat, k, ox, out, iden, rep, comp, dt_end))
            
            conexao.commit()
            conexao.close()
            st.success("✅ Registro processado e atualizado no estoque com sucesso!")
            st.rerun()

# --- ABA 3: LISTA / ESTOQUE GERAL ---
with aba_visualizacao:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_b, col_del = st.columns(2)
    with col_b:
        busca_estoque = st.text_input("🔍 Sistema de Filtro e Busca Rápida (Digite o CODE ou AREA):", placeholder="Ex: L5-26-150...", key="busca_view")
    
    with col_del:
        with st.container(border=True):
            st.markdown("<small>🗑️ Central de Exclusão Definitiva</small>", unsafe_allow_html=True)
