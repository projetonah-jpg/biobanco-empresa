import hmac
import os
import sqlite3
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

st.set_page_config(
    page_title="BIO BANK - NATALIA",
    page_icon="🧫",
    layout="wide",
)

PASTA_APP = Path(__file__).resolve().parent
CAMINHO_BANCO = PASTA_APP / "monitoramento.db"

USUARIO_PADRAO = os.getenv("APP_USERNAME", "Natalia")
SENHA_PADRAO = os.getenv("APP_PASSWORD", "Natalia@2026")


# ============================================================
# ESTILO E IDENTIDADE VISUAL
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --navy: #12343b;
        --teal: #13877c;
        --mint: #eaf5f2;
        --white: #ffffff;
    }

    .stApp {
        background: linear-gradient(
            135deg,
            #f8fcfb 0%,
            #edf6f4 100%
        );
    }

    .block-container {
        padding-top: 1.5rem;
        max-width: 1280px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #12343b,
            #0d5c58
        );
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #dcebe7;
        border-left: 5px solid #13877c;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 6px 18px rgba(18, 52, 59, 0.07);
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 10px;
        border: 0;
        background-color: #13877c;
        color: white;
        font-weight: 700;
        width: 100%;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #0f6f67;
        color: white;
    }

    .logo-login {
        text-align: center;
        color: #12343b;
        margin: 3vh auto 18px auto;
    }

    .logo-login h1 {
        font-size: 34px;
        margin: 10px 0 0 0;
    }

    .logo-login p {
        color: #5e7776;
        margin-top: 4px;
    }

    .logo-icone {
        width: 96px;
        height: 96px;
        margin: auto;
        border-radius: 50%;
        display: grid;
        place-items: center;
        background: linear-gradient(
            145deg,
            #13877c,
            #12343b
        );
        color: white;
        font-size: 48px;
        box-shadow: 0 12px 28px rgba(19, 135, 124, 0.28);
    }

    .caixa-login {
        background-color: white;
        padding: 28px 34px 20px 34px;
        border-radius: 22px;
        box-shadow: 0 24px 70px rgba(18, 52, 59, 0.14);
        border: 1px solid #dfefeb;
    }

    .cabecalho {
        padding: 20px 24px;
        background: linear-gradient(
            120deg,
            #12343b,
            #13877c
        );
        color: white;
        border-radius: 18px;
        margin-bottom: 20px;
        box-shadow: 0 12px 30px rgba(18, 52, 59, 0.14);
    }

    .cabecalho h1 {
        margin: 0;
        font-size: 29px;
    }

    .cabecalho p {
        margin: 5px 0 0 0;
        color: #d8efeb;
    }

    .logo-menu {
        text-align: center;
        padding: 10px 0 18px 0;
        font-weight: 700;
        font-size: 18px;
    }

    .logo-menu span {
        display: block;
        font-size: 12px;
        font-weight: 400;
        color: #cbe5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LISTAS DE VALIDAÇÃO
# ============================================================

LISTAS = {
    "ORIGIN": ["Environmental Monitoring", "Storage Tanks", "M.A", "Processes"],
    "AREA": [
        "Laboratory", "Dissolution", "1940", "1920", "1910", "1710", "1720",
        "Line 2", "Line 3", "Line 4", "Line 5", "SBTA", "SBTA 1", "SBTA 2", "Autoclave"
    ],
    "SAMPLE": [
        "Inoculation Room Anteroom", "Inoculation Room", "Flow Room", "Dissolution",
        "Preparation", "Weighing", "Team Member", "Sterile"
    ],
    "COLLECTION POINT": [
        "Laminar Flow FLA001", "Laminar Flow FLA002", "Laminar Flow FLA003",
        "Laminar Flow FLA004", "Laminar Flow FLA005", "Laminar Flow FLA006",
        "Dissolution Room", "Inoculation Room", "Inoculation Anteroom", "Molasses",
        "Blend", "VHP", "CIP", "Flow Room", "Dissolution Tank", "Pump Outlet Filter",
        "Weighing Bench", "Becker", "Bucket", "Spatula", "Floor", "Wall",
        "Hands (glove)", "Lab Coat", "Drain Dissolution", "Weighing Drain",
        "Hand-Washing Sink", "Feedstock", "Aseptic Salts", "Collection Point"
    ],
    "SAMPLING": ["Swab", "Passive", "MAS-100", "Palating"],
    "METHOD": ["Petrifilm AC", "Petrifilm EB", "TSAC", "YPD", "Petrifilm YM"],
    "FORM": ["Cocos", "Bacilos", "Strepto", "Staphylo", "Cocobacilos", "Vibrio", "Leveduras"],
    "AFFIRMATION": ["Positive", "Negative", "N/A"],
    "MARGIN": ["Round", "Wavy", "Lobulated", "Filamentous", "Spiral"],
    "RESULTADO": ["Conforme", "Não Conforme"],
    "FREQUÊNCIA": ["Semanal", "Mensal"],
}


# ============================================================
# CONEXÃO E FUNÇÕES DO BANCO DE DADOS
# ============================================================

def inicializar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    
    # Criando a tabela de identificações com TODAS as colunas para preservar legado
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS identificacoes (
            code TEXT PRIMARY KEY,
            area TEXT,
            collection_point TEXT,
            date TEXT,
            form TEXT,
            margin TEXT,
            pigment TEXT,
            gram_stain TEXT,
            catalase TEXT,
            koh TEXT,
            oxidase TEXT,
            outsourced_method TEXT,
            identification TEXT,
            company TEXT,
            end_date TEXT,
            report_name TEXT,
            report_data BLOB
        )
        """
    )
    conexao.commit()
    conexao.close()


def salvar_identificacao(dados, arquivo_bytes=None, arquivo_nome=""):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    
    # Executa a query salvando valores padrão vazios para os campos removidos
    cursor.execute(
        """
        INSERT INTO identificacoes (
            code, area, collection_point, date, form, 
            margin, pigment, gram_stain, catalase, koh, 
            oxidase, outsourced_method, identification, company, end_date,
            report_name, report_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(code) DO UPDATE SET
            area=excluded.area,
            collection_point=excluded.collection_point,
            date=excluded.date,
            form=excluded.form,
            gram_stain=excluded.gram_stain,
            identification=excluded.identification,
            company=excluded.company,
            end_date=excluded.end_date,
            report_name=COALESCE(excluded.report_name, identificacoes.report_name),
            report_data=COALESCE(excluded.report_data, identificacoes.report_data)
        """,
        (
            dados["code"], dados["area"], dados["collection_point"], dados["date"], dados["form"],
            dados.get("margin", ""), dados.get("pigment", ""), dados["gram_stain"], 
            dados.get("catalase", ""), dados.get("koh", ""), dados.get("oxidase", ""), 
            dados.get("outsourced_method", ""), dados["identification"], dados["company"], dados["end_date"],
            arquivo_nome, arquivo_bytes
        )
    )
    conexao.commit()
    conexao.close()


def listar_identificacoes():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    df = pd.read_sql_query("SELECT * FROM identificacoes", conexao)
    conexao.close()
    return df


# Inicializa o banco de dados
inicializar_banco()


# ============================================================
# INTERFACE DO USUÁRIO (STREAMLIT)
# ============================================================

# Mock de sessões ativas simples para demonstração técnica do fluxo
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = True  # Bypass para fins de teste direto da tela


if st.session_state["autenticado"]:
    # Barra Lateral
    with st.sidebar:
        st.markdown('<div class="logo-menu">🧫 BIO BANK<br><span>Monitoramento Microbiológico</span></div>', unsafe_allow_html=True)
        st.write(f"Conectado como: **{USUARIO_PADRAO}**")
        st.markdown("---")
        st.markdown("• **Identificação**")
        st.markdown("• Armazenamento")
        st.markdown("• Dados")

    # Cabeçalho Principal
    st.markdown(
        """
        <div class="cabecalho">
            <h1>Identificação Microbiológica</h1>
            <p>Painel de Triagem e Cadastro Automatizado de Cepas</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Simulação de metadados herdados da amostra selecionada
    st.subheader("Seleccione o CODE")
    codigo_selecionado = st.selectbox("CODE", ["B4-001", "B4-002", "B4-003", "B4-004", "B4-005"], label_visibility="collapsed")
    
    # Informação de Contexto Fictícia baseada no CODE
    st.info(f"📍 **Área:** Laboratory | **Ponto:** Inoculation Anteroom | **Data de Entrada:** 2026-09-22")

    st.markdown("---")

    # FORMULÁRIO ATUALIZADO E LIMPO (Sugestão Biobank)
    col1, col2 = st.columns(2)

    with col1:
        morphology = st.selectbox("MORPHOLOGY", LISTAS["FORM"], index=0)
        gram_stain = st.selectbox("GRAM STAIN", LISTAS["AFFIRMATION"], index=0)
        identification = st.text_input("IDENTIFICATION", placeholder="Ex: Enterococcus faecalis")

    with col2:
        company = st.text_input("COMPANY", placeholder="Empresa responsável ou parceira")
