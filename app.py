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
# ESTILO E IDENTIDADE VISUAL DINÂMICA (CORREÇÃO TOTAL DE LEITURA)
# ============================================================

if not st.session_state.get("autenticado"):
    cor_fundo_interna = "#612147"
    cor_texto_login_h1 = "#ffffff"
    cor_texto_login_p = "#f5edf2"
    sombra_container = "none"
    padding_container = "2rem"
else:
    cor_fundo_interna = "#ffffff"
    cor_texto_login_h1 = "#31333F"
    cor_texto_login_p = "#31333F"
    sombra_container = "0 12px 36px rgba(0, 0, 0, 0.25)"
    padding_container = "0px 45px 35px 45px"

st.markdown(
    f"""
    <style>
    :root {{
        --purple-dark: #612147;
        --purple-light: #833161;
        --purple-bg: #fdfafc;
        --white: #ffffff;
    }}

    /* 🚫 Oculta completamente a barra branca superior e seus botões (Share, Gato) */
    .stAppHeader, [data-testid="stHeader"], header, [data-testid="stHeaderActionElements"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }}

    /* 💜 Pinta as laterais externas e o fundo geral com o roxo escuro oficial */
    .stApp {{
        background-color: #612147 !important;
    }}

    /* 🛡️ Força a folha interna a seguir a decisão do Python */
    [data-testid="stMainView"], [data-testid="stCanvas"], .main, .stVerticalBlockRoot {{
        background-color: {cor_fundo_interna} !important;
    }}

    /* 📏 Ajusta a folha central de trabalho de forma dinâmica */
    .block-container {{
        background-color: {cor_fundo_interna} !important;
        padding: {padding_container} !important;
        margin-top: 0rem !important;
        border-radius: 0px 0px 18px 18px !important;
        box-shadow: {sombra_container} !important;
        max-width: 94% !important;
    }}

    [data-testid="stMain"] {{
        padding-top: 0rem !important;
        background-color: #612147 !important;
    }}

    /* 🎯 CORREÇÃO: Garante que APENAS os textos de dentro do formulário branco fiquem pretos */
    [data-testid="stMainView"] [data-testid="stWidgetLabel"] p, 
    [data-testid="stMainView"] label p, 
    [data-testid="stMainView"] .stMarkdown p, 
    [data-testid="stMainView"] h1, 
    [data-testid="stMainView"] h2, 
    [data-testid="stMainView"] h3, 
    [data-testid="stMainView"] .stSubheader {{
        color: #31333F !important;
    }}
    
    /* ⚪ FORÇA TEXTO BRANCO ABSOLUTO NO BANNER DO TOPO (Garante Biobank - Natalia e Gestão de Cepas legíveis) */
    .banner-topo, .banner-topo h1, .banner-topo p, .banner-topo div {{
        color: #ffffff !important;
    }}
    
    /* ⚪ FORÇA TEXTO BRANCO ABSOLUTO NA BARRA LATERAL (Garante Natalia, Navegação, Conectado em branco) */
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {{
        color: #ffffff !important;
    }}

    /* 💜 Menu Lateral Customizado com a cor sólida idêntica ao seu banner oficial */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{
        background-color: #612147 !important;
        background-image: none !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}

    /* 💜 Cards de Indicadores (Métricas) com Borda Combinando */
    [data-testid="stMetric"] {{
        background-color: white !important;
        border: 1px solid #f5edf2 !important;
        border-left: 5px solid #833161 !important;
        padding: 16px !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 18px rgba(97, 33, 71, 0.06) !important;
    }}

    /* 💜 Botões de ação com letras brancas forçadas sempre */
    .stButton > button, .stFormSubmitButton > button, 
    .stButton > button *, .stFormSubmitButton > button * {{
        border-radius: 10px !important;
        border: 0 !important;
        background-color: #833161 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }}

    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        background-color: #612147 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(131, 49, 97, 0.25) !important;
    }}

    /* 💜 Estilos da Tela de Login */
          /* 💜 Estilos da Tela de Login */
    .logo-login {{
        text-align: center;
        margin: 3vh auto 18px auto;
    }}

    .logo-login h1 {{
        font-size: 38px !important;
        margin: 10px 0 0 0 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }}

    .logo-login p {{
        color: #f5edf2 !important;
        margin-top: 4px !important;
    }}

    /* 🔬 CONFIGURAÇÃO DO ÍCONE GRANDE E EM 3D COM CHAVES DUPLAS */
    .logo-icone {{
        width: 140px !important;    /* Aumenta o tamanho do círculo */
        height: 140px !important;   /* Aumenta o tamanho do círculo */
        margin: auto !important;
        border-radius: 50% !important;
        display: grid !important;
        place-items: center !important;
        background: linear-gradient(145deg, #833161, #612147) !important;
        color: white !important;
        font-size: 72px !important; /* Deixa o microscópio bem grande dentro do círculo */
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4) !important; /* Efeito de sombra marcante */
        border: 3px solid rgba(255, 255, 255, 0.1) !important;
    }}

    [data-testid="stForm"] {{
        background-color: white !important;
        padding: 28px 34px 20px 34px !important;
        border-radius: 22px !important;
        border: 1px solid #f5edf2 !important;
    }}

    .texto-rodape {{
        text-align: center;
        color: #f5edf2 !important;
        font-size: 13px;
        margin-top: 15px;
    }}
     /* 🎯 Limpa os bugs do Modo Escuro: força fundo branco e letra escura em tudo, incluindo a DATA */
    [data-testid="stTextInput"] input, 
    [data-testid="stSelectbox"] div, 
    [data-testid="stNumberInput"] input,
    .stSelectbox div,
    .stDateInput button,
    input {{
        background-color: #ffffff !important;
        color: #31333F !important;
        -webkit-text-fill-color: #31333F !important;
    }}
    </style>
    
    """,
    unsafe_allow_html=True,
)
# ============================================================
# LISTAS DE VALIDAÇÃO
# ============================================================

LISTAS = {
    "ORIGIN": [
        "Environmental Monitoring",
        "Storage Tanks",
        "Processes",
    ],
    "AREA": [
        "Laboratory",
        "Dissolution",
        "1940",
        "1920",
        "1910",
        "1710",
        "1720",
        "Line 2",
        "Line 3",
        "Line 4",
        "Line 5",
        "SBTA",
        "SBTA 1",
        "SBTA 2",
        "Autoclave",
    ],
    "SAMPLE": [
        "Inoculation Room Anteroom",
        "Inoculation Room",
        "Flow Room",
        "Dissolution",
        "Preparation",
        "Weighing",
        "Team Member",
        "Sterile",
    ],
    "COLLECTION POINT": [
        "Laminar Flow FLA001",
        "Laminar Flow FLA002",
        "Laminar Flow FLA003",
        "Laminar Flow FLA004",
        "Laminar Flow FLA005",
        "Laminar Flow FLA006",
        "Dissolution Room",
        "Inoculation Room",
        "Inoculation Anteroom",
        "Molasses",
        "Blend",
        "VHP",
        "CIP",
        "Flow Room",
        "Dissolution Tank",
        "Pump Outlet Filter",
        "Weighing Bench",
        "Becker",
        "Bucket",
        "Spatula",
        "Floor",
        "Wall",
        "Hands (glove)",
        "Lab Coat",
        "Drain Dissolution",
        "Weighing Drain",
        "Hand-Washing Sink",
        "Feedstock",
        "Aseptic Salts",
        "Collection Point",
    ],
    "SAMPLING": [
        "Swab",
        "Passive",
        "MAS-100",
        "Palating",
    ],
    "METHOD": [
        "Petrifilm AC",
        "Petrifilm EB",
        "TSAC",
        "YPD",
        "Petrifilm YM",
    ],
    "FORM": [
        "Cocos",
        "Bacilos",
        "Strepto",
        "Staphylo",
        "Cocobacilos",
        "Vibrio",
    ],
    "AFFIRMATION": [
        "Positive",
        "Negative",
        "N/A",
    ],
    "MARGIN": [
        "Round",
        "Wavy",
        "Lobulated",
        "Filamentous",
        "Spiral",
    ],
    "RESULTADO": [
        "Conforme",
        "Não Conforme",
    ],
    "FREQUÊNCIA": [
        "Semanal",
        "Mensal",
    ],
}


# ============================================================
# DADOS ATUAIS DA PLANILHA
# ============================================================

AMOSTRAS_INICIAIS = [
    {
        "code": "B4-001",
        "ponto": "",
        "origin": "Storage Tanks",
        "area": "Laboratory",
        "sample": "",
        "collection_point": "",
        "sampling": "",
        "method": "",
        "frequencia": "Mensal",
        "analista": "Natalia",
        "data": "2026-09-23",
        "resultado_final": "Conforme",
    },
    {
        "code": "B4-002",
        "ponto": "",
        "origin": "Storage Tanks",
        "area": "Line 4",
        "sample": "Preparation",
        "collection_point": "Laminar Flow FLA006",
        "sampling": "Passive",
        "method": "TSAC",
        "frequencia": "Mensal",
        "analyst": "Natalia",
        "data": "2026-09-23",
        "resultado_final": "Não Conforme",
    },
    {
        "code": "B4-003",
        "ponto": "",
        "origin": "Amostra",
        "area": "Line 3",
        "sample": "Dissolution",
        "collection_point": "Laminar Flow FLA002",
        "sampling": "MAS-100",
        "method": "YPD",
        "frequencia": "Mensal",
        "analista": "Natalia",
        "data": "2026-09-23",
        "resultado_final": "Conforme",
    },
    {
        "code": "B4-004",
        "ponto": "",
        "origin": "Storage Tanks",
        "area": "Line 3",
        "sample": "Flow Room",
        "collection_point": "Flow Room",
        "sampling": "Palating",
        "method": "TSAC",
        "frequencia": "Mensal",
        "analista": "Natalia",
        "data": "2026-09-23",
        "resultado_final": "Conforme",
    },
    {
        "code": "B4-005",
        "ponto": "",
        "origin": "Environmental Monitoring",
        "area": "Dissolution",
        "sample": "Flow Room",
        "collection_point": "Laminar Flow FLA001",
        "sampling": "Swab",
        "method": "Petrifilm EB",
        "frequencia": "Mensal",
        "analista": "Natalia",
        "data": "2026-09-23",
        "resultado_final": "Não Conforme",
    },
]


IDENTIFICACOES_INICIAIS = [
    {
        "code": "B4-001",
        "form": "",
        "margin": "Round",
        "pigment": "",
        "gram_stain": "Positive",
        "catalase": "Negative",
        "koh": "Negative",
        "oxidase": "Negative",
        "outsourced_method": "",
        "identification": "Fungo",
        "report": "",
        "company": "",
        "end_date": "",
    },
    {
        "code": "B4-002",
        "form": "",
        "margin": "",
        "pigment": "",
        "gram_stain": "Negative",
        "catalase": "Negative",
        "koh": "Negative",
        "oxidase": "Negative",
        "outsourced_method": "",
        "identification": "Fungo",
        "report": "",
        "company": "",
        "end_date": "",
    },
    {
        "code": "B4-003",
        "form": "",
        "margin": "",
        "pigment": "",
        "gram_stain": "Negative",
        "catalase": "Positive",
        "koh": "Positive",
        "oxidase": "Positive",
        "outsourced_method": "",
        "identification": "Fungo",
        "report": "",
        "company": "",
        "end_date": "",
    },
    {
        "code": "B4-004",
        "form": "",
        "margin": "",
        "pigment": "",
        "gram_stain": "Negative",
        "catalase": "Negative",
        "koh": "Negative",
        "oxidase": "Negative",
        "outsourced_method": "",
        "identification": "Fungo",
        "report": "",
        "company": "",
        "end_date": "",
    },
    {
        "code": "B4-005",
        "form": "",
        "margin": "",
        "pigment": "",
        "gram_stain": "Positive",
        "catalase": "Negative",
        "koh": "Positive",
        "oxidase": "Positive",
        "outsourced_method": "",
        "identification": "Fungo",
        "report": "",
        "company": "",
        "end_date": "",
    },
]


# ============================================================
# BANCO DE DADOS
# ============================================================

COLUNAS_AMOSTRA = [
    "code",
    "ponto",
    "origin",
    "area",
    "sample",
    "collection_point",
    "sampling",
    "method",
    "frequencia",
    "analista",
    "data",
    "resultado_final",
]


COLUNAS_IDENTIFICACAO = [
    "code",
    "form",
    "margin",
    "pigment",
    "gram_stain",
    "catalase",
    "koh",
    "oxidase",
    "outsourced_method",
    "identification",
    "report",
    "company",
    "end_date",
]


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_banco():
    with conectar() as conexao:

        # 1. Criação direta das tabelas
        q1 = "CREATE TABLE IF NOT EXISTS amostras (code TEXT PRIMARY KEY, criado_em TEXT DEFAULT CURRENT_TIMESTAMP, atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP);"

        q2 = "CREATE TABLE IF NOT EXISTS identificacoes (code TEXT PRIMARY KEY, criado_em TEXT DEFAULT CURRENT_TIMESTAMP, atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(code) REFERENCES amostras(code) ON DELETE CASCADE);"

        q3 = "CREATE TABLE IF NOT EXISTS dados_brutos (id INTEGER PRIMARY KEY AUTOINCREMENT, criado_em TEXT DEFAULT CURRENT_TIMESTAMP);"

        q4 = """
        CREATE TABLE IF NOT EXISTS armazenamento_cepas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            box TEXT,
            backup_box TEXT,
            freezer TEXT,
            storage_date TEXT,
            analyst TEXT,
            backup_used TEXT
        );
        """

        conexao.execute(q1)
        conexao.execute(q2)
        conexao.execute(q3)
        conexao.execute(q4)

        
        # 2. MIGRATION: Garante as colunas na tabela 'amostras'
        colunas_amostras = {
            "ponto": "TEXT", "origin": "TEXT", "area": "TEXT", "sample": "TEXT", 
            "collection_point": "TEXT", "sampling": "TEXT", "method": "TEXT", 
            "frequencia": "TEXT", "analista": "TEXT", "data": "TEXT", "resultado_final": "TEXT"
        }
        for col, tipo in colunas_amostras.items():
            try: conexao.execute(f"ALTER TABLE amostras ADD COLUMN {col} {tipo}")
            except sqlite3.OperationalError: pass
                
        # 3. MIGRATION: Garante as colunas na tabela 'identificacoes'
        colunas_identificacoes = {
            "form": "TEXT", "margin": "TEXT", "pigment": "TEXT", "gram_stain": "TEXT", 
            "catalase": "TEXT", "koh": "TEXT", "oxidase": "TEXT", "outsourced_method": "TEXT", 
            "identification": "TEXT", "report": "TEXT", "company": "TEXT", "start_date": "TEXT", 
            "end_date": "TEXT", "report_data": "BLOB"
        }
        for col, tipo in colunas_identificacoes.items():
            try: conexao.execute(f"ALTER TABLE identificacoes ADD COLUMN {col} {tipo}")
            except sqlite3.OperationalError: pass

        # 4. MIGRATION: Garante as colunas na tabela 'dados_brutos'
        colunas_brutos = {
            "tsb": "TEXT", "tsb_val": "TEXT", "glicerina": "TEXT", "glicerina_val": "TEXT", 
            "tsa": "TEXT", "tsa_val": "TEXT", "criotubo": "TEXT", "placa_de_petri": "TEXT", 
            "fluxo_laminar": "TEXT", "ultrafreezer": "TEXT"
        }
        for col, tipo in colunas_brutos.items():
            try: conexao.execute(f"ALTER TABLE dados_brutos ADD COLUMN {col} {tipo}")
            except sqlite3.OperationalError: pass
                
        inserir_dados_iniciais(conexao)


def inserir_dados_iniciais(conexao):
    for amostra in AMOSTRAS_INICIAIS:
        valores = [amostra.get(coluna, "") for coluna in COLUNAS_AMOSTRA]
        conexao.execute(f"INSERT OR IGNORE INTO amostras ({','.join(COLUNAS_AMOSTRA)}) VALUES ({','.join('?' for _ in COLUNAS_AMOSTRA)})", valores)

    for identificacao in IDENTIFICACOES_INICIAIS:
        valores = [identificacao.get(coluna, "") for coluna in COLUNAS_IDENTIFICACAO]
        conexao.execute(f"INSERT OR IGNORE INTO identificacoes ({','.join(COLUNAS_IDENTIFICACAO)}) VALUES ({','.join('?' for _ in COLUNAS_IDENTIFICACAO)})", valores)

        conexao.execute(
            f"""
            INSERT OR IGNORE INTO identificacoes
            ({",".join(COLUNAS_IDENTIFICACAO)})
            VALUES (
                {",".join("?" for _ in COLUNAS_IDENTIFICACAO)}
            )
            """,
            valores,
        )


def consultar(sql, parametros=()):
    with conectar() as conexao:
        linhas = conexao.execute(
            sql,
            parametros,
        ).fetchall()

        return [dict(linha) for linha in linhas]


def salvar_amostra(registro):
    # Correção: Ajustado para usar exatamente a lista correta mapeada com 'resultado_final'
    marcadores = ",".join(
        "?" for _ in COLUNAS_AMOSTRA
    )

    atualizacoes = ",".join(
        f"{coluna}=excluded.{coluna}"
        for coluna in COLUNAS_AMOSTRA
        if coluna != "code"
    )

    sql = f"""
        INSERT INTO amostras
        ({",".join(COLUNAS_AMOSTRA)})
        VALUES ({marcadores})

        ON CONFLICT(code) DO UPDATE SET
            {atualizacoes},
            atualizado_em=CURRENT_TIMESTAMP
    """

    valores = [
        registro.get(coluna, "")
        for coluna in COLUNAS_AMOSTRA
    ]

    with conectar() as conexao:
        conexao.execute(sql, valores)


def salvar_identificacao(registro):
    marcadores = ",".join(
        "?" for _ in COLUNAS_IDENTIFICACAO
    )

    atualizacoes = ",".join(
        f"{coluna}=excluded.{coluna}"
        for coluna in COLUNAS_IDENTIFICACAO
        if coluna != "code"
    )

    sql = f"""
        INSERT INTO identificacoes
        ({",".join(COLUNAS_IDENTIFICACAO)})
        VALUES ({marcadores})

        ON CONFLICT(code) DO UPDATE SET
            {atualizacoes},
            atualizado_em=CURRENT_TIMESTAMP
    """

    valores = [
        registro.get(coluna, "")
        for coluna in COLUNAS_IDENTIFICACAO
    ]

    with conectar() as conexao:
        conexao.execute(sql, valores)


def excluir_amostra(code):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM amostras WHERE code = ?",
            (code,),
        )


def substituir_dados(amostras, identificacoes):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM identificacoes"
        )

        conexao.execute(
            "DELETE FROM amostras"
        )

    for amostra in amostras:
        salvar_amostra(amostra)

    for identificacao in identificacoes:
        salvar_identificacao(identificacao)


# ============================================================
# LOGIN
# ============================================================

def mostrar_login():
    if st.session_state.get("autenticado"):
        return True
    
    # GARANTA QUE ESSA LINHA ABAIXO ESTEJA EXATAMENTE ASSIM COM O ÍCONE 🔬
    st.markdown('<div class="logo-login"><div class="logo-icone">🔬</div><h1>BioBank</h1><p>Monitoramento Microbiológico</p></div>', unsafe_allow_html=True)
    
    _, centro, _ = st.columns([1.15, 1, 1.15])
    with centro:
        with st.form("formulario_login"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            
        st.markdown('<div class="texto-rodape">Acesso restrito ao laboratório de microbiologia.</div>', unsafe_allow_html=True)
        
        if entrar:
            if hmac.compare_digest(usuario.strip(), USUARIO_PADRAO) and hmac.compare_digest(senha, SENHA_PADRAO):
                st.session_state.autenticado = True
                st.session_state.usuario = USUARIO_PADRAO
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
    return False




# ============================================================
# FUNÇÕES DOS DADOS
# ============================================================

def obter_amostras():
    dados = consultar(
        """
        SELECT
            code,
            ponto,
            origin,
            area,
            sample,
            collection_point,
            sampling,
            method,
            frequencia,
            analista,
            data,
            resultado_final
        FROM amostras
        ORDER BY data DESC, code
        """
    )

    return pd.DataFrame(dados)


def obter_identificacoes():
    sql_consulta = """
        SELECT
            a.code,
            a.area,
            a.collection_point,
            a.data,
            i.form,
            i.margin,
            i.pigment,
            i.gram_stain,
            i.catalase,
            i.koh,
            i.oxidase,
            i.outsourced_method,
            i.identification,
            i.report,
            i.company,
            i.start_date,
            i.end_date
        FROM amostras a

        LEFT JOIN identificacoes i
            ON i.code = a.code

        ORDER BY a.code
    """
    try:
        dados = consultar(sql_consulta)
    except sqlite3.OperationalError:
        # Se a coluna start_date não existir ainda, cria ela agora automaticamente
        with conectar() as conexao:
            try:
                conexao.execute("ALTER TABLE identificacoes ADD COLUMN start_date TEXT")
                conexao.commit()
            except sqlite3.OperationalError:
                pass
        # Tenta consultar novamente após criar a coluna
        dados = consultar(sql_consulta)

    return pd.DataFrame(dados)




def campo_selecao(
    titulo,
    nome_lista,
    valor_atual="",
):
    opcoes = [""] + LISTAS.get(nome_lista, [])

    if valor_atual and valor_atual not in opcoes:
        opcoes.append(valor_atual)

    indice = (
        opcoes.index(valor_atual)
        if valor_atual in opcoes
        else 0
    )

    return st.selectbox(
        titulo,
        opcoes,
        index=indice,
    )


# ============================================================
# DASHBOARD
# ============================================================

def pagina_dashboard():
    # --------------------------------------------------------
    # ESTILIZAÇÃO E TÍTULOS
    # --------------------------------------------------------
    st.markdown(
        """
        <style>
        .titulo-relatorio {
            text-align: center; 
            letter-spacing: 2px; 
            margin-bottom: 5px;
            color: #16857a;
            font-weight: bold;
        }
        .subtitulo-relatorio {
            text-align: center; 
            color: #666666; 
            letter-spacing: 1px; 
            margin-top: 0px; 
            margin-bottom: 30px;
            font-size: 16px;
        }
        /* Estilização para os cards de Limite de Ação / Status */
        .card-status {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1 class='titulo-relatorio'>SISTEMA DE MONITORAMENTO BIOLÓGICO</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-relatorio'>ANÁLISE E CONTROLE DE CONTAMINANTES AMBIENTAIS</p>", unsafe_allow_html=True)

    # 1. Busca abrangente de dados do banco
    df_completo = consultar(
        """
        SELECT
            a.code,
            a.origin,
            a.area,
            a.sample,
            a.collection_point,
            a.frequencia,
            a.resultado_final,
            a.data,
            i.identification,
            i.gram_stain
        FROM amostras a
        LEFT JOIN identificacoes i ON i.code = a.code
        """
    )
    
    df = pd.DataFrame(df_completo)

    if df.empty:
        st.info("Nenhuma amostra cadastrada no banco de dados.")
        return

    # --------------------------------------------------------
    # CRIAÇÃO DAS ABAS ENRIQUECIDAS
    # --------------------------------------------------------
    aba_tendencia, aba_tanques, aba_auditoria = st.tabs([
        "📊 Relatório de Tendência", 
        "🏭 Controle por Áreas e Tanques",
        "🛡️ Indicadores Avançados e Auditoria"
    ])

    # ========================================================
    # ABA 1: RELATÓRIO DE TENDÊNCIA PADRÃO
    # ========================================================
    with aba_tendencia:
        df_identificados = df[df["identification"].str.strip() != ""].copy()
        if not df_identificados.empty:
            total_identificados = len(df_identificados)
            resumo = df_identificados["identification"].value_counts().reset_index()
            resumo.columns = ["Microrganismo", "Contagem"]
            resumo["Frequência"] = (resumo["Contagem"] / total_identificados * 100).round(1).astype(str) + "%"
            
            grams, esporulados, ecologias, patogenicidades = [], [], [], []
            for micro in resumo["Microrganismo"]:
                if "Staphylococcus" in micro or "epidermidis" in micro.lower() or "hominis" in micro.lower():
                    grams.append("C+"); esporulados.append("Não"); ecologias.append("Microbiota normal da pele e mucosas"); patogenicidades.append("Não-patogênico")
                elif "Bacillus" in micro:
                    grams.append("B+"); esporulados.append("Sim"); ecologias.append("Comumente encontrado em solo"); patogenicidades.append("Patogenicidade variada")
                elif "Micrococcus" in micro or "luteus" in micro.lower():
                    grams.append("C+"); esporulados.append("Não"); ecologias.append("Comumente encontrada em ar, solo e pele"); patogenicidades.append("Não-patogênico")
                else:
                    grams.append("N/A"); esporulados.append("Não"); ecologias.append("Ambiente geral / Dispersão aérea"); patogenicidades.append("Variada")
            
            resumo["Gram"], resumo["Esporulado"], resumo["Ecologia"], resumo["Patogenicidade"] = grams, esporulados, ecologias, patogenicidades
            st.dataframe(resumo[["Microrganismo", "Frequência", "Gram", "Esporulado", "Ecologia", "Patogenicidade"]], use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            if not df_identificados.empty:
                fig_p = px.pie(df_identificados["identification"].value_counts().reset_index(), names="identification", values="count", hole=0.4, title="Distribuição dos micro-organismos", color_discrete_sequence=px.colors.qualitative.Safe)
                fig_p.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#333333"), title_font=dict(size=14, color="#16857a"))
                st.plotly_chart(fig_p, use_container_width=True)
        with g2:
            df_pontos = df[df["collection_point"].str.strip() != ""].copy()
            if not df_pontos.empty:
                fig_b = px.bar(df_pontos["collection_point"].value_counts().reset_index(), x="collection_point", y="count", text_auto=True, title="Frequência dos locais isolados", color_discrete_sequence=["#16857a"])
                fig_b.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#333333"), title_font=dict(size=14, color="#16857a"))
                st.plotly_chart(fig_b, use_container_width=True)

    # ========================================================
    # ABA 2: CONTROLE POR ÁREAS E TANQUES
    # ========================================================
    with aba_tanques:
        st.subheader("🔍 Rastreabilidade e Auditoria por Setor")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_origem = st.selectbox("Filtrar por Origem do Monitoramento:", ["Todos"] + list(df["origin"].dropna().unique()))
        with col_f2:
            filtro_conformidade = st.selectbox("Filtrar por Status de Conformidade:", ["Todos", "Conforme", "Não Conforme"])
        
        df_filtrado = df.copy()
        if filtro_origem != "Todos":
            df_filtrado = df_filtrado[df_filtrado["origin"] == filtro_origem]
        if filtro_conformidade != "Todos":
            df_filtrado = df_filtrado[df_filtrado["resultado_final"] == filtro_conformidade]
            
        c1, c2, c3 = st.columns(3)
        c1.metric("Amostras Avaliadas no Filtro", len(df_filtrado))
        c2.metric("Pontos Críticos Identificados", df_filtrado["collection_point"].nunique())
        c3.metric("Ocorrências Não Conformes", int((df_filtrado["resultado_final"] == "Não Conforme").sum()))
        
        st.write("---")
        g_areas, g_conformidade = st.columns(2)
        with g_areas:
            fig_areas = px.bar(df_filtrado["area"].value_counts().reset_index(), y="area", x="count", orientation="h", text_auto=True, title="<b>Volume de Ocorrências por Área / Tanque</b>", color_discrete_sequence=["#2a6f68"])
            fig_areas.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_areas, use_container_width=True)
        with g_conformidade:
            df_status = df_filtrado.groupby(["collection_point", "resultado_final"]).size().reset_index(name="Quantidade")
            fig_status = px.bar(df_status, x="collection_point", y="Quantidade", color="resultado_final", title="<b>Conformidade por Ponto de Coleta Crítico</b>", barmode="stack", color_discrete_map={"Conforme": "#6bb1a9", "Não Conforme": "#d9534f", "": "#999999"})
            fig_status.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Amostras")
            st.plotly_chart(fig_status, use_container_width=True)

        st.subheader("Lista Filtrada de Isolados")
        st.dataframe(df_filtrado[["code", "origin", "area", "collection_point", "identification", "resultado_final", "data"]], use_container_width=True, hide_index=True)

    # ========================================================
    # ABA 3: NOVA ABA AVANÇADA (SISTEMA DE ALERTA, HEATMAP E PDF)
    # ========================================================
    with aba_auditoria:
        st.subheader("🛡️ Gestão de Riscos e Validação de Processos")
        
        # 1. SISTEMA DE ALERTA DINÂMICO (LIMITE DE AÇÃO)
        nao_conformes_totais = (df["resultado_final"] == "Não Conforme").sum()
        
        card_1, card_2 = st.columns(2)
        with card_1:
            if nao_conformes_totais <= 2:
                st.markdown('<div class="card-status" style="background-color: #28a745;">🟢 STATUS DO BIOBANCO: NORMAL<br><span style="font-size:12px; font-weight:normal;">Dentro do Limite de Alerta aceitável.</span></div>', unsafe_allow_html=True)
            elif nao_conformes_totais <= 4:
                st.markdown('<div class="card-status" style="background-color: #ffc107; color: #333;">🟡 STATUS DO BIOBANCO: ALERTA<br><span style="font-size:12px; font-weight:normal;">Aumento de desvios. Revisar desinfecção.</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card-status" style="background-color: #dc3545;">🔴 STATUS DO BIOBANCO: CRÍTICO<br><span style="font-size:12px; font-weight:normal;">Limite de Ação violado. Exige sanitização emergencial!</span></div>', unsafe_allow_html=True)
        
        # 2. ÍNDICE DE EFICIÊNCIA DE LIMPEZA
        with card_2:
            total_avaliadas = len(df)
            conformes = (df["resultado_final"] == "Conforme").sum()
            taxa_eficiencia = round((conformes / total_avaliadas) * 100, 1) if total_avaliadas > 0 else 100.0
            
            st.markdown(f'<div class="card-status" style="background-color: #16857a;">🧼 EFICIÊNCIA DE SANITIZAÇÃO: {taxa_eficiencia}%<br><span style="font-size:12px; font-weight:normal;">Proporção de pontos validados como livres de contaminação.</span></div>', unsafe_allow_html=True)
            
        st.write("---")
         # ========================================================
    # ABA 3: NOVA ABA AVANÇADA (SISTEMA DE ALERTA, HEATMAP E PDF)
    # ========================================================
    with aba_auditoria:
        st.subheader("🛡️ Gestão de Riscos e Validação de Processos")
        
        # 1. SISTEMA DE ALERTA DINÂMICO (LIMITE DE AÇÃO)
        nao_conformes_totais = (df["resultado_final"] == "Não Conforme").sum()
        
        card_1, card_2 = st.columns(2)
        with card_1:
            if nao_conformes_totais <= 2:
                st.markdown('<div class="card-status" style="background-color: #28a745;">🟢 STATUS DO BIOBANCO: NORMAL<br><span style="font-size:12px; font-weight:normal;">Dentro do Limite de Alerta aceitável.</span></div>', unsafe_allow_html=True)
            elif nao_conformes_totais <= 4:
                st.markdown('<div class="card-status" style="background-color: #ffc107; color: #333;">🟡 STATUS DO BIOBANCO: ALERTA<br><span style="font-size:12px; font-weight:normal;">Aumento de desvios. Revisar desinfecção.</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card-status" style="background-color: #dc3545;">🔴 STATUS DO BIOBANCO: CRÍTICO<br><span style="font-size:12px; font-weight:normal;">Limite de Ação violado. Exige sanitização emergencial!</span></div>', unsafe_allow_html=True)
        
        # 2. ÍNDICE DE EFICIÊNCIA DE LIMPEZA
        with card_2:
            total_avaliadas = len(df)
            conformes = (df["resultado_final"] == "Conforme").sum()
            taxa_eficiencia = round((conformes / total_avaliadas) * 100, 1) if total_avaliadas > 0 else 100.0
            
            st.markdown(f'<div class="card-status" style="background-color: #16857a;">🧼 EFICIÊNCIA DE SANITIZAÇÃO: {taxa_eficiencia}%<br><span style="font-size:12px; font-weight:normal;">Proporção de pontos validados como livres de contaminação.</span></div>', unsafe_allow_html=True)
     
    # ========================================================
    # ABA 3: INDICADORES AVANÇADOS E AUDITORIA (SEM DUPLICAÇÃO)
    # ========================================================
    with aba_auditoria:
        # 1. SISTEMA DE ALERTA DINÂMICO (LIMITE DE AÇÃO)
        nao_conformes_totais = (df["resultado_final"] == "Não Conforme").sum()
        
        card_1, card_2 = st.columns(2)
        with card_1:
            if nao_conformes_totais <= 2:
                st.markdown('<div class="card-status" style="background-color: #28a745;">🟢 STATUS DO BIOBANCO: NORMAL<br><span style="font-size:12px; font-weight:normal;">Dentro do Limite de Alerta aceitável.</span></div>', unsafe_allow_html=True)
            elif nao_conformes_totais <= 4:
                st.markdown('<div class="card-status" style="background-color: #ffc107; color: #333;">🟡 STATUS DO BIOBANCO: ALERTA<br><span style="font-size:12px; font-weight:normal;">Aumento de desvios. Revisar desinfecção.</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card-status" style="background-color: #dc3545;">🔴 STATUS DO BIOBANCO: CRÍTICO<br><span style="font-size:12px; font-weight:normal;">Limite de Ação violado. Exige sanitização emergencial!</span></div>', unsafe_allow_html=True)
        
        # 2. ÍNDICE DE EFICIÊNCIA DE LIMPEZA
        with card_2:
            total_avaliadas = len(df)
            conformes = (df["resultado_final"] == "Conforme").sum()
            taxa_eficiencia = round((conformes / total_avaliadas) * 100, 1) if total_avaliadas > 0 else 100.0
            
            st.markdown(f'<div class="card-status" style="background-color: #16857a;">🧼 EFICIÊNCIA DE SANITIZAÇÃO: {taxa_eficiencia}%<br><span style="font-size:12px; font-weight:normal;">Proporção de pontos validados como livres de contaminação.</span></div>', unsafe_allow_html=True)
            
        st.write("---")
        
        # 3. MAPA DE CALOR (HEATMAP CROSS-TABLE)
        st.markdown("##### 🗺️ Mapa de Calor: Concentração de Microrganismos por Ponto Crítico")
        df_heatmap_raw = df[(df["collection_point"].str.strip() != "") & (df["identification"].str.strip() != "")]
        
        if not df_heatmap_raw.empty:
            matriz_contagem = pd.crosstab(df_heatmap_raw["collection_point"], df_heatmap_raw["identification"])
            
            fig_heatmap = px.imshow(
                matriz_contagem,
                text_auto=True,
                labels=dict(x="Microrganismo Isolado", y="Ponto de Coleta", color="Ocorrências"),
                color_continuous_scale="Tealrose"
            )
            fig_heatmap.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#333333"),
                title_font=dict(size=14, color="#16857a")
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar a matriz de correlação cruzada.")
            
        st.write("---")
        
        # 4. EXPORTAÇÃO RÁPIDA DE AUDITORIA (CONSOLIDADA EM EXCEL)
        st.markdown("##### 📄 Central de Relatórios para Fiscais e Auditores")
        st.caption("Gere instantaneamente o arquivo consolidado de dados biológicos para apresentação em inspeções da Vigilância Sanitária.")
        
        st.download_button(
            label="📥 Exportar Relatório de Auditoria Consolidado",
            data=gerar_excel(),
            file_name="relatorio_auditoria_biobanco.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


# ============================================================
# REGISTRO DE AMOSTRAS
# ============================================================

def pagina_identificacao():
    st.title("Identificação Microbiológica")

    df = obter_identificacoes()

    if df.empty:
        st.info(
            "Cadastre uma amostra antes "
            "de preencher a identificação."
        )
        return

    code = st.selectbox(
        "Selecione o CODE",
        df["code"].tolist(),
    )

    registro = (
        df[df["code"] == code]
        .iloc[0]
        .fillna("")
        .to_dict()
    )

    st.info(
        f"Área: {registro.get('area', '—')} | "
        f"Ponto: {registro.get('collection_point', '—')} | "
        f"Data: {registro.get('data', '—')}"
    )

    with st.form("formulario_identificacao"):
        coluna1, coluna2 = st.columns(2)

        with coluna1:
            form = campo_selecao(
                "MORPHOLOGY",
                "FORM",
                registro.get("form", ""),
            )

            gram_stain = campo_selecao(
                "GRAM STAIN",
                "AFFIRMATION",
                registro.get("gram_stain", ""),
            )

            identification = st.text_input(
                "IDENTIFICATION",
                registro.get("identification", ""),
            )

            # Lista suspensa de método terceirizado em inglês
            opcoes_metodo = ["", "NGS Sequencing", "Maldi TOF", "Others"]
            valor_salvo = registro.get("outsourced_method", "")
            
            if valor_salvo == "Sequenciamento NGS": valor_salvo = "NGS Sequencing"
            if valor_salvo == "Outros": valor_salvo = "Others"
            
            if valor_salvo not in opcoes_metodo:
                opcoes_metodo.append(valor_salvo)
                
            indice_metodo = opcoes_metodo.index(valor_salvo) if valor_salvo in opcoes_metodo else 0
            
            outsourced_method = st.selectbox(
                "OUTSOURCED METHOD",
                opcoes_metodo,
                index=indice_metodo
            )

        with coluna2:
            company = st.text_input(
                "COMPANY",
                registro.get("company", ""),
            )

            col_data1, col_data2 = st.columns(2)

            with col_data1:
                data_inicio_atual = pd.to_datetime(
                    registro.get("start_date", ""),
                    errors="coerce",
                )
                start_date = st.date_input(
                    "START DATE",
                    value=(
                        None
                        if pd.isna(data_inicio_atual)
                        else data_inicio_atual.date()
                    ),
                    format="DD/MM/YYYY",
                )

            with col_data2:
                data_final_atual = pd.to_datetime(
                    registro.get("end_date", ""),
                    errors="coerce",
                )
                end_date = st.date_input(
                    "END DATE",
                    value=(
                        None
                        if pd.isna(data_final_atual)
                        else data_final_atual.date()
                    ),
                    format="DD/MM/YYYY",
                )

            arquivo_anexo = st.file_uploader(
                "ATTACH REPORT (Word, Excel, Foto ou PDF)",
                type=["doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "pdf"]
            )
            
            remover_anexo = st.checkbox("❌ Remover anexo atual desta amostra")

        enviado = st.form_submit_button(
            "Salvar identificação",
            type="primary",
            use_container_width=True,
        )

    nome_arquivo_salvo = registro.get("report", "")
    
    if nome_arquivo_salvo:
        st.markdown(f"📎 **Arquivo anexado atual:** `{nome_arquivo_salvo}`")
        
        bytes_reais = None
        with conectar() as conexao:
            try:
                _cursor = conexao.execute("SELECT report_data FROM identificacoes WHERE code = ?", (code,))
                _linha = _cursor.fetchone()
                if _linha and _linha["report_data"]:
                    bytes_reais = _linha["report_data"]
            except sqlite3.OperationalError:
                conexao.execute("ALTER TABLE identificacoes ADD COLUMN report_data BLOB")
                conexao.commit()

        if bytes_reais and len(bytes_reais) > 100:
            st.download_button(
                label=f"📥 Baixar/Abrir Documento Físico: {nome_arquivo_salvo}",
                data=bytes_reais,
                file_name=nome_arquivo_salvo,
                mime="application/octet-stream",
                use_container_width=True
            )
        else:
            st.warning("⚠️ O arquivo antigo continha apenas metadados de texto. Faça um novo upload no campo acima para registrar o arquivo físico.")
    else:
        st.caption("ℹ️ Nenhum documento ou foto foi anexado para esta amostra ainda.")

    if enviado:
        if remover_anexo:
            nome_relatorio = ""
            bytes_arquivo = None
            atualizar_dados_arquivo = True
        elif arquivo_anexo is not None:
            nome_relatorio = arquivo_anexo.name
            bytes_arquivo = arquivo_anexo.getvalue()
            atualizar_dados_arquivo = True
        else:
            nome_relatorio = registro.get("report", "")
            bytes_arquivo = None
            atualizar_dados_arquivo = False

        with conectar() as conexao:
            try: conexao.execute("ALTER TABLE identificacoes ADD COLUMN report_data BLOB"); conexao.commit()
            except sqlite3.OperationalError: pass
            try: conexao.execute("ALTER TABLE identificacoes ADD COLUMN start_date TEXT"); conexao.commit()
            except sqlite3.OperationalError: pass

        sql_salvar = f"""
            INSERT INTO identificacoes (
                code, form, margin, pigment, gram_stain, catalase, koh, oxidase,
                outsourced_method, identification, report, company, end_date, report_data, start_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                form=excluded.form,
                gram_stain=excluded.gram_stain,
                identification=excluded.identification,
                company=excluded.company,
                end_date=excluded.end_date,
                report={"excluded.report" if atualizar_dados_arquivo else "identificacoes.report"},
                report_data={"excluded.report_data" if atualizar_dados_arquivo else "identificacoes.report_data"},
                start_date=excluded.start_date,
                outsourced_method=excluded.outsourced_method,
                atualizado_em=CURRENT_TIMESTAMP
        """

        valores = (
            code, form, registro.get("margin", ""), registro.get("pigment", ""), gram_stain,
            registro.get("catalase", ""), registro.get("koh", ""), registro.get("oxidase", ""),
            outsourced_method, identification, nome_relatorio, company,
            (end_date.isoformat() if end_date else ""), bytes_arquivo,
            (start_date.isoformat() if start_date else "")
        )

        with conectar() as conexao:
            conexao.execute(sql_salvar, valores)

        st.success(f"Identificação de {code} salva com sucesso!")
        st.rerun()

    st.subheader("Identificações cadastradas")

    colunas_visiveis = [
        "code", "area", "collection_point", "data", 
        "form", "gram_stain", "identification", "outsourced_method", "report", "company", "start_date", "end_date"
    ]
    df_filtrado = df[[col for col in colunas_visiveis if col in df.columns]]

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
        column_config={
            "code": "CODE",
            "area": "AREA",
            "collection_point": "COLLECTION POINT",
            "data": "DATE",
            "form": "MORPHOLOGY",
            "gram_stain": "GRAM STAIN",
            "identification": "IDENTIFICATION",
            "outsourced_method": "OUTSOURCED METHOD",
            "report": "ATTACH REPORT",
            "company": "COMPANY",
            "start_date": "START DATE",
            "end_date": "END DATE"
        }
    )


# ============================================================
# IDENTIFICAÇÃO MICROBIOLÓGICA
# ============================================================
def campo_selecao(titulo, nome_lista, valor_atual=""):
    opcoes = [""] + LISTAS.get(nome_lista, [])

    if valor_atual and valor_atual not in opcoes:
        opcoes.append(valor_atual)

    indice = (
        opcoes.index(valor_atual)
        if valor_atual in opcoes
        else 0
    )

    return st.selectbox(
        titulo,
        opcoes,
        index=indice,
    )



# ============================================================
# ABA REGISTRO ATIVADA DE VOLTA (RESOLVE O NAMEERROR)
# ============================================================

def pagina_registro():
    st.title("Registro de Monitoramento")
    df = obter_amostras()
    codigos = df["code"].tolist() if not df.empty else []
    
    # 🎛️ Adicionada a opção de Excluir de volta no menu de rádio
    modo = st.radio("Ação", ["Novo registro", "Editar registro", "Excluir registro"], horizontal=True)
    
    # 🩹 Carrega as informações se for editar ou excluir
    reg = df[df["code"] == st.selectbox("Selecione o CODE", codigos)].iloc[0].fillna("").to_dict() if modo in ["Editar registro", "Excluir registro"] and codigos else {}
    
    # ============================================================
    # MODO EXCLUIR REGISTRO (TELA EXCLUSIVA)
    # ============================================================
    if modo == "Excluir registro":
        if not codigos:
            st.info("Nenhum registro encontrado para excluir.")
            return
            
        st.warning(f"⚠️ Atenção: Você está prestes a excluir definitivamente a amostra {reg.get('code')}.")
        st.markdown(
            f"""
            * **Origem:** {reg.get('origin', '—')}
            * **Área:** {reg.get('area', '—')}
            * **Data de Coleta:** {reg.get('data', '—')}
            * **Resultado:** {reg.get('resultado_final', '—')}
            """
        )
        
        # Botão com confirmação para evitar cliques acidentais
        confirmar_exclusao = st.checkbox(f"Confirmo que quero deletar permanentemente a amostra {reg.get('code')}")
        
        if st.button("❌ Deletar Registro Permanentemente", type="primary", disabled=not confirmar_exclusao, use_container_width=True):
            excluir_amostra(reg.get("code"))
            st.success(f"Amostra {reg.get('code')} deletada com sucesso!")
            st.rerun()
            
        st.divider()

    # ============================================================
    # MODO NOVO / EDITAR REGISTRO
    # ============================================================
    else:
        with st.form("form_amostra"):
            col1, col2, col3 = st.columns(3)
            
            # 🤖 GERAÇÃO AUTOMÁTICA DO PRÓXIMO CODE
            if modo == "Novo registro":
                ultimo_registro = consultar("SELECT code FROM amostras ORDER BY code DESC LIMIT 1")
                if ultimo_registro and len(ultimo_registro) > 0:
                    ultimo_code = ultimo_registro[0]["code"]  # Acessa o dicionário dentro da lista retornada
                    try:
                        prefixo, numero = ultimo_code.split("-")
                        proximo_numero = int(numero) + 1
                        code_sugerido = f"{prefixo}-{proximo_numero:03d}"
                    except ValueError:
                        code_sugerido = "B4-006"
                else:
                    code_sugerido = "B4-001"
                    
                code = col1.text_input("CODE *", value=code_sugerido)
            else:
                code = col1.text_input("CODE *", reg.get("code", ""), disabled=True)
                
            ponto = col2.text_input("OBSERVATION", reg.get("ponto", ""))
            analista = col3.text_input("ANALYST", reg.get("analista", ""))
            
            col4, col5, col6 = st.columns(3)
            with col4: origin = campo_selecao("ORIGIN", "ORIGIN", reg.get("origin", ""))
            with col5: sample = campo_selecao("SAMPLE", "SAMPLE", reg.get("sample", ""))
            with col6: sampling = campo_selecao("SAMPLING", "SAMPLING", reg.get("sampling", ""))
                
            col7, col8, col9 = st.columns(3)
            with col7: area = campo_selecao("AREA", "AREA", reg.get("area", ""))
            with col8: collection_point = campo_selecao("COLLECTION POINT", "COLLECTION POINT", reg.get("collection_point", ""))
            with col9: method = campo_selecao("METHOD", "METHOD", reg.get("method", ""))
                
            col10, col11, col12 = st.columns(3)
            with col10: frequencia = st.selectbox("FREQUENCY", ["", "Semanal", "Mensal"], index=["", "Semanal", "Mensal"].index(reg.get("frequencia", "")) if reg.get("frequencia", "") in ["", "Semanal", "Mensal"] else 0)
            with col11:
                dt_at = pd.to_datetime(reg.get("data", ""), errors="coerce")
                data = st.date_input("DATA", value=None if pd.isna(dt_at) else dt_at.date(), format="DD/MM/YYYY")
            with col12: resultado_final = st.selectbox("RESULT", ["", "Conforme", "Não Conforme"], index=["", "Conforme", "Não Conforme"].index(reg.get("resultado_final", "")) if reg.get("resultado_final", "") in ["", "Conforme", "Não Conforme"] else 0)
            
            enviado_reg = st.form_submit_button("Salvar Registro", type="primary")

        if enviado_reg and code.strip():
            salvar_amostra({"code": code.strip(), "ponto": ponto, "origin": origin, "area": area, "sample": sample, "collection_point": collection_point, "sampling": sampling, "method": method, "frequencia": frequencia, "analista": analista, "data": data.isoformat() if data else "", "resultado_final": resultado_final})
            st.success("Registro Corretamente Salvo!")
            st.rerun()

    # ============================================================
    # VISUALIZAÇÃO DA TABELA (COMUM A TODOS OS MODOS)
    # ============================================================
    st.subheader("Amostras cadastradas")
    config_colunas = {
        "code": "CODE", "ponto": "OBSERVATION", "origin": "ORIGIN", "area": "AREA", 
        "sample": "SAMPLE", "collection_point": "COLLECTION POINT", "sampling": "SAMPLING", 
        "method": "METHOD", "frequencia": "FREQUENCY", "analista": "ANALYST", "data": "DATA", 
        "resultado_final": "RESULT"
    }
    st.dataframe(df, use_container_width=True, hide_index=True, column_config=config_colunas)









# ============================================================
# ARMAZENAMENTO
# ============================================================


def mapa_caixa():

    st.markdown("##### Posições")

    for linha in range(9):

        texto = ""

        for coluna in range(9):

            pos = linha * 9 + coluna + 1
def salvar_armazenamento(
    code,
    box,
    backup_box,
    freezer,
    storage_date,
    analyst,
    backup_used,
    posicao=None,
    posicao_backup=None
):
    with conectar() as conexao:
        try: conexao.execute("ALTER TABLE armazenamento_cepas ADD COLUMN posicao INTEGER"); conexao.commit()
        except sqlite3.OperationalError: pass
        try: conexao.execute("ALTER TABLE armazenamento_cepas ADD COLUMN posicao_backup INTEGER"); conexao.commit()
        except sqlite3.OperationalError: pass

        conexao.execute("""
            INSERT OR REPLACE INTO armazenamento_cepas (
                code, box, backup_box, freezer, storage_date, analyst, backup_used, posicao, posicao_backup
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code, box, backup_box, freezer, storage_date, analyst, backup_used, posicao, posicao_backup
        ))

def excluir_armazenamento(code):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM armazenamento_cepas WHERE code = ?",
            (code,)
        )

def obter_armazenamento():
    with conectar() as conexao:
        try: conexao.execute("ALTER TABLE armazenamento_cepas ADD COLUMN posicao INTEGER")
        except sqlite3.OperationalError: pass
        try: conexao.execute("ALTER TABLE armazenamento_cepas ADD COLUMN posicao_backup INTEGER")
        except sqlite3.OperationalError: pass
        return pd.read_sql_query("SELECT * FROM armazenamento_cepas", conexao)

def pagina_armazenamento():
    st.title("🧫 Armazenamento de Isolados Identificados")
    st.caption("Gestão do banco de cepas e rastreabilidade dos isolados.")

    df = obter_identificacoes()
    if df.empty:
        st.info("Cadastre uma amostra antes de preencher a identificação.")
        return

    df_filtrado = df[df["identification"].fillna("").str.strip() != ""].copy()
    if df_filtrado.empty:
        st.info("Nenhum microrganismo identificado disponível.")
        return

    codigos = sorted(df_filtrado["code"].unique())
    dados = obter_armazenamento()

    modo = st.radio("Ação", ["Novo Registro", "Editar Registro", "Excluir Registro"], horizontal=True)
    registro = {}

    if modo in ["Editar Registro", "Excluir Registro"] and not dados.empty:
        codigo_selecionado = st.selectbox("Selecione o CODE", dados["code"].tolist(), key="sb_code_edicao")
        registro = dados[dados["code"] == codigo_selecionado].iloc.to_dict()

    if modo == "Excluir Registro":
        if dados.empty:
            st.info("Nenhum registro encontrado.")
            return

        st.warning(f"⚠️ O registro {registro.get('code','')} será removido permanentemente.")
        confirmar = st.checkbox("Confirmo a exclusão deste registro")

        if st.button("🗑️ Excluir Registro", disabled=not confirmar, use_container_width=True):
            excluir_armazenamento(registro.get("code"))
            st.toast("Registro excluído com sucesso! ✅")
            st.rerun()

    else:
        with st.form("form_armazenamento"):
            if modo == "Novo Registro":
                code = st.selectbox("Code", codigos)
                valor_box = "C1"
                valor_backup_box = "C1"
                valor_freezer = ""
                valor_analyst = ""
                valor_backup_used = "No"
                pos_salva_principal = None
                pos_salva_backup = None
            else:
                code = st.text_input("Code", value=str(registro.get("code", "")), disabled=True)
                valor_box = str(registro.get("box", "C1"))
                valor_backup_box = str(registro.get("backup_box", "C1"))
                valor_freezer = str(registro.get("freezer", ""))
                valor_analyst = str(registro.get("analyst", ""))
                valor_backup_used = str(registro.get("backup_used", "No"))
                pos_salva_principal = registro.get("posicao")
                pos_salva_backup = registro.get("posicao_backup")

            col1, col2 = st.columns(2)
            with col1:
                freezer = st.text_input("Freezer", value=valor_freezer)
                analyst = st.text_input("Analyst", value=valor_analyst)
            with col2:
                dt_at = pd.to_datetime(registro.get("storage_date", ""), errors="coerce")
                storage_date = st.date_input("Storage Date", value=None if pd.isna(dt_at) else dt_at.date(), format="DD/MM/YYYY")
                backup_used = st.selectbox("Backup Used", ["No", "Yes"], index=0 if valor_backup_used == "No" else 1)

            st.markdown("---")
            
            # Espaçamento lateral controlado entre as colunas
            col_box_principal, col_espaco, col_box_backup = st.columns([1, 0.1, 1])

            # --- 📦 CAIXA PRINCIPAL ---
            with col_box_principal:
                st.subheader("📦 Caixa Principal")
                st.markdown("<p style='font-size:12px; margin-top:-10px; color:#7f8c8d;'>🟢 Livre | 🔵 Selecionado | 🔴 Ocupado</p>", unsafe_allow_html=True)
                
                box = st.selectbox("Box", ["C1", "C2", "C3", "C4", "C5"], index=["C1", "C2", "C3", "C4", "C5"].index(valor_box) if valor_box in ["C1", "C2", "C3", "C4", "C5"] else 0, key="sb_box_main")
                
                dados_persistidos = obter_armazenamento()
                ocupadas_main = {}
                if not dados_persistidos.empty:
                    for _, reg_db in dados_persistidos.iterrows():
                        b_banco = str(reg_db.get("box")).strip()
                        p_banco = str(reg_db.get("posicao")).strip()
                        c_banco = str(reg_db.get("code")).strip()
                        if b_banco == str(box).strip() and p_banco != "" and p_banco != "None":
                            ocupadas_main[int(float(p_banco))] = c_banco
                
                if modo == "Editar Registro" and pos_salva_principal:
                    try: ocupadas_main.pop(int(float(pos_salva_principal)), None)
                    except ValueError: pass

                opcoes_pos_main = [""] + [p for p in range(1, 82) if p not in ocupadas_main]
                idx_main = 0
                if pos_salva_principal:
                    try:
                        p_int = int(float(pos_salva_principal))
                        if p_int in opcoes_pos_main: idx_main = opcoes_pos_main.index(p_int)
                    except ValueError: pass
                
                posicao_escolhida_main = st.selectbox(
                    f"Posição na Caixa {box} *",
                    opcoes_pos_main,
                    index=idx_main,
                    format_func=lambda x: f"Posição {x:02d}" if x != "" else "Escolha uma posição...",
                    key="pos_main_select"
                )

                st.markdown("<p style='font-size:13px; font-weight:bold; color:#612147; margin-top:10px; margin-bottom:5px;'>Mapa de Ocupação:</p>", unsafe_allow_html=True)
                for i in range(0, 81, 9):
                    cols_m = st.columns(9)
                    for j in range(9):
                        pos = i + j + 1
                        if posicao_escolhida_main != "" and pos == int(posicao_escolhida_main):
                            cor = "#3498db"
                            label_html = f"🔵 {pos:02d}"
                        elif pos in ocupadas_main:
                            cor = "#e74c3c"
                            label_html = f"🔴 {pos:02d}"
                        else:
                            cor = "#2ecc71"
                            label_html = f"🟢 {pos:02d}"
                        cols_m[j].markdown(f"<div style='text-align:center; font-size:11px; font-weight:bold; color:{cor}; margin:2px 0;'>{label_html}</div>", unsafe_allow_html=True)

            # --- 🛡️ CAIXA DE BACKUP ---
            with col_box_backup:
                st.subheader("🛡️ Caixa de Backup")
                st.markdown("<p style='font-size:12px; margin-top:-10px; color:#7f8c8d;'>🟢 Livre | 🔵 Selecionado | 🔴 Ocupado</p>", unsafe_allow_html=True)
                
                backup_box = st.selectbox("Backup Box", ["C1", "C2", "C3", "C4", "C5"], index=["C1", "C2", "C3", "C4", "C5"].index(valor_backup_box) if valor_backup_box in ["C1", "C2", "C3", "C4", "C5"] else 0, key="sb_box_backup")
                
                ocupadas_backup = {}
                if not dados_persistidos.empty:
                    for _, reg_db in dados_persistidos.iterrows():
                        b_banco = str(reg_db.get("backup_box")).strip()
                        p_banco = str(reg_db.get("posicao_backup")).strip()
                        c_banco = str(reg_db.get("code")).strip()
                        if b_banco == str(backup_box).strip() and p_banco != "" and p_banco != "None":
                            ocupadas_backup[int(float(p_banco))] = c_banco

                if modo == "Editar Registro" and pos_salva_backup:
                    try: ocupadas_backup.pop(int(float(pos_salva_backup)), None)
                    except ValueError: pass

                opcoes_pos_backup = [""] + [p for p in range(1, 82) if p not in ocupadas_backup]
                idx_backup = 0
                if pos_salva_backup:
                    try:
                        p_int = int(float(pos_salva_backup))
                        if p_int in opcoes_pos_backup: idx_backup = opcoes_pos_backup.index(p_int)
                    except ValueError: pass

                posicao_escolhida_backup = st.selectbox(
                    f"Posição na Caixa de Backup {backup_box} *",
                    opcoes_pos_backup,
                    index=idx_backup,
                    format_func=lambda x: f"Posição {x:02d}" if x != "" else "Escolha uma posição...",
                    key="pos_backup_select"
                )

                st.markdown("<p style='font-size:13px; font-weight:bold; color:#612147; margin-top:10px; margin-bottom:5px;'>Mapa de Ocupação:</p>", unsafe_allow_html=True)
                for i in range(0, 81, 9):
                    cols_b = st.columns(9)
                    for j in range(9):
                        pos = i + j + 1
                        if posicao_escolhida_backup != "" and pos == int(posicao_escolhida_backup):
                            cor = "#3498db"
                            label_html = f"🔵 {pos:02d}"
                        elif pos in ocupadas_backup:
                            cor = "#e74c3c"
                            label_html = f"🔴 {pos:02d}"
                        else:
                            cor = "#2ecc71"
                            label_html = f"🟢 {pos:02d}"
                        cols_b[j].markdown(f"<div style='text-align:center; font-size:11px; font-weight:bold; color:{cor}; margin:2px 0;'>{label_html}</div>", unsafe_allow_html=True)

            st.markdown("---")
            salvar = st.form_submit_button("💾 Salvar Registro")

            if salvar:
                if posicao_escolhida_main == "" or posicao_escolhida_backup == "":
                    st.error("Por favor, selecione as posições obrigatórias nos campos de seleção antes de salvar!")
                else:
                    dt_iso = storage_date.isoformat() if storage_date else ""
                    salvar_armazenamento(code, box, backup_box, freezer, dt_iso, analyst, backup_used, int(posicao_escolhida_main), int(posicao_escolhida_backup))
    dados = obter_armazenamento()
    if not dados.empty:
        total_isolados = len(dados)
        st.metric("🦠 Total de Isolados Preservados no Banco", f"{total_isolados} un")

        colunas_existentes = dados.columns
        mapeamento = {
            "code": "CODE", "box": "BOX", "posicao": "POSITION",
            "backup_box": "BACKUP BOX", "posicao_backup": "BACKUP POSITION",
            "freezer": "FREEZER", "storage_date": "STORAGE DATE",
            "analyst": "ANALYST", "backup_used": "BACKUP USED"
        }
        mapeamento_valido = {k: v for k, v in mapeamento.items() if k in colunas_existentes}
        dados_exibicao = dados.rename(columns=mapeamento_valido)
        colunas_exibir = [v for k, v in mapeamento_valido.items() if v in dados_exibicao.columns]

        if colunas_exibir:
            st.dataframe(dados_exibicao[colunas_exibir], use_container_width=True, hide_index=True)


# ============================================================
# IMPORTAÇÃO DE EXCEL
# ============================================================

def normalizar_coluna(nome):
    conversoes = {
        "CODE": "code",
        "PONTO": "ponto",
        "ORIGIN": "origin",
        "AREA": "area",
        "SAMPLE": "sample",
        "COLLECTION POINT": "collection_point",
        "SAMPLING": "sampling",
        "METHOD": "method",
        "FREQUÊNCIA": "frequencia",
        "FREQUENCIA": "frequencia",
        "ANALISTA": "analista",
        "DATA": "data",
        "RESULTADO": "resultado",
        "FORM": "form",
        "MARGIN": "margin",
        "PIGMENT": "pigment",
        "GRAM STAIN": "gram_stain",
        "CATALASE": "catalase",
        "KOH": "koh",
        "OXIDASE": "oxidase",
        "OUTSOURCED METHOD": "outsourced_method",
        "IDENTIFICATION": "identification",
        "REPORT": "report",
        "COMPANY": "company",
        "END DATE": "end_date",
    }

    nome = str(nome).strip()

    return conversoes.get(
        nome.upper(),
        nome.lower().replace(" ", "_"),
    )


def importar_excel(arquivo):
    registro = pd.read_excel(
        arquivo,
        sheet_name="Registro",
    )

    arquivo.seek(0)

    identificacao = pd.read_excel(
        arquivo,
        sheet_name="Identification",
    )

    registro.columns = [
        normalizar_coluna(coluna)
        for coluna in registro.columns
    ]

    identificacao.columns = [
        normalizar_coluna(coluna)
        for coluna in identificacao.columns
    ]

    for coluna in COLUNAS_AMOSTRA:
        if coluna not in registro.columns:
            registro[coluna] = ""

    for coluna in COLUNAS_IDENTIFICACAO:
        if coluna not in identificacao.columns:
            identificacao[coluna] = ""

    registro = registro[
        COLUNAS_AMOSTRA
    ].fillna("")

    identificacao = identificacao[
        COLUNAS_IDENTIFICACAO
    ].fillna("")

    registro = registro[
        registro["code"].astype(str).str.strip() != ""
    ]

    identificacao = identificacao[
        identificacao["code"].astype(str).str.strip() != ""
    ]

    registro["data"] = (
        pd.to_datetime(
            registro["data"],
            errors="coerce",
        )
        .dt.strftime("%Y-%m-%d")
        .fillna("")
    )

    identificacao["end_date"] = (
        pd.to_datetime(
            identificacao["end_date"],
            errors="coerce",
        )
        .dt.strftime("%Y-%m-%d")
        .fillna("")
    )

    substituir_dados(
        registro.to_dict("records"),
        identificacao.to_dict("records"),
    )


def gerar_excel():

    amostras = obter_amostras()

    identificacoes = obter_identificacoes()

    armazenamento = obter_armazenamento()

    if not armazenamento.empty:
        armazenamento = armazenamento.rename(columns={
            "code": "CODE",
            "box": "BOX",
            "backup_box": "BACKUP BOX",
            "freezer": "FREEZER",
            "storage_date": "STORAGE DATE",
            "analyst": "ANALYST",
            "backup_used": "BACKUP USED"
        })

    arquivo = BytesIO()

    with pd.ExcelWriter(
        arquivo,
        engine="openpyxl"
    ) as writer:

        amostras.to_excel(
            writer,
            sheet_name="Registro",
            index=False
        )

        identificacoes.to_excel(
            writer,
            sheet_name="Identification",
            index=False
        )

        armazenamento.to_excel(
            writer,
            sheet_name="Storage",
            index=False
        )

    return arquivo.getvalue()

def normalizar_coluna_sistema(nome):
    conversoes = {
        "CODE": "code", "PONTO": "ponto", "ORIGIN": "origin", "AREA": "area", "SAMPLE": "sample",
        "COLLECTION POINT": "collection_point", "SAMPLING": "sampling", "METHOD": "method",
        "FREQUÊNCIA": "frequencia", "FREQUENCIA": "frequencia", "ANALISTA": "analista", "DATA": "data",
        "RESULTADO": "resultado", "FORM": "form", "MARGIN": "margin", "PIGMENT": "pigment",
        "GRAM STAIN": "gram_stain", "CATALASE": "catalase", "KOH": "koh", "OXIDASE": "oxidase",
        "OUTSOURCED METHOD": "outsourced_method", "IDENTIFICATION": "identification", "REPORT": "report",
        "COMPANY": "company", "END DATE": "end_date",
        "TSB": "tsb", "GLICERINA": "glicerina", "TSA": "tsa", "CRIOTUBO": "criotubo",
        "PLACA DE PETRI": "placa_de_petri", "FLUXO LAMINAR": "fluxo_laminar", "ULTRAFREEZER": "ultrafreezer"
    }
    return conversoes.get(str(nome).strip().upper(), str(nome).strip().lower().replace(" ", "_"))


def importar_excel(arquivo):
    with conectar() as conexao:
        try:
            df_brutos = pd.read_excel(arquivo, sheet_name="Dados Brutos")
            df_brutos.columns = [normalizar_coluna_sistema(col) for col in df_brutos.columns]
            colunas_obrigatorias = ["tsb", "glicerina", "tsa", "criotubo", "placa_de_petri", "fluxo_laminar", "ultrafreezer"]
            for col in colunas_obrigatorias:
                if col not in df_brutos.columns: df_brutos[col] = ""
            df_brutos = df_brutos.fillna("")
            
            conexao.execute("DELETE FROM dados_brutos")
            for _, linha in df_brutos.iterrows():
                conexao.execute("INSERT INTO dados_brutos (tsb, glicerina, tsa, criotubo, placa_de_petri, fluxo_laminar, ultrafreezer) VALUES (?, ?, ?, ?, ?, ?, ?)", (str(linha.get("tsb", "")), str(linha.get("glicerina", "")), str(linha.get("tsa", "")), str(linha.get("criotubo", "")), str(linha.get("placa_de_petri", "")), str(linha.get("fluxo_laminar", "")), str(linha.get("ultrafreezer", ""))))
        except Exception:
            pass

        try:
            arquivo.seek(0)
            registro = pd.read_excel(arquivo, sheet_name="Registro")
            arquivo.seek(0)
            identificacao = pd.read_excel(arquivo, sheet_name="Identification")

            registro.columns = [normalizar_coluna_sistema(c) for c in registro.columns]
            identificacao.columns = [normalizar_coluna_sistema(c) for c in identificacao.columns]

            registro = registro.fillna("").loc[lambda d: d["code"].astype(str).str.strip().ne("")]
            identificacao = identificacao.fillna("").loc[lambda d: d["code"].astype(str).str.strip().ne("")]

            conexao.execute("DELETE FROM identificacoes")
            conexao.execute("DELETE FROM amostras")
            
            for _, r in registro.iterrows():
                conexao.execute(f"INSERT INTO amostras ({','.join(COLUNAS_AMOSTRA)}) VALUES ({','.join('?' for _ in COLUNAS_AMOSTRA)})", [r.get(c, "") for c in COLUNAS_AMOSTRA])
            for _, i in identificacao.iterrows():
                conexao.execute(f"INSERT INTO identificacoes ({','.join(COLUNAS_IDENTIFICACAO)}) VALUES ({','.join('?' for _ in COLUNAS_IDENTIFICACAO)})", [i[c] for c in COLUNAS_IDENTIFICACAO])
        except Exception as e:
            st.error(f"Erro nas planilhas padrão: {e}")


def pagina_dados():
    st.title("Importação e Exportação")
    st.download_button(label="Baixar dados em Excel", data=gerar_excel(), file_name="monitoramento_microbiologico.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.divider()
    st.subheader("Importar arquivo Excel")
    st.warning("A importação substituirá os registros atuais. Faça backup antes.")

    arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
    confirmar = st.checkbox("Confirmo a substituição total")

    if arquivo is not None and confirmar and st.button("Importar dados", type="primary"):
        try:
            importar_excel(arquivo)
            st.success("Dados importados com sucesso.")
            st.rerun()
        except Exception as erro: st.error(f"Erro na importação: {erro}")



def pagina_dados_brutos():
    st.title("🗃️ Registro de Dados Brutos (Raw Data)")
    st.caption("Gerenciamento e monitoramento automático de validades de insumos e meios de cultura.")

    # Garante a existência da tabela com suporte a formato de data nativo
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS dados_brutos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tsb TEXT, tsb_val TEXT,
                glicerina TEXT, glicerina_val TEXT,
                tsa TEXT, tsa_val TEXT,
                criotubo TEXT, placa_de_petri TEXT, fluxo_laminar TEXT, ultrafreezer TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

    try:
        linhas = consultar("SELECT id, tsb, tsb_val, glicerina, tsa, tsa_val, criotubo, placa_de_petri, fluxo_laminar, ultrafreezer FROM dados_brutos ORDER BY id DESC")
    except Exception:
        linhas = []
        
    df_brutos = pd.DataFrame(linhas)
    lista_ids = df_brutos["id"].tolist() if not df_brutos.empty else []

    modo = st.radio("Ação", ["📋 Visualizar Planilha & Alertas", "➕ Inserir Linha Manual", "✏️ Editar Linha", "❌ Excluir Linha"], horizontal=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # MODO 1: VISUALIZAR PLANILHA COM ALERTAS COLORIDOS
    # ============================================================
    if modo == "📋 Visualizar Planilha & Alertas":
        if df_brutos.empty:
            st.info("Nenhum dado bruto encontrado. Cadastre manualmente ou via importação.")
        else:
            st.markdown("### 🚦 Status e Alertas de Validade")
            
            def mapear_status_validade(data_texto):
                if not data_texto or data_texto == "—":
                    return "⚪ Sem Data"
                try:
                    data_val = pd.to_datetime(data_texto).date()
                    hoje = pd.Timestamp.now().date()
                    dias_restantes = (data_val - hoje).days
                    
                    if dias_restantes < 0:
                        return "🔴 VENCIDO"
                    elif dias_restantes <= 30:
                        return f"🟡 Vence em {dias_restantes} dias"
                    else:
                        return "🟢 Regular"
                except Exception:
                    return "⚪ Erro na data"

            df_visualizacao = df_brutos.copy()
            df_visualizacao["STATUS TSB"] = df_visualizacao["tsb_val"].apply(mapear_status_validade)
            df_visualizacao["STATUS TSA"] = df_visualizacao["tsa_val"].apply(mapear_status_validade)
            
            st.dataframe(
                df_visualizacao[[
                    "id", "tsb", "tsb_val", "STATUS TSB", 
                    "tsa", "tsa_val", "STATUS TSA", 
                    "glicerina", "criotubo", "placa_de_petri", "fluxo_laminar", "ultrafreezer"
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID", "tsb": "LOTE TSB", "tsb_val": "VALIDADE TSB",
                    "tsa": "LOTE TSA", "tsa_val": "VALIDADE TSA",
                    "glicerina": "GLICERINA", "criotubo": "CRIOTUBO",
                    "placa_de_petri": "PLACA PETRI", "fluxo_laminar": "FLUXO LAMINAR", "ultrafreezer": "ULTRAFREEZER"
                }
            )
            
    # ============================================================
    # MODO 2: EXCLUIR REGISTRO
    # ============================================================
    elif modo == "❌ Excluir Linha":
        if not lista_ids: return
        id_sel = st.selectbox("Selecione o ID para remover:", lista_ids)
        if st.button("❌ Deletar Permanentemente", type="primary", use_container_width=True):
            with conectar() as conexao: 
                conexao.execute("DELETE FROM dados_brutos WHERE id = ?", (id_sel,))
            st.success("Deletado com sucesso!")
            st.rerun()

    # ============================================================
    # MODO 3: INSERIR OU EDITAR COM SELETOR DE CALENDÁRIO
    # ============================================================
    else:
        reg = df_brutos[df_brutos["id"] == st.selectbox("Selecione o ID para editar:", lista_ids)].iloc[0].to_dict() if modo == "✏️ Editar Linha" and lista_ids else {}
        
        with st.form("form_brutos_validades"):
            st.markdown("##### 🧫 Meios de Cultura (Lote e Validade)")
            col_tsb1, col_tsb2 = st.columns([2, 1])
            tsb = col_tsb1.text_input("Lote TSB", value=reg.get("tsb", ""))
            dt_tsb = pd.to_datetime(reg.get("tsb_val", ""), errors="coerce")
            tsb_val = col_tsb2.date_input("Validade TSB", value=None if pd.isna(dt_tsb) else dt_tsb.date(), format="DD/MM/YYYY")

            col_tsa1, col_tsa2 = st.columns([2, 1])
            tsa = col_tsa1.text_input("Lote TSA", value=reg.get("tsa", ""))
            dt_tsa = pd.to_datetime(reg.get("tsa_val", ""), errors="coerce")
            tsa_val = col_tsa2.date_input("Validade TSA", value=None if pd.isna(dt_tsa) else dt_tsa.date(), format="DD/MM/YYYY")

            st.markdown("---")
            st.markdown("##### 📦 Outros Insumos e Equipamentos")
            c1, c2, c3, c4 = st.columns(4)
            glicerina = c1.text_input("GLICERINA", value=reg.get("glicerina", ""))
            criotubo = c2.text_input("CRIOTUBO", value=reg.get("criotubo", ""))
            placa = c3.text_input("PLACA DE PETRI", value=reg.get("placa_de_petri", ""))
            fluxo = c4.text_input("FLUXO LAMINAR", value=reg.get("fluxo_laminar", ""))
            
            ultrafreezer = st.text_input("ULTRAFREEZER", value=reg.get("ultrafreezer", ""))
            
            if st.form_submit_button("Salvar Dados e Monitorar Validades", type="primary"):
                t_val = tsb_val.isoformat() if tsb_val else ""
                a_val = tsa_val.isoformat() if tsa_val else ""
                
                with conectar() as conexao:
                    # 🩹 SEGURANÇA INTERNA AUTOMÁTICA CONTRA ERROS DE SQLITE
                    try: conexao.execute("ALTER TABLE dados_brutos ADD COLUMN tsb_val TEXT")
                    except sqlite3.OperationalError: pass
                    try: conexao.execute("ALTER TABLE dados_brutos ADD COLUMN tsa_val TEXT")
                    except sqlite3.OperationalError: pass
                    
                    if modo == "✏️ Editar Linha":
                        conexao.execute("""
                            UPDATE dados_brutos 
                            SET tsb=?, tsb_val=?, glicerina=?, tsa=?, tsa_val=?, criotubo=?, placa_de_petri=?, fluxo_laminar=?, ultrafreezer=? 
                            WHERE id=?
                        """, (tsb, t_val, glicerina, tsa, a_val, criotubo, placa, fluxo, ultrafreezer, id_sel))
                    else:
                        conexao.execute("""
                            INSERT INTO dados_brutos (tsb, tsb_val, glicerina, tsa, tsa_val, criotubo, placa_de_petri, fluxo_laminar, ultrafreezer) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (tsb, t_val, glicerina, tsa, a_val, criotubo, placa, fluxo, ultrafreezer))
                st.success("Dados salvos e monitoramento ativado!")
                st.rerun()






# ============================================================
# INICIALIZAÇÃO DO SISTEMA
# ============================================================

if not mostrar_login():
    st.stop()

criar_banco()


# ============================================================
# MENU LATERAL (CORRIGIDO PARA SINTAXE NATIVA)
# ============================================================

st.sidebar.markdown(
    """
    <div class="logo-menu">
        🧫 Natalia
        <span>Monitoramento Microbiológico</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.caption(
    f"Conectado como "
    f"{st.session_state.get('usuario', 'Natalia')}"
)

# Definição das opções em português para bater com a lógica do seu app
pagina = st.sidebar.radio(
    "Navegação",
    [
        "Dashboard",
        "Registro",
        "Identificação",
        "Armazenamento",
        "Dados",
        "Dados Brutos",
    ],
)

st.sidebar.divider()

if st.sidebar.button(
    "Sair",
    use_container_width=True,
):
    st.session_state.autenticado = False
    st.session_state.pop("usuario", None)
    st.rerun()

st.sidebar.caption(
    "Banco SQLite • dados persistentes"
)


# ============================================================
# CABEÇALHO
# ============================================================

# ==========================================
# CABEÇALHO DO BIOBANK
# ==========================================

st.markdown(
    """
    <style>
    /* Reduz as margens e amplia a área principal */
    .block-container {
        max-width: 100% !important;
        padding-top: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
    }

    /* Evita espaços laterais desnecessários */
    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
    }

    /* Banner ocupa toda a largura disponível */
    .biobank-banner {
        width: 100%;
        min-height: 150px;
        box-sizing: border-box;
        background-image:
            linear-gradient(
                90deg,
                rgba(75, 20, 60, 0.12),
                rgba(100, 20, 85, 0.18)
            ),
            url("https://raw.githubusercontent.com/projetonah-jpg/biobanco-empresa/main/banner_novo.png.jpg");
        background-size: cover;
        background-position: center;
        border-radius: 0 0 18px 18px;
        margin: 0 0 24px 0;
        padding: 28px 32px;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        justify-content: center;
        text-align: right;
        color: white;
        box-shadow: 0 8px 24px rgba(74, 43, 117, 0.12);
    }

    .biobank-banner h1 {
        margin: 0;
        font-size: clamp(24px, 2.5vw, 36px);
        font-weight: 750;
        color: white;
        text-shadow: 1px 2px 5px rgba(0, 0, 0, 0.3);
    }

    .biobank-banner p {
        margin: 8px 0 0 0;
        font-size: 15px;
        color: white;
    }

    /* Cartões e gráficos aproveitam a largura */
    [data-testid="stMetric"],
    [data-testid="stPlotlyChart"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        width: 100%;
    }

    /* Ajustes para telas menores */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        .biobank-banner {
            min-height: 125px;
            padding: 22px 18px;
            background-position: center;
        }

        .biobank-banner h1 {
            font-size: 24px;
        }

        .biobank-banner p {
            font-size: 13px;
        }
    }
    </style>

    <div class="biobank-banner">
        <h1>BIOBANK - NATALIA</h1>
        <p>Gestão integrada de cepas, identificação e armazenamento.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# ABERTURA DAS PÁGINAS (ORQUESTRADOR DAS ABAS)
# ============================================================

if pagina == "Dashboard":
    pagina_dashboard()

elif pagina == "Registro":
    pagina_registro()

elif pagina == "Identificação":
    pagina_identificacao()

elif pagina == "Armazenamento":
    pagina_armazenamento()

elif pagina == "Dados Brutos":
    pagina_dados_brutos()

elif pagina == "Dados":
    pagina_dados()
