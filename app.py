import io
from io import BytesIO
from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
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


# ============================================================
# ESTILO E IDENTIDADE VISUAL
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --purple-dark: #612147;
        --purple-light: #833161;
        --purple-bg: #fdfafc;
        --white: #ffffff;
    }

    /* Oculta barra superior padrão */
    .stAppHeader, [data-testid="stHeader"], header, [data-testid="stHeaderActionElements"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Fundo roxo externo */
    .stApp {
        background-color: #612147 !important;
    }

    /* Folha interna branca */
    [data-testid="stMainView"], [data-testid="stCanvas"], .main, .stVerticalBlockRoot {
        background-color: #ffffff !important;
    }

    .block-container {
        background-color: #ffffff !important;
        padding: 0px 45px 35px 45px !important;
        margin-top: 0rem !important;
        border-radius: 0px 0px 18px 18px !important;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25) !important;
        max-width: 96% !important;
    }

    [data-testid="stMain"] {
        padding-top: 0rem !important;
        background-color: #612147 !important;
    }

    /* Textos escuros dentro da área branca */
    [data-testid="stMainView"] [data-testid="stWidgetLabel"] p, 
    [data-testid="stMainView"] label p, 
    [data-testid="stMainView"] .stMarkdown p, 
    [data-testid="stMainView"] h1, 
    [data-testid="stMainView"] h2, 
    [data-testid="stMainView"] h3, 
    [data-testid="stMainView"] .stSubheader {
        color: #31333F !important;
    }
    
    /* Texto branco na barra lateral */
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
        background-color: #612147 !important;
        background-image: none !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Cards de Indicadores */
    [data-testid="stMetric"] {
        background-color: white !important;
        border: 1px solid #f5edf2 !important;
        border-left: 5px solid #833161 !important;
        padding: 16px !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 18px rgba(97, 33, 71, 0.06) !important;
    }

    /* Botões roxos com letra branca */
    .stButton > button, .stFormSubmitButton > button, 
    .stButton > button *, .stFormSubmitButton > button * {
        border-radius: 10px !important;
        border: 0 !important;
        background-color: #833161 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background-color: #612147 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(131, 49, 97, 0.25) !important;
    }

    [data-testid="stForm"] {
        background-color: white !important;
        padding: 28px 34px 20px 34px !important;
        border-radius: 22px !important;
        border: 1px solid #f5edf2 !important;
    }

    /* Corrige campos de entrada no modo escuro */
    [data-testid="stTextInput"] input, 
    [data-testid="stSelectbox"] div, 
    [data-testid="stNumberInput"] input,
    .stSelectbox div,
    .stDateInput button,
    input {
        background-color: #ffffff !important;
        color: #31333F !important;
        -webkit-text-fill-color: #31333F !important;
    }
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
        "Others",
    ],
    "AREA": [
        "Laboratory",
        "Dissolution of Salts",
        "1940 - Dissolution of Sugar",
        "1920 - Dissolution of Sugar",
        "1910 - Dissolution of Sugar",
        "1710 - Dissolution of Sugar",
        "1720 - Dissolution of Sugar",
        "Line 2 - Fermentation",
        "Line 3 - Fermentation",
        "Line 4 - Fermentation",
        "Line 5 - Fermentation",
        "SBTA 1 - Dissolution of Sugar",
        "SBTA 2 - Dissolution of Sugar",
        "Autoclave 3710 - Fermentation",
        "Autoclave 3720 - Fermentation",
        "Autoclave 4710 - Fermentation",
        "Autoclave 4720 - Fermentation",
    ],
    "SAMPLE": [
        "Inoculation Room Anteroom",
        "Inoculation Room",
        "Flow Room",
        "Dissolution of Salts - Tank Area",
        "Dissolution of Salts - Weighing Area",
        "Team Member",
        "Sterile",
        "Non sterile",
        "Sample",
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
        "Antifoam L81 (TERGITOL L-81 BR surfactant)",
        "Maltose",
    ],
    "SAMPLING": [
        "Swab",
        "Passive",
        "MAS-100",
        "Plating",
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
# BANCO DE DADOS
# ============================================================

COLUNAS_AMOSTRA = [
    "code",
    "sample_id",
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
            backup_used TEXT,
            posicao INTEGER,
            posicao_backup INTEGER
        );
        """
        conexao.execute(q1)
        conexao.execute(q2)
        conexao.execute(q3)
        conexao.execute(q4)

        colunas_amostras = {
            "sample_id": "TEXT",
            "ponto": "TEXT",
            "origin": "TEXT",
            "area": "TEXT",
            "sample": "TEXT",
            "collection_point": "TEXT",
            "sampling": "TEXT",
            "method": "TEXT",
            "frequencia": "TEXT",
            "analista": "TEXT",
            "data": "TEXT",
            "resultado_final": "TEXT",
        }
        for col, tipo in colunas_amostras.items():
            try:
                conexao.execute(f"ALTER TABLE amostras ADD COLUMN {col} {tipo}")
            except sqlite3.OperationalError:
                pass

        colunas_identificacoes = {
            "form": "TEXT",
            "margin": "TEXT",
            "pigment": "TEXT",
            "gram_stain": "TEXT",
            "catalase": "TEXT",
            "koh": "TEXT",
            "oxidase": "TEXT",
            "outsourced_method": "TEXT",
            "identification": "TEXT",
            "report": "TEXT",
            "company": "TEXT",
            "start_date": "TEXT",
            "end_date": "TEXT",
            "report_data": "BLOB",
        }
        for col, tipo in colunas_identificacoes.items():
            try:
                conexao.execute(
                    f"ALTER TABLE identificacoes ADD COLUMN {col} {tipo}"
                )
            except sqlite3.OperationalError:
                pass

        colunas_brutos = {
            "tsb": "TEXT",
            "tsb_val": "TEXT",
            "glicerina": "TEXT",
            "glicerina_val": "TEXT",
            "tsa": "TEXT",
            "tsa_val": "TEXT",
            "criotubo": "TEXT",
            "placa_de_petri": "TEXT",
            "fluxo_laminar": "TEXT",
            "ultrafreezer": "TEXT",
        }
        for col, tipo in colunas_brutos.items():
            try:
                conexao.execute(
                    f"ALTER TABLE dados_brutos ADD COLUMN {col} {tipo}"
                )
            except sqlite3.OperationalError:
                pass


def consultar(sql, parametros=()):
    with conectar() as conexao:
        linhas = conexao.execute(sql, parametros).fetchall()
        return [dict(linha) for linha in linhas]


def salvar_amostra(registro):
    marcadores = ",".join("?" for _ in COLUNAS_AMOSTRA)
    atualizacoes = ",".join(
        f"{coluna}=excluded.{coluna}"
        for coluna in COLUNAS_AMOSTRA
        if coluna != "code"
    )
    sql = f"""
        INSERT INTO amostras ({",".join(COLUNAS_AMOSTRA)})
        VALUES ({marcadores})
        ON CONFLICT(code) DO UPDATE SET
            {atualizacoes},
            atualizado_em=CURRENT_TIMESTAMP
    """
    valores = [registro.get(coluna, "") for coluna in COLUNAS_AMOSTRA]
    with conectar() as conexao:
        conexao.execute(sql, valores)


def salvar_identificacao(registro):
    marcadores = ",".join("?" for _ in COLUNAS_IDENTIFICACAO)
    atualizacoes = ",".join(
        f"{coluna}=excluded.{coluna}"
        for coluna in COLUNAS_IDENTIFICACAO
        if coluna != "code"
    )
    sql = f"""
        INSERT INTO identificacoes ({",".join(COLUNAS_IDENTIFICACAO)})
        VALUES ({marcadores})
        ON CONFLICT(code) DO UPDATE SET
            {atualizacoes},
            atualizado_em=CURRENT_TIMESTAMP
    """
    valores = [registro.get(coluna, "") for coluna in COLUNAS_IDENTIFICACAO]
    with conectar() as conexao:
        conexao.execute(sql, valores)


def excluir_amostra(code):
    with conectar() as conexao:
        conexao.execute("DELETE FROM armazenamento_cepas WHERE code = ?", (code,))
        conexao.execute("DELETE FROM identificacoes WHERE code = ?", (code,))
        conexao.execute("DELETE FROM amostras WHERE code = ?", (code,))
        conexao.commit()

# ============================================================
# FUNÇÕES AUXILIARES DOS DADOS
# ============================================================


def obter_amostras():
    dados = consultar(
        """
        SELECT
            code, sample_id, ponto, origin, area, sample,
            collection_point, sampling, method, frequencia,
            analista, data, resultado_final
        FROM amostras
        ORDER BY data DESC, code
        """
    )
    return pd.DataFrame(dados)


def obter_identificacoes():
    sql_consulta = """
        SELECT
            a.code, a.area, a.collection_point, a.data,
            i.form, i.margin, i.pigment, i.gram_stain,
            i.catalase, i.koh, i.oxidase, i.outsourced_method,
            i.identification, i.report, i.company, i.start_date, i.end_date
        FROM amostras a
        LEFT JOIN identificacoes i ON i.code = a.code
        ORDER BY a.code
    """
    try:
        dados = consultar(sql_consulta)
    except sqlite3.OperationalError:
        with conectar() as conexao:
            try:
                conexao.execute(
                    "ALTER TABLE identificacoes ADD COLUMN start_date TEXT"
                )
                conexao.commit()
            except sqlite3.OperationalError:
                pass
        dados = consultar(sql_consulta)

    return pd.DataFrame(dados)


def campo_selecao(titulo, nome_lista, valor_atual=""):
    opcoes = [""] + LISTAS.get(nome_lista, [])
    if valor_atual and valor_atual not in opcoes:
        opcoes.append(valor_atual)
    indice = opcoes.index(valor_atual) if valor_atual in opcoes else 0
    return st.selectbox(titulo, opcoes, index=indice)


# ============================================================
# PÁGINA 1: DASHBOARD
# ============================================================


def pagina_dashboard():
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

    st.markdown(
        "<h1 class='titulo-relatorio'>SISTEMA DE MONITORAMENTO BIOLÓGICO</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='subtitulo-relatorio'>ANÁLISE E CONTROLE DE CONTAMINANTES"
        " AMBIENTAIS</p>",
        unsafe_allow_html=True,
    )

    df_completo = consultar(
        """
        SELECT
            a.code, a.origin, a.area, a.sample, a.collection_point,
            a.frequencia, a.resultado_final, a.data,
            i.identification, i.gram_stain
        FROM amostras a
        LEFT JOIN identificacoes i ON i.code = a.code
        """
    )

    df = pd.DataFrame(df_completo)

    if df.empty:
        st.info("Nenhuma amostra cadastrada no banco de dados.")
        return

    aba_tendencia, aba_tanques, aba_auditoria = st.tabs([
        "📊 Relatório de Tendência",
        "🏭 Controle por Áreas e Tanques",
        "🛡️ Indicadores Avançados e Auditoria",
    ])

    # ABA 1: RELATÓRIO DE TENDÊNCIA
    with aba_tendencia:
        df_identificados = df[
            df["identification"].fillna("").str.strip() != ""
        ].copy()
        if not df_identificados.empty:
            total_identificados = len(df_identificados)
            resumo = (
                df_identificados["identification"].value_counts().reset_index()
            )
            resumo.columns = ["Microrganismo", "Contagem"]
            resumo["Frequência"] = (
                resumo["Contagem"] / total_identificados * 100
            ).round(1).astype(str) + "%"

            grams, esporulados, ecologias, patogenicidades = [], [], [], []
            for micro in resumo["Microrganismo"]:
                if (
                    "Staphylococcus" in micro
                    or "epidermidis" in micro.lower()
                    or "hominis" in micro.lower()
                ):
                    grams.append("C+")
                    esporulados.append("Não")
                    ecologias.append("Microbiota normal da pele e mucosas")
                    patogenicidades.append("Não-patogênico")
                elif "Bacillus" in micro:
                    grams.append("B+")
                    esporulados.append("Sim")
                    ecologias.append("Comumente encontrado em solo")
                    patogenicidades.append("Patogenicidade variada")
                elif "Micrococcus" in micro or "luteus" in micro.lower():
                    grams.append("C+")
                    esporulados.append("Não")
                    ecologias.append("Comumente encontrada em ar, solo e pele")
                    patogenicidades.append("Não-patogênico")
                else:
                    grams.append("N/A")
                    esporulados.append("Não")
                    ecologias.append("Ambiente geral / Dispersão aérea")
                    patogenicidades.append("Variada")

            resumo["Gram"] = grams
            resumo["Esporulado"] = esporulados
            resumo["Ecologia"] = ecologias
            resumo["Patogenicidade"] = patogenicidades

            st.dataframe(
                resumo[[
                    "Microrganismo",
                    "Frequência",
                    "Gram",
                    "Esporulado",
                    "Ecologia",
                    "Patogenicidade",
                ]],
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            if not df_identificados.empty:
                fig_p = px.pie(
                    df_identificados["identification"]
                    .value_counts()
                    .reset_index(),
                    names="identification",
                    values="count",
                    hole=0.4,
                    title="Distribuição dos micro-organismos",
                    color_discrete_sequence=px.colors.qualitative.Safe,
                )
                fig_p.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#333333"),
                    title_font=dict(size=14, color="#16857a"),
                )
                st.plotly_chart(fig_p, use_container_width=True)
        with g2:
            df_pontos = df[
                df["collection_point"].fillna("").str.strip() != ""
            ].copy()
            if not df_pontos.empty:
                contagem_pontos = (
                    df_pontos["collection_point"].value_counts().reset_index()
                )
                contagem_pontos.columns = ["collection_point", "Quantidade"]
                contagem_pontos = contagem_pontos.sort_values(
                    by="Quantidade", ascending=True
                )

                fig_b = px.bar(
                    contagem_pontos,
                    y="collection_point",
                    x="Quantidade",
                    orientation="h",
                    text_auto=True,
                    title="Frequência dos locais isolados",
                    color_discrete_sequence=["#16857a"],
                )
                fig_b.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#333333"),
                    title_font=dict(size=14, color="#16857a"),
                    xaxis=dict(
                        title="Ocorrências", gridcolor="rgba(0,0,0,0.05)"
                    ),
                    yaxis=dict(title=""),
                )
                st.plotly_chart(fig_b, use_container_width=True)

    # ABA 2: CONTROLE POR ÁREAS E TANQUES
    with aba_tanques:
        st.subheader("🔍 Rastreabilidade e Auditoria por Setor")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_origem = st.selectbox(
                "Filtrar por Origem do Monitoramento:",
                ["Todos"] + list(df["origin"].dropna().unique()),
            )
        with col_f2:
            filtro_conformidade = st.selectbox(
                "Filtrar por Status de Conformidade:",
                ["Todos", "Conforme", "Não Conforme"],
            )

        df_filtrado = df.copy()
        if filtro_origem != "Todos":
            df_filtrado = df_filtrado[df_filtrado["origin"] == filtro_origem]
        if filtro_conformidade != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["resultado_final"] == filtro_conformidade
            ]

        c1, c2, c3 = st.columns(3)
        c1.metric("Amostras Avaliadas no Filtro", len(df_filtrado))
        c2.metric(
            "Pontos Críticos Identificados",
            df_filtrado["collection_point"].nunique(),
        )
        c3.metric(
            "Ocorrências Não Conformes",
            int((df_filtrado["resultado_final"] == "Não Conforme").sum()),
        )

        st.write("---")
        g_areas, g_conformidade = st.columns(2)
        with g_areas:
            fig_areas = px.bar(
                df_filtrado["area"].value_counts().reset_index(),
                y="area",
                x="count",
                orientation="h",
                text_auto=True,
                title="<b>Volume de Ocorrências por Área / Tanque</b>",
                color_discrete_sequence=["#2a6f68"],
            )
            fig_areas.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_areas, use_container_width=True)
        with g_conformidade:
            df_status = (
                df_filtrado.groupby(["collection_point", "resultado_final"])
                .size()
                .reset_index(name="Quantidade")
            )
            fig_status = px.bar(
                df_status,
                x="collection_point",
                y="Quantidade",
                color="resultado_final",
                title="<b>Conformidade por Ponto de Coleta Crítico</b>",
                barmode="stack",
                color_discrete_map={
                    "Conforme": "#6bb1a9",
                    "Não Conforme": "#d9534f",
                    "": "#999999",
                },
            )
            fig_status.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="",
                yaxis_title="Amostras",
            )
            st.plotly_chart(fig_status, use_container_width=True)

        st.subheader("Lista Filtrada de Isolados")
        st.dataframe(
            df_filtrado[[
                "code",
                "origin",
                "area",
                "collection_point",
                "identification",
                "resultado_final",
                "data",
            ]],
            use_container_width=True,
            hide_index=True,
        )

    # ABA 3: INDICADORES AVANÇADOS E AUDITORIA
    with aba_auditoria:
        st.subheader("🛡️ Gestão de Riscos e Validação de Processos")

        df_auditoria = df.copy()
        df_auditoria["data"] = pd.to_datetime(
            df_auditoria["data"], errors="coerce"
        )

        col_ano, col_mes = st.columns(2)
        with col_ano:
            anos_disponiveis = ["Todos"] + sorted(
                list(df_auditoria["data"].dt.year.dropna().unique().astype(int)),
                reverse=True,
            )
            ano_selecionado = st.selectbox(
                "Filtrar Auditoria por Ano:",
                anos_disponiveis,
                key="auditoria_ano",
            )

        with col_mes:
            meses_nomes = {
                1: "Janeiro",
                2: "Fevereiro",
                3: "Março",
                4: "Abril",
                5: "Maio",
                6: "Junho",
                7: "Julho",
                8: "Agosto",
                9: "Setembro",
                10: "Outubro",
                11: "Novembro",
                12: "Dezembro",
            }
            meses_disponiveis = ["Todos"]
            if ano_selecionado != "Todos":
                meses_numeros = (
                    df_auditoria[
                        df_auditoria["data"].dt.year == int(ano_selecionado)
                    ]["data"]
                    .dt.month.dropna()
                    .unique()
                )
                meses_disponiveis += [
                    meses_nomes[m] for m in sorted(meses_numeros)
                ]
            else:
                meses_disponiveis += [
                    meses_nomes[m]
                    for m in sorted(
                        df_auditoria["data"].dt.month.dropna().unique()
                    )
                ]

            mes_selecionado = st.selectbox(
                "Filtrar Auditoria por Mês:",
                meses_disponiveis,
                key="auditoria_mes",
            )

        if ano_selecionado != "Todos":
            df_auditoria = df_auditoria[
                df_auditoria["data"].dt.year == int(ano_selecionado)
            ]
        if mes_selecionado != "Todos":
            num_mes = [
                k for k, v in meses_nomes.items() if v == mes_selecionado
            ][0]
            df_auditoria = df_auditoria[
                df_auditoria["data"].dt.month == num_mes
            ]

        st.write("---")

        nao_conformes_totais = (
            df_auditoria["resultado_final"] == "Não Conforme"
        ).sum()

        card_1, card_2 = st.columns(2)
        with card_1:
            if nao_conformes_totais <= 2:
                st.markdown(
                    '<div class="card-status" style="background-color:'
                    " #28a745;'>🟢 STATUS DO BIOBANCO: NORMAL<br><span"
                    ' style="font-size:12px; font-weight:normal;">Dentro do'
                    " Limite de Alerta aceitável no período.</span></div>",
                    unsafe_allow_html=True,
                )
            elif nao_conformes_totais <= 4:
                st.markdown(
                    '<div class="card-status" style="background-color: #ffc107;'
                    ' color: #333;">🟡 STATUS DO BIOBANCO: ALERTA<br><span'
                    ' style="font-size:12px; font-weight:normal;">Aumento de'
                    " desvios no período. Revisar processos.</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="card-status" style="background-color:'
                    " #dc3545;'>🔴 STATUS DO BIOBANCO: CRÍTICO<br><span"
                    ' style="font-size:12px; font-weight:normal;">Limite de'
                    " Ação violado no período. Exige sanitização!</span></div>",
                    unsafe_allow_html=True,
                )
        with card_2:
            total_avaliadas = len(df_auditoria)
            conformes = (df_auditoria["resultado_final"] == "Conforme").sum()
            taxa_eficiencia = (
                round((conformes / total_avaliadas) * 100, 1)
                if total_avaliadas > 0
                else 100.0
            )
            texto_html = (
                '<div class="card-status" style="background-color: #16857a;">🧼'
                f" EFICIÊNCIA DE SANITIZAÇÃO: {taxa_eficiencia}%<br><span"
                ' style="font-size:12px; font-weight:normal;">Pontos livres de'
                " contaminação no período filtrado.</span></div>"
            )
            st.markdown(texto_html, unsafe_allow_html=True)

        st.write("---")

        st.markdown(
            "##### 🗺️ Mapa de Calor: Concentração de Microrganismos por Ponto"
            " Crítico"
        )
        df_heatmap_raw = df_auditoria[
            (df_auditoria["collection_point"].fillna("").str.strip() != "")
            & (df_auditoria["identification"].fillna("").str.strip() != "")
        ]

        if not df_heatmap_raw.empty:
            matriz_contagem = pd.crosstab(
                df_heatmap_raw["identification"],
                df_heatmap_raw["collection_point"],
            )
            fig_heatmap = px.imshow(
                matriz_contagem,
                text_auto=True,
                labels=dict(
                    x="Ponto de Coleta / Local Isolado",
                    y="Microrganismo Identificado",
                    color="Ocorrências",
                ),
                color_continuous_scale="Reds",
            )
            fig_heatmap.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#333333"),
                title_font=dict(size=14, color="#16857a"),
                yaxis=dict(autorange="reversed"),
                margin=dict(l=20, r=20, t=30, b=30),
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info(
                "Nenhum dado biológico encontrado para o mês/ano selecionado."
            )

        st.write("---")

        st.markdown("##### 📄 Central de Relatórios para Fiscais e Auditores")
        st.caption(
            "Gere instantaneamente o arquivo consolidado da base de dados."
        )

        dados_excel = gerar_excel()
        nome_arquivo = (
            f"relatorio_auditoria_{ano_selecionado}_{mes_selecionado}.xlsx"
        )

        st.download_button(
            label="📥 Exportar Relatório em Excel",
            data=dados_excel,
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ============================================================
# PÁGINA 2: REGISTRO DE AMOSTRAS
# ============================================================


def pagina_registro():
    st.title("Registro de Monitoramento")
    df = obter_amostras()
    codigos = df["code"].tolist() if not df.empty else []

    modo = st.radio(
        "Ação",
        ["Novo registro", "Editar registro", "Excluir registro"],
        horizontal=True,
    )

    reg = (
        df[df["code"] == st.selectbox("Selecione o CODE", codigos)]
        .iloc[0]
        .fillna("")
        .to_dict()
        if modo in ["Editar registro", "Excluir registro"] and codigos
        else {}
    )

    if modo == "Excluir registro":
        if "msg_exclusao_ok" in st.session_state:
            st.success(st.session_state.pop("msg_exclusao_ok"))

        if not codigos:
            st.info("Nenhum registro encontrado para excluir.")
            return

        st.warning(
            "⚠️ Atenção: Você está prestes a excluir definitivamente a amostra"
            f" {reg.get('code')}."
        )
        st.markdown(
            f"""
            * **Origem:** {reg.get('origin', '—')}
            * **Área:** {reg.get('area', '—')}
            * **Data de Coleta:** {reg.get('data', '—')}
            * **Resultado:** {reg.get('resultado_final', '—')}
            """
        )

        confirmar_exclusao = st.checkbox(
            "Confirmo que quero deletar permanentemente a amostra"
            f" {reg.get('code')}"
        )

        if st.button(
            "❌ Deletar Registro Permanentemente",
            type="primary",
            disabled=not confirmar_exclusao,
            use_container_width=True,
        ):
            code_deletado = reg.get("code")
            excluir_amostra(code_deletado)
            st.session_state["msg_exclusao_ok"] = (
                f"Amostra {code_deletado} deletada com sucesso! ✅"
            )
            st.rerun()

        st.divider()

    else:
        with st.form("form_amostra"):
            col1, col2, col3, col4 = st.columns(4)

            if modo == "Novo registro":
                ultimo_registro = consultar(
                    "SELECT code FROM amostras ORDER BY code DESC LIMIT 1"
                )
                if ultimo_registro and len(ultimo_registro) > 0:
                    ultimo_code = ultimo_registro[0]["code"]
                    try:
                        prefixo, numero = ultimo_code.split("-")
                        proximo_numero = int(numero) + 1
                        code_sugerido = f"{prefixo}-{proximo_numero:03d}"
                    except ValueError:
                        code_sugerido = "B4-001"
                else:
                    code_sugerido = "B4-001"

                code = col1.text_input("CODE *", value=code_sugerido)
            else:
                code = col1.text_input(
                    "CODE *", reg.get("code", ""), disabled=True
                )

            sample_id = col2.text_input(
                "ID",
                value=reg.get("sample_id", ""),
                placeholder="LIMS ou Micro Sample Number",
            )
            ponto = col3.text_input("OBSERVATION", reg.get("ponto", ""))
            analista = col4.text_input("ANALYST", reg.get("analista", ""))

            col5, col6, col7 = st.columns(3)
            with col5:
                origin = campo_selecao(
                    "ORIGIN", "ORIGIN", reg.get("origin", "")
                )
            with col6:
                sample = campo_selecao(
                    "SAMPLE", "SAMPLE", reg.get("sample", "")
                )
            with col7:
                sampling = campo_selecao(
                    "SAMPLING", "SAMPLING", reg.get("sampling", "")
                )

            col8, col9, col10 = st.columns(3)
            with col8:
                area = campo_selecao("AREA", "AREA", reg.get("area", ""))
            with col9:
                collection_point = campo_selecao(
                    "COLLECTION POINT",
                    "COLLECTION POINT",
                    reg.get("collection_point", ""),
                )
            with col10:
                method = campo_selecao(
                    "METHOD", "METHOD", reg.get("method", "")
                )

            col11, col12, col13 = st.columns(3)
            with col11:
                frequencia = st.selectbox(
                    "FREQUENCY",
                    ["", "Semanal", "Mensal"],
                    index=["", "Semanal", "Mensal"].index(
                        reg.get("frequencia", "")
                    )
                    if reg.get("frequencia", "") in ["", "Semanal", "Mensal"]
                    else 0,
                )
            with col12:
                dt_at = pd.to_datetime(reg.get("data", ""), errors="coerce")
                data = st.date_input(
                    "DATE",
                    value=None if pd.isna(dt_at) else dt_at.date(),
                    format="DD/MM/YYYY",
                )
            with col13:
                resultado_final = st.selectbox(
                    "RESULT",
                    ["", "Conforme", "Não Conforme"],
                    index=["", "Conforme", "Não Conforme"].index(
                        reg.get("resultado_final", "")
                    )
                    if reg.get("resultado_final", "")
                    in ["", "Conforme", "Não Conforme"]
                    else 0,
                )

            enviado_reg = st.form_submit_button(
                "Salvar Registro", type="primary"
            )

        if enviado_reg and code.strip():
            salvar_amostra({
                "code": code.strip(),
                "sample_id": sample_id.strip(),
                "ponto": ponto,
                "origin": origin,
                "area": area,
                "sample": sample,
                "collection_point": collection_point,
                "sampling": sampling,
                "method": method,
                "frequencia": frequencia,
                "analista": analista,
                "data": data.isoformat() if data else "",
                "resultado_final": resultado_final,
            })
            st.success("Registro Corretamente Salvo!")
            st.rerun()

    st.subheader("Amostras cadastradas")
    config_colunas = {
        "code": "CODE",
        "sample_id": "ID",
        "ponto": "OBSERVATION",
        "origin": "ORIGIN",
        "area": "AREA",
        "sample": "SAMPLE",
        "collection_point": "COLLECTION POINT",
        "sampling": "SAMPLING",
        "method": "METHOD",
        "frequencia": "FREQUENCY",
        "analista": "ANALYST",
        "data": "DATE",
        "resultado_final": "RESULT",
    }
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=config_colunas,
    )

# ============================================================
# PÁGINA 3: IDENTIFICAÇÃO MICROBIOLÓGICA
# ============================================================


def pagina_identificacao():
    st.title("Identificação Microbiológica")

    df = obter_identificacoes()

    if df.empty:
        st.info("Cadastre uma amostra antes de preencher a identificação.")
        return

    code = st.selectbox("Selecione o CODE", df["code"].tolist())

    registro = df[df["code"] == code].iloc[0].fillna("").to_dict()

    st.info(
        f"Área: {registro.get('area', '—')} | "
        f"Ponto: {registro.get('collection_point', '—')} | "
        f"Data: {registro.get('data', '—')}"
    )

    with st.form("formulario_identificacao"):
        coluna1, coluna2 = st.columns(2)

        with coluna1:
            form = campo_selecao(
                "MORPHOLOGY", "FORM", registro.get("form", "")
            )
            gram_stain = campo_selecao(
                "GRAM STAIN", "AFFIRMATION", registro.get("gram_stain", "")
            )
            identification = st.text_input(
                "IDENTIFICATION", registro.get("identification", "")
            )

            opcoes_metodo = ["", "NGS Sequencing", "Maldi TOF", "Others"]
            valor_salvo = registro.get("outsourced_method", "")
            if valor_salvo == "Sequenciamento NGS":
                valor_salvo = "NGS Sequencing"
            if valor_salvo == "Outros":
                valor_salvo = "Others"
            if valor_salvo not in opcoes_metodo:
                opcoes_metodo.append(valor_salvo)

            indice_metodo = (
                opcoes_metodo.index(valor_salvo)
                if valor_salvo in opcoes_metodo
                else 0
            )
            outsourced_method = st.selectbox(
                "OUTSOURCED METHOD", opcoes_metodo, index=indice_metodo
            )

        with coluna2:
            company = st.text_input("COMPANY", registro.get("company", ""))
            col_data1, col_data2 = st.columns(2)

            with col_data1:
                data_inicio_atual = pd.to_datetime(
                    registro.get("start_date", ""), errors="coerce"
                )
                start_date = st.date_input(
                    "START DATE",
                    value=None
                    if pd.isna(data_inicio_atual)
                    else data_inicio_atual.date(),
                    format="DD/MM/YYYY",
                )

            with col_data2:
                data_final_atual = pd.to_datetime(
                    registro.get("end_date", ""), errors="coerce"
                )
                end_date = st.date_input(
                    "END DATE",
                    value=None
                    if pd.isna(data_final_atual)
                    else data_final_atual.date(),
                    format="DD/MM/YYYY",
                )

            arquivo_anexo = st.file_uploader(
                "ATTACH REPORT (Word, Excel, Foto ou PDF)",
                type=["doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "pdf"],
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
                _cursor = conexao.execute(
                    "SELECT report_data FROM identificacoes WHERE code = ?",
                    (code,),
                )
                _linha = _cursor.fetchone()
                if _linha and _linha["report_data"]:
                    bytes_reais = _linha["report_data"]
            except sqlite3.OperationalError:
                conexao.execute(
                    "ALTER TABLE identificacoes ADD COLUMN report_data BLOB"
                )
                conexao.commit()

        if bytes_reais and len(bytes_reais) > 100:
            st.download_button(
                label=f"📥 Baixar/Abrir Documento Físico: {nome_arquivo_salvo}",
                data=bytes_reais,
                file_name=nome_arquivo_salvo,
                mime="application/octet-stream",
                use_container_width=True,
            )
        else:
            st.warning(
                "⚠️ O arquivo antigo continha apenas metadados de texto. Faça"
                " um novo upload no campo acima para registrar o arquivo"
                " físico."
            )
    else:
        st.caption(
            "ℹ️ Nenhum documento ou foto foi anexado para esta amostra ainda."
        )

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
            try:
                conexao.execute(
                    "ALTER TABLE identificacoes ADD COLUMN report_data BLOB"
                )
                conexao.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conexao.execute(
                    "ALTER TABLE identificacoes ADD COLUMN start_date TEXT"
                )
                conexao.commit()
            except sqlite3.OperationalError:
                pass

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
            code,
            form,
            registro.get("margin", ""),
            registro.get("pigment", ""),
            gram_stain,
            registro.get("catalase", ""),
            registro.get("koh", ""),
            registro.get("oxidase", ""),
            outsourced_method,
            identification,
            nome_relatorio,
            company,
            (end_date.isoformat() if end_date else ""),
            bytes_arquivo,
            (start_date.isoformat() if start_date else ""),
        )

        with conectar() as conexao:
            conexao.execute(sql_salvar, valores)

        st.success(f"Identificação de {code} salva com sucesso!")
        st.rerun()

    st.subheader("Identificações cadastradas")

    colunas_visiveis = [
        "code",
        "area",
        "collection_point",
        "data",
        "form",
        "gram_stain",
        "identification",
        "outsourced_method",
        "report",
        "company",
        "start_date",
        "end_date",
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
            "end_date": "END DATE",
        },
    )

# ============================================================
# PÁGINA 4: ARMAZENAMENTO DE CEPAS E ETIQUETAS ZEBRA
# ============================================================


def salvar_armazenamento(
    code,
    box,
    backup_box,
    freezer,
    storage_date,
    analyst,
    backup_used,
    posicao=None,
    posicao_backup=None,
):
    with conectar() as conexao:
        try:
            conexao.execute(
                "ALTER TABLE armazenamento_cepas ADD COLUMN posicao INTEGER"
            )
            conexao.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conexao.execute(
                "ALTER TABLE armazenamento_cepas ADD COLUMN posicao_backup"
                " INTEGER"
            )
            conexao.commit()
        except sqlite3.OperationalError:
            pass

        conexao.execute(
            """
            INSERT OR REPLACE INTO armazenamento_cepas (
                code, box, backup_box, freezer, storage_date, analyst, backup_used, posicao, posicao_backup
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                code,
                box,
                backup_box,
                freezer,
                storage_date,
                analyst,
                backup_used,
                posicao,
                posicao_backup,
            ),
        )


def excluir_armazenamento(code):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM armazenamento_cepas WHERE code = ?", (code,)
        )


def obter_armazenamento():
    with conectar() as conexao:
        try:
            conexao.execute(
                "ALTER TABLE armazenamento_cepas ADD COLUMN posicao INTEGER"
            )
        except sqlite3.OperationalError:
            pass
        try:
            conexao.execute(
                "ALTER TABLE armazenamento_cepas ADD COLUMN posicao_backup"
                " INTEGER"
            )
        except sqlite3.OperationalError:
            pass
        return pd.read_sql_query("SELECT * FROM armazenamento_cepas", conexao)


def pagina_armazenamento():
    st.title("🧫 Armazenamento de Isolados Identificados")
    st.caption("Gestão do banco de cepas e rastreabilidade dos isolados.")

    df = obter_identificacoes()
    if df.empty:
        st.info("Cadastre uma amostra antes de preencher a identificação.")
        return

    df_filtrado = df[
        df["identification"].fillna("").str.strip() != ""
    ].copy()
    if df_filtrado.empty:
        st.info("Nenhum microrganismo identificado disponível.")
        return

    codigos = sorted(df_filtrado["code"].unique())
    dados = obter_armazenamento()

    modo = st.radio(
        "Ação",
        ["Novo Registro", "Editar Registro", "Excluir Registro"],
        horizontal=True,
    )
    registro = {}

    if modo in ["Editar Registro", "Excluir Registro"] and not dados.empty:
        codigo_selecionado = st.selectbox(
            "Selecione o CODE", dados["code"].tolist(), key="sb_code_edicao"
        )
        busca_filtrada = dados[dados["code"] == codigo_selecionado]
        if not busca_filtrada.empty:
            registro = busca_filtrada.iloc.to_dict()
        else:
            st.error("Erro interno: Registro não encontrado.")
            return

    if modo == "Excluir Registro":
        if dados.empty:
            st.info("Nenhum registro encontrado.")
            return

        st.warning(
            f"⚠️ O registro {registro.get('code','')} será removido"
            " permanentemente."
        )
        confirmar = st.checkbox("Confirmo a exclusão deste registro")

        if st.button(
            "🗑️ Excluir Registro",
            disabled=not confirmar,
            use_container_width=True,
        ):
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
                code = st.text_input(
                    "Code", value=str(registro.get("code", "")), disabled=True
                )
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
                dt_at = pd.to_datetime(
                    registro.get("storage_date", ""), errors="coerce"
                )
                storage_date = st.date_input(
                    "Storage Date",
                    value=None if pd.isna(dt_at) else dt_at.date(),
                    format="DD/MM/YYYY",
                )
                backup_used = st.selectbox(
                    "Backup Used",
                    ["No", "Yes"],
                    index=0 if valor_backup_used == "No" else 1,
                )

            st.markdown("---")
            col_box_principal, col_espaco, col_box_backup = st.columns(
                [1, 0.1, 1]
            )

            # CAIXA PRINCIPAL
            with col_box_principal:
                st.subheader("📦 Caixa Principal")
                st.markdown(
                    "<p style='font-size:12px; margin-top:-10px;"
                    " color:#7f8c8d;'>🟢 Livre | 🔵 Selecionado | 🔴"
                    " Ocupado</p>",
                    unsafe_allow_html=True,
                )

                box = st.selectbox(
                    "Box",
                    ["C1", "C2", "C3", "C4", "C5"],
                    index=["C1", "C2", "C3", "C4", "C5"].index(valor_box)
                    if valor_box in ["C1", "C2", "C3", "C4", "C5"]
                    else 0,
                    key="sb_box_main",
                )

                dados_persistidos = obter_armazenamento()
                ocupadas_main = {}
                if not dados_persistidos.empty:
                    for _, reg_db in dados_persistidos.iterrows():
                        b_banco = str(reg_db.get("box")).strip()
                        p_banco = str(reg_db.get("posicao")).strip()
                        c_banco = str(reg_db.get("code")).strip()
                        if (
                            b_banco == str(box).strip()
                            and p_banco != ""
                            and p_banco != "None"
                        ):
                            try:
                                p_limpo = int(float(p_banco))
                                ocupadas_main[p_limpo] = c_banco
                            except ValueError:
                                pass

                if modo == "Editar Registro" and pos_salva_principal:
                    try:
                        ocupadas_main.pop(int(float(pos_salva_principal)), None)
                    except (ValueError, TypeError):
                        pass

                opcoes_pos_main = [""] + [
                    p for p in range(1, 82) if p not in ocupadas_main
                ]
                idx_main = 0
                if pos_salva_principal:
                    try:
                        p_int = int(float(pos_salva_principal))
                        if p_int in opcoes_pos_main:
                            idx_main = opcoes_pos_main.index(p_int)
                    except (ValueError, TypeError):
                        pass

                posicao_escolhida_main = st.selectbox(
                    f"Posição na Caixa {box} *",
                    opcoes_pos_main,
                    index=idx_main,
                    format_func=lambda x: f"Posição {x:02d}"
                    if x != ""
                    else "Escolha uma posição...",
                    key="pos_main_select",
                )

                st.markdown(
                    "<p style='font-size:13px; font-weight:bold; color:#612147;"
                    " margin-top:10px; margin-bottom:5px;'>Mapa de"
                    " Ocupação:</p>",
                    unsafe_allow_html=True,
                )
                for i in range(0, 81, 9):
                    cols_m = st.columns(9)
                    for j in range(9):
                        pos = i + j + 1
                        try:
                            check_main = posicao_escolhida_main != "" and pos == int(
                                posicao_escolhida_main
                            )
                        except (ValueError, TypeError):
                            check_main = False

                        if check_main:
                            cor = "#3498db"
                            label_html = f"🔵 {pos:02d}"
                        elif pos in ocupadas_main:
                            cor = "#e74c3c"
                            label_html = f"🔴 {pos:02d}"
                        else:
                            cor = "#2ecc71"
                            label_html = f"🟢 {pos:02d}"
                        cols_m[j].markdown(
                            "<div style='text-align:center; font-size:11px;"
                            f" font-weight:bold; color:{cor}; margin:2px"
                            f" 0;'>{label_html}</div>",
                            unsafe_allow_html=True,
                        )

            # CAIXA DE BACKUP
            with col_box_backup:
                st.subheader("🛡️ Caixa de Backup")
                st.markdown(
                    "<p style='font-size:12px; margin-top:-10px;"
                    " color:#7f8c8d;'>🟢 Livre | 🔵 Selecionado | 🔴"
                    " Ocupado</p>",
                    unsafe_allow_html=True,
                )

                backup_box = st.selectbox(
                    "Backup Box",
                    ["C1", "C2", "C3", "C4", "C5"],
                    index=["C1", "C2", "C3", "C4", "C5"].index(valor_backup_box)
                    if valor_backup_box in ["C1", "C2", "C3", "C4", "C5"]
                    else 0,
                    key="sb_box_backup",
                )

                ocupadas_backup = {}
                if not dados_persistidos.empty:
                    for _, reg_db in dados_persistidos.iterrows():
                        b_banco = str(reg_db.get("backup_box")).strip()
                        p_banco = str(reg_db.get("posicao_backup")).strip()
                        c_banco = str(reg_db.get("code")).strip()
                        if (
                            b_banco == str(backup_box).strip()
                            and p_banco != ""
                            and p_banco != "None"
                        ):
                            try:
                                p_limpo = int(float(p_banco))
                                ocupadas_backup[p_limpo] = c_banco
                            except ValueError:
                                pass

                if modo == "Editar Registro" and pos_salva_backup:
                    try:
                        ocupadas_backup.pop(int(float(pos_salva_backup)), None)
                    except (ValueError, TypeError):
                        pass

                opcoes_pos_backup = [""] + [
                    p for p in range(1, 82) if p not in ocupadas_backup
                ]
                idx_backup = 0
                if pos_salva_backup:
                    try:
                        p_int = int(float(pos_salva_backup))
                        if p_int in opcoes_pos_backup:
                            idx_backup = opcoes_pos_backup.index(p_int)
                    except (ValueError, TypeError):
                        pass

                posicao_escolhida_backup = st.selectbox(
                    f"Posição na Caixa de Backup {backup_box} *",
                    opcoes_pos_backup,
                    index=idx_backup,
                    format_func=lambda x: f"Posição {x:02d}"
                    if x != ""
                    else "Escolha uma posição...",
                    key="pos_backup_select",
                )

                st.markdown(
                    "<p style='font-size:13px; font-weight:bold; color:#612147;"
                    " margin-top:10px; margin-bottom:5px;'>Mapa de"
                    " Ocupação:</p>",
                    unsafe_allow_html=True,
                )
                for i in range(0, 81, 9):
                    cols_b = st.columns(9)
                    for j in range(9):
                        pos = i + j + 1
                        try:
                            check_backup = (
                                posicao_escolhida_backup != ""
                                and pos == int(posicao_escolhida_backup)
                            )
                        except (ValueError, TypeError):
                            check_backup = False

                        if check_backup:
                            cor = "#3498db"
                            label_html = f"🔵 {pos:02d}"
                        elif pos in ocupadas_backup:
                            cor = "#e74c3c"
                            label_html = f"🔴 {pos:02d}"
                        else:
                            cor = "#2ecc71"
                            label_html = f"🟢 {pos:02d}"
                        cols_b[j].markdown(
                            "<div style='text-align:center; font-size:11px;"
                            f" font-weight:bold; color:{cor}; margin:2px"
                            f" 0;'>{label_html}</div>",
                            unsafe_allow_html=True,
                        )

            st.markdown("---")
            btn_texto = (
                "Salvar Alterações 💾"
                if modo == "Editar Registro"
                else "Gravar Armazenamento 💾"
            )
            btn_enviar = st.form_submit_button(
                btn_texto, use_container_width=True
            )

            if btn_enviar:
                if (
                    str(posicao_escolhida_main) == ""
                    or str(posicao_escolhida_backup) == ""
                ):
                    st.error(
                        "❌ Por favor, selecione as posições obrigatórias em"
                        " ambas as caixas antes de gravar."
                    )
                else:
                    dt_iso = storage_date.isoformat() if storage_date else ""
                    salvar_armazenamento(
                        code,
                        box,
                        backup_box,
                        freezer,
                        dt_iso,
                        analyst,
                        backup_used,
                        int(posicao_escolhida_main),
                        int(posicao_escolhida_backup),
                    )
                    st.toast("Armazenamento gravado com sucesso! ✅")
                    st.rerun()

    st.divider()
    dados = obter_armazenamento()
    if not dados.empty:
        total_isolados = len(dados)
        st.metric(
            "🦠 Total de Isolados Preservados no Banco", f"{total_isolados} un"
        )

        colunas_existentes = dados.columns
        mapeamento = {
            "code": "CODE",
            "box": "BOX",
            "posicao": "POSITION",
            "backup_box": "BACKUP BOX",
            "posicao_backup": "BACKUP POSITION",
            "freezer": "FREEZER",
            "storage_date": "STORAGE DATE",
            "analyst": "ANALYST",
            "backup_used": "BACKUP USED",
        }
        mapeamento_valido = {
            k: v for k, v in mapeamento.items() if k in colunas_existentes
        }
        dados_exibicao = dados.rename(columns=mapeamento_valido)
        colunas_exibir = [
            v for k, v in mapeamento_valido.items() if v in dados_exibicao.columns
        ]

        if colunas_exibir:
            st.dataframe(
                dados_exibicao[colunas_exibir],
                use_container_width=True,
                hide_index=True,
            )

        # GERADOR DE ETIQUETAS ZEBRA
        st.divider()
        st.subheader("🏷️ Impressão de Etiquetas para Criotubos (Zebra)")
        st.caption(
            "Selecione uma cepa salva para gerar o PDF pronto para impressão."
        )

        col_etq1, col_etq2, col_etq3 = st.columns([1.5, 1.5, 1])

        with col_etq1:
            code_etiqueta = st.selectbox(
                "Selecione o CODE para etiqueta",
                dados["code"].tolist(),
                key="sb_code_etiqueta",
            )

        with col_etq2:
            impressora_selecionada = st.selectbox(
                "Impressora de Destino",
                [
                    "Zebra ZD220 (Laboratório Micro)",
                    "Zebra GK420t (Sala de Preparo)",
                    "Zebra ZT230 (Biobanco)",
                    "Impressora Padrão (PDF / Navegador)",
                ],
                key="sb_impressora",
            )

        with col_etq3:
            tipo_etiqueta = st.selectbox(
                "Tipo de Tubo",
                ["Caixa Principal", "Caixa de Backup", "Ambas (2 etiquetas)"],
                key="sb_tipo_etiqueta",
            )

        reg_etq = dados[dados["code"] == code_etiqueta].iloc

        df_id_etq = obter_identificacoes()
        nome_microrganismo = "Não identificado"
        if not df_id_etq.empty and code_etiqueta in df_id_etq["code"].values:
            ident_val = df_id_etq[df_id_etq["code"] == code_etiqueta][
                "identification"
            ].iloc
            if pd.notna(ident_val) and str(ident_val).strip() != "":
                nome_microrganismo = str(ident_val).strip()

        box_etq = reg_etq.get("box", "-")
        pos_etq = (
            f"{int(float(reg_etq['posicao'])):02d}"
            if pd.notna(reg_etq.get("posicao"))
            and str(reg_etq.get("posicao")).strip() != ""
            else "-"
        )
        b_box_etq = reg_etq.get("backup_box", "-")
        b_pos_etq = (
            f"{int(float(reg_etq['posicao_backup'])):02d}"
            if pd.notna(reg_etq.get("posicao_backup"))
            and str(reg_etq.get("posicao_backup")).strip() != ""
            else "-"
        )
        data_etq = reg_etq.get("storage_date", "-")

        nome_imp_curto = (
            impressora_selecionada.split(" ")
            if impressora_selecionada
            else ""
        )
        data_formatada = (
            str(data_etq).strip()
            if pd.notna(data_etq)
            and str(data_etq).strip() not in ["", "None", "-"]
            else "—"
        )

        st.markdown("##### 👁️ Pré-visualização da Etiqueta")
        c_prev1, c_prev2 = st.columns(2)

        if tipo_etiqueta in ["Caixa Principal", "Ambas (2 etiquetas)"]:
            with c_prev1:
                st.markdown(
                    f"""
                    <div style="border: 2px dashed #612147; border-radius: 8px; padding: 12px; background-color: #ffffff; color: #000000; font-family: monospace; max-width: 320px;">
                        <div style="font-size: 16px; font-weight: bold;">🧬 {code_etiqueta} | PRINCIPAL</div>
                        <div style="font-size: 13px; font-weight: bold; margin-top: 4px;">{nome_microrganismo[:28]}</div>
                        <div style="font-size: 12px; margin-top: 4px;">Caixa: <b>{box_etq}</b> | Pos: <b>{pos_etq}</b></div>
                        <div style="font-size: 11px; color: #444;">Data: {data_formatada} | {nome_imp_curto}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if tipo_etiqueta in ["Caixa de Backup", "Ambas (2 etiquetas)"]:
            with c_prev2:
                st.markdown(
                    f"""
                    <div style="border: 2px dashed #1f618d; border-radius: 8px; padding: 12px; background-color: #ffffff; color: #000000; font-family: monospace; max-width: 320px;">
                        <div style="font-size: 16px; font-weight: bold;">🛡️ {code_etiqueta} | BACKUP</div>
                        <div style="font-size: 13px; font-weight: bold; margin-top: 4px;">{nome_microrganismo[:28]}</div>
                        <div style="font-size: 12px; margin-top: 4px;">Caixa: <b>{b_box_etq}</b> | Pos: <b>{b_pos_etq}</b></div>
                        <div style="font-size: 11px; color: #444;">Data: {data_formatada} | {nome_imp_curto}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        buffer_pdf = io.BytesIO()
        c = canvas.Canvas(buffer_pdf, pagesize=(35 * mm, 20 * mm))
        margem_esq = 4 * mm

        if tipo_etiqueta in ["Caixa Principal", "Ambas (2 etiquetas)"]:
            c.setFont("Helvetica-Bold", 6.5)
            c.drawString(margem_esq, 14.5 * mm, f"{code_etiqueta} | PRINCIPAL")
            c.setFont("Helvetica-Bold", 5.5)
            c.drawString(margem_esq, 11 * mm, f"{nome_microrganismo[:26]}")
            c.setFont("Helvetica", 5)
            c.drawString(
                margem_esq, 7.5 * mm, f"Caixa: {box_etq} | Pos: {pos_etq}"
            )
            c.setFont("Helvetica", 4.5)
            c.drawString(
                margem_esq, 4 * mm, f"Data: {data_formatada} | {nome_imp_curto}"
            )
            c.showPage()

        if tipo_etiqueta in ["Caixa de Backup", "Ambas (2 etiquetas)"]:
            c.setFont("Helvetica-Bold", 6.5)
            c.drawString(margem_esq, 14.5 * mm, f"{code_etiqueta} | BACKUP")
            c.setFont("Helvetica-Bold", 5.5)
            c.drawString(margem_esq, 11 * mm, f"{nome_microrganismo[:26]}")
            c.setFont("Helvetica", 5)
            c.drawString(
                margem_esq, 7.5 * mm, f"Caixa: {b_box_etq} | Pos: {b_pos_etq}"
            )
            c.setFont("Helvetica", 4.5)
            c.drawString(
                margem_esq, 4 * mm, f"Data: {data_formatada} | {nome_imp_curto}"
            )
            c.showPage()

        c.save()
        pdf_bytes = buffer_pdf.getvalue()

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="🖨️ Baixar Etiqueta em PDF (Pronta para Imprimir)",
            data=pdf_bytes,
            file_name=f"etiqueta_{code_etiqueta}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

# ============================================================
# PÁGINA 5: IMPORTAÇÃO E EXPORTAÇÃO DE EXCEL
# ============================================================


def normalizar_coluna_sistema(nome):
    conversoes = {
        "CODE": "code",
        "ID": "sample_id",
        "SAMPLE_ID": "sample_id",
        "PONTO": "ponto",
        "OBSERVATION": "ponto",
        "ORIGIN": "origin",
        "AREA": "area",
        "SAMPLE": "sample",
        "COLLECTION POINT": "collection_point",
        "SAMPLING": "sampling",
        "METHOD": "method",
        "FREQUÊNCIA": "frequencia",
        "FREQUENCIA": "frequencia",
        "FREQUENCY": "frequencia",
        "ANALISTA": "analista",
        "ANALYST": "analista",
        "DATA": "data",
        "DATE": "data",
        "RESULTADO": "resultado_final",
        "RESULT": "resultado_final",
        "RESULTADO_FINAL": "resultado_final",
        "FORM": "form",
        "MORPHOLOGY": "form",
        "MARGIN": "margin",
        "PIGMENT": "pigment",
        "GRAM STAIN": "gram_stain",
        "CATALASE": "catalase",
        "KOH": "koh",
        "OXIDASE": "oxidase",
        "OUTSOURCED METHOD": "outsourced_method",
        "IDENTIFICATION": "identification",
        "REPORT": "report",
        "ATTACH REPORT": "report",
        "COMPANY": "company",
        "START DATE": "start_date",
        "END DATE": "end_date",
        "TSB": "tsb",
        "VALIDADE TSB": "tsb_val",
        "TSB_VAL": "tsb_val",
        "GLICERINA": "glicerina",
        "TSA": "tsa",
        "VALIDADE TSA": "tsa_val",
        "TSA_VAL": "tsa_val",
        "CRIOTUBO": "criotubo",
        "PLACA DE PETRI": "placa_de_petri",
        "PLACA PETRI": "placa_de_petri",
        "FLUXO LAMINAR": "fluxo_laminar",
        "ULTRAFREEZER": "ultrafreezer",
    }
    chave = str(nome).strip().upper()
    return conversoes.get(chave, str(nome).strip().lower().replace(" ", "_"))


def gerar_excel(df_filtrado=None):
    arquivo = BytesIO()
    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        if df_filtrado is not None:
            df_export = df_filtrado.copy()
            if "data" in df_export.columns:
                df_export["data"] = df_export["data"].astype(str).replace("NaT", "")
            df_export.to_excel(writer, sheet_name="Auditoria_Filtrada", index=False)
        else:
            amostras = obter_amostras()
            identificacoes = obter_identificacoes()
            armazenamento = obter_armazenamento()

            if not armazenamento.empty:
                armazenamento = armazenamento.rename(
                    columns={
                        "code": "CODE",
                        "box": "BOX",
                        "posicao": "POSITION",
                        "backup_box": "BACKUP BOX",
                        "posicao_backup": "BACKUP POSITION",
                        "freezer": "FREEZER",
                        "storage_date": "STORAGE DATE",
                        "analyst": "ANALYST",
                        "backup_used": "BACKUP USED",
                    }
                )

            amostras.to_excel(writer, sheet_name="Registro", index=False)
            identificacoes.to_excel(writer, sheet_name="Identification", index=False)
            armazenamento.to_excel(writer, sheet_name="Storage", index=False)

    return arquivo.getvalue()


def importar_excel(arquivo):
    xl = pd.ExcelFile(arquivo)
    abas = xl.sheet_names

    with conectar() as conexao:
        try:
            if "Dados Brutos" in abas:
                df_brutos = pd.read_excel(xl, sheet_name="Dados Brutos")
                df_brutos.columns = [
                    normalizar_coluna_sistema(col) for col in df_brutos.columns
                ]
                colunas_obrigatorias = [
                    "tsb",
                    "tsb_val",
                    "glicerina",
                    "tsa",
                    "tsa_val",
                    "criotubo",
                    "placa_de_petri",
                    "fluxo_laminar",
                    "ultrafreezer",
                ]
                for col in colunas_obrigatorias:
                    if col not in df_brutos.columns:
                        df_brutos[col] = ""
                df_brutos = df_brutos.fillna("")

                conexao.execute("DELETE FROM dados_brutos")
                for _, linha in df_brutos.iterrows():
                    conexao.execute(
                        """
                        INSERT INTO dados_brutos (
                            tsb, tsb_val, glicerina, tsa, tsa_val,
                            criotubo, placa_de_petri, fluxo_laminar, ultrafreezer
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        tuple(str(linha.get(c, "")) for c in colunas_obrigatorias),
                    )
        except Exception:
            pass

        try:
            if "Registro" in abas:
                registro = pd.read_excel(xl, sheet_name="Registro")
                registro.columns = [
                    normalizar_coluna_sistema(c) for c in registro.columns
                ]
                for col in COLUNAS_AMOSTRA:
                    if col not in registro.columns:
                        registro[col] = ""
                registro = registro[COLUNAS_AMOSTRA].fillna("")
                registro = registro[
                    registro["code"].astype(str).str.strip().ne("")
                ]
                registro["data"] = (
                    pd.to_datetime(registro["data"], errors="coerce")
                    .dt.strftime("%Y-%m-%d")
                    .fillna("")
                )

                conexao.execute("DELETE FROM identificacoes")
                conexao.execute("DELETE FROM amostras")

                for _, r in registro.iterrows():
                    conexao.execute(
                        f"INSERT INTO amostras ({','.join(COLUNAS_AMOSTRA)}) "
                        f"VALUES ({','.join('?' for _ in COLUNAS_AMOSTRA)})",
                        [str(r.get(c, "")) for c in COLUNAS_AMOSTRA],
                    )

            if "Identification" in abas:
                identificacao = pd.read_excel(xl, sheet_name="Identification")
                identificacao.columns = [
                    normalizar_coluna_sistema(c) for c in identificacao.columns
                ]
                for col in COLUNAS_IDENTIFICACAO:
                    if col not in identificacao.columns:
                        identificacao[col] = ""
                identificacao = identificacao[COLUNAS_IDENTIFICACAO].fillna("")
                identificacao = identificacao[
                    identificacao["code"].astype(str).str.strip().ne("")
                ]

                for col_dt in ["start_date", "end_date"]:
                    identificacao[col_dt] = (
                        pd.to_datetime(identificacao[col_dt], errors="coerce")
                        .dt.strftime("%Y-%m-%d")
                        .fillna("")
                    )

                codigos_validos = {
                    row["code"]
                    for row in conexao.execute("SELECT code FROM amostras").fetchall()
                }
                for _, i in identificacao.iterrows():
                    if str(i["code"]).strip() in codigos_validos:
                        conexao.execute(
                            f"INSERT OR REPLACE INTO identificacoes ({','.join(COLUNAS_IDENTIFICACAO)}) "
                            f"VALUES ({','.join('?' for _ in COLUNAS_IDENTIFICACAO)})",
                            [str(i.get(c, "")) for c in COLUNAS_IDENTIFICACAO],
                        )
        except Exception as e:
            st.error(f"Erro nas planilhas padrão: {e}")


def pagina_dados():
    st.title("Importação e Exportação")
    st.download_button(
        label="Baixar dados em Excel",
        data=gerar_excel(),
        file_name="monitoramento_microbiologico.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.divider()
    st.subheader("Importar arquivo Excel")
    st.warning("A importação substituirá os registros atuais. Faça backup antes.")

    arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
    confirmar = st.checkbox("Confirmo a substituição total")

    if (
        arquivo is not None
        and confirmar
        and st.button("Importar dados", type="primary")
    ):
        try:
            importar_excel(arquivo)
            st.success("Dados importados com sucesso.")
            st.rerun()
        except Exception as erro:
            st.error(f"Erro na importação: {erro}")

# ============================================================
# PÁGINA 6: DADOS BRUTOS
# ============================================================


def pagina_dados_brutos():
    st.title("🗃️ Registro de Dados Brutos (Raw Data)")
    st.caption(
        "Gerenciamento e monitoramento automático de validades de insumos e"
        " meios de cultura."
    )

    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS dados_brutos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tsb TEXT, tsb_val TEXT,
                glicerina TEXT, glicerina_val TEXT,
                tsa TEXT, tsa_val TEXT,
                criotubo TEXT, placa_de_petri TEXT, fluxo_laminar TEXT, ultrafreezer TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    try:
        linhas = consultar(
            "SELECT id, tsb, tsb_val, glicerina, tsa, tsa_val, criotubo,"
            " placa_de_petri, fluxo_laminar, ultrafreezer FROM dados_brutos"
            " ORDER BY id DESC"
        )
    except Exception:
        linhas = []

    df_brutos = pd.DataFrame(linhas)
    lista_ids = df_brutos["id"].tolist() if not df_brutos.empty else []

    modo = st.radio(
        "Ação",
        [
            "📋 Visualizar Planilha & Alertas",
            "➕ Inserir Linha Manual",
            "✏️ Editar Linha",
            "❌ Excluir Linha",
        ],
        horizontal=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if modo == "📋 Visualizar Planilha & Alertas":
        if df_brutos.empty:
            st.info(
                "Nenhum dado bruto encontrado. Cadastre manualmente ou via"
                " importação."
            )
        else:
            st.markdown("### 🚦 Status e Alertas de Validade")

            def mapear_status_validade(data_texto):
                if not data_texto or str(data_texto).strip() in ["", "—", "None"]:
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
            df_visualizacao["STATUS TSB"] = df_visualizacao["tsb_val"].apply(
                mapear_status_validade
            )
            df_visualizacao["STATUS TSA"] = df_visualizacao["tsa_val"].apply(
                mapear_status_validade
            )

            st.dataframe(
                df_visualizacao[
                    [
                        "id",
                        "tsb",
                        "tsb_val",
                        "STATUS TSB",
                        "tsa",
                        "tsa_val",
                        "STATUS TSA",
                        "glicerina",
                        "criotubo",
                        "placa_de_petri",
                        "fluxo_laminar",
                        "ultrafreezer",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "tsb": "LOTE TSB",
                    "tsb_val": "VALIDADE TSB",
                    "tsa": "LOTE TSA",
                    "tsa_val": "VALIDADE TSA",
                    "glicerina": "GLICERINA",
                    "criotubo": "CRIOTUBO",
                    "placa_de_petri": "PLACA PETRI",
                    "fluxo_laminar": "FLUXO LAMINAR",
                    "ultrafreezer": "ULTRAFREEZER",
                },
            )

    elif modo == "❌ Excluir Linha":
        if not lista_ids:
            st.info("Nenhum registro para excluir.")
            return
        id_sel = st.selectbox("Selecione o ID para remover:", lista_ids)
        if st.button(
            "❌ Deletar Permanentemente",
            type="primary",
            use_container_width=True,
        ):
            with conectar() as conexao:
                conexao.execute(
                    "DELETE FROM dados_brutos WHERE id = ?", (id_sel,)
                )
            st.success("Deletado com sucesso!")
            st.rerun()

    else:
        id_sel = None
        reg = {}
        if modo == "✏️ Editar Linha":
            if not lista_ids:
                st.info("Nenhum registro disponível para editar.")
                return
            id_sel = st.selectbox("Selecione o ID para editar:", lista_ids)
            reg = df_brutos[df_brutos["id"] == id_sel].iloc[0].fillna("").to_dict()

        with st.form("form_brutos_validades"):
            st.markdown("##### 🧫 Meios de Cultura (Lote e Validade)")
            col_tsb1, col_tsb2 = st.columns([2, 1])
            tsb = col_tsb1.text_input("Lote TSB", value=reg.get("tsb", ""))
            dt_tsb = pd.to_datetime(reg.get("tsb_val", ""), errors="coerce")
            tsb_val = col_tsb2.date_input(
                "Validade TSB",
                value=None if pd.isna(dt_tsb) else dt_tsb.date(),
                format="DD/MM/YYYY",
            )

            col_tsa1, col_tsa2 = st.columns([2, 1])
            tsa = col_tsa1.text_input("Lote TSA", value=reg.get("tsa", ""))
            dt_tsa = pd.to_datetime(reg.get("tsa_val", ""), errors="coerce")
            tsa_val = col_tsa2.date_input(
                "Validade TSA",
                value=None if pd.isna(dt_tsa) else dt_tsa.date(),
                format="DD/MM/YYYY",
            )

            st.markdown("---")
            st.markdown("##### 📦 Outros Insumos e Equipamentos")
            c1, c2, c3, c4 = st.columns(4)
            glicerina = c1.text_input(
                "GLICERINA", value=reg.get("glicerina", "")
            )
            criotubo = c2.text_input("CRIOTUBO", value=reg.get("criotubo", ""))
            placa = c3.text_input(
                "PLACA DE PETRI", value=reg.get("placa_de_petri", "")
            )
            fluxo = c4.text_input(
                "FLUXO LAMINAR", value=reg.get("fluxo_laminar", "")
            )

            ultrafreezer = st.text_input(
                "ULTRAFREEZER", value=reg.get("ultrafreezer", "")
            )

            if st.form_submit_button(
                "Salvar Dados e Monitorar Validades", type="primary"
            ):
                t_val = tsb_val.isoformat() if tsb_val else ""
                a_val = tsa_val.isoformat() if tsa_val else ""

                with conectar() as conexao:
                    try:
                        conexao.execute(
                            "ALTER TABLE dados_brutos ADD COLUMN tsb_val TEXT"
                        )
                    except sqlite3.OperationalError:
                        pass
                    try:
                        conexao.execute(
                            "ALTER TABLE dados_brutos ADD COLUMN tsa_val TEXT"
                        )
                    except sqlite3.OperationalError:
                        pass

                    if modo == "✏️ Editar Linha" and id_sel is not None:
                        conexao.execute(
                            """
                            UPDATE dados_brutos
                            SET tsb=?, tsb_val=?, glicerina=?, tsa=?, tsa_val=?, criotubo=?, placa_de_petri=?, fluxo_laminar=?, ultrafreezer=?
                            WHERE id=?
                            """,
                            (
                                tsb,
                                t_val,
                                glicerina,
                                tsa,
                                a_val,
                                criotubo,
                                placa,
                                fluxo,
                                ultrafreezer,
                                id_sel,
                            ),
                        )
                    else:
                        conexao.execute(
                            """
                            INSERT INTO dados_brutos (tsb, tsb_val, glicerina, tsa, tsa_val, criotubo, placa_de_petri, fluxo_laminar, ultrafreezer)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                tsb,
                                t_val,
                                glicerina,
                                tsa,
                                a_val,
                                criotubo,
                                placa,
                                fluxo,
                                ultrafreezer,
                            ),
                        )
                st.success("Dados salvos e monitoramento ativado!")
                st.rerun()

# ============================================================
# INICIALIZAÇÃO DO SISTEMA E MENU LATERAL
# ============================================================

criar_banco()

st.sidebar.markdown(
    """
    <div class="logo-menu">
        🧫 Natalia
        <span>Monitoramento Microbiológico</span>
    </div>
    """,
    unsafe_allow_html=True,
)

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
st.sidebar.caption("Banco SQLite • dados persistentes")


============================================================


CABEÇALHO DO BIOBANK


============================================================

st.markdown(
"""

.block-container {
max-width: 100% !important;
padding-top: 1rem !important;
padding-right: 1rem !important;
padding-bottom: 1rem !important;
padding-left: 1rem !important;
}
[data-testid="stMainBlockContainer"] {
max-width: 100% !important;
}
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
url("githubusercontent.com");
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
[data-testid="stMetric"],
[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"],
[data-testid="stTable"] {
width: 100%;
}
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
BIOBANK - NATALIA
Gestão integrada de cepas, identificação e armazenamento.
""",
unsafe_allow_html=True,
)

# ============================================================
# ABERTURA DAS PÁGINAS
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
