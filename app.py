import sqlite3
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Natalia - Monitoramento Microbiológico",
    page_icon="🧫",
    layout="wide",
)

CAMINHO_BANCO = Path(__file__).parent / "monitoramento.db"


# ============================================================
# INTERFACE VISUAL
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --navy: #12343b;
        --teal: #13877c;
        --mint: #eaf5f2;
    }

    .stApp {
        background: linear-gradient(
            135deg,
            #f8fcfb,
            #edf6f4
        );
    }

    .block-container {
        padding-top: 1.4rem;
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
        background: white;
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
        background: #13877c;
        color: white;
        font-weight: 700;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #0f6f67;
        color: white;
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
        margin: 5px 0 0;
        color: #d8efeb;
    }

    .logo-menu {
        text-align: center;
        padding: 12px 0 20px;
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
    "ORIGIN": [
        "Environmental Monitoring",
        "Storage Tanks",
        "Amostra",
        "Processes",
    ],
    "AREA": [
        "Laboratory",
        "Dissolution",
        "Line 2",
        "Line 3",
        "Line 4",
        "Line 5",
        "SBTA 1",
        "SBTA 2",
        "Autoclave",
    ],
    "SAMPLE": [
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
        "Punctiform",
        "Circular",
        "Filamentous",
        "Irregular",
        "Rhizoid",
        "Fusiform",
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
    "RESULTADO_FINAL": [
        "Conforme",
        "Não Conforme",
    ],
    "FREQUÊNCIA": [
        "Mensal",
        "Semanal",
    ],
}


# ============================================================
# DADOS INICIAIS
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
        "analista": "Natalia",
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
        "form": "Rhizoid",
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
# COLUNAS DO BANCO
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


# ============================================================
# BANCO SQLITE
# ============================================================

def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_banco():
    with conectar() as conexao:
        conexao.executescript(
            """
            CREATE TABLE IF NOT EXISTS amostras (
                code TEXT PRIMARY KEY,
                ponto TEXT,
                origin TEXT,
                area TEXT,
                sample TEXT,
                collection_point TEXT,
                sampling TEXT,
                method TEXT,
                frequencia TEXT,
                analista TEXT,
                data TEXT,
                resultado_final TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS identificacoes (
                code TEXT PRIMARY KEY,
                form TEXT,
                margin TEXT,
                pigment TEXT,
                gram_stain TEXT,
                catalase TEXT,
                koh TEXT,
                oxidase TEXT,
                outsourced_method TEXT,
                identification TEXT,
                report TEXT,
                company TEXT,
                end_date TEXT,
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (code)
                    REFERENCES amostras(code)
                    ON DELETE CASCADE
            );
            """
        )

        quantidade = conexao.execute(
            "SELECT COUNT(*) FROM amostras"
        ).fetchone()[0]

        if quantidade == 0:
            inserir_dados_iniciais(conexao)


def inserir_dados_iniciais(conexao):
    for registro in AMOSTRAS_INICIAIS:
        marcadores = ",".join(
            "?" for _ in COLUNAS_AMOSTRA
        )

        conexao.execute(
            f"""
            INSERT OR IGNORE INTO amostras
            ({",".join(COLUNAS_AMOSTRA)})
            VALUES ({marcadores})
            """,
            [
                registro.get(coluna, "")
                for coluna in COLUNAS_AMOSTRA
            ],
        )

    for registro in IDENTIFICACOES_INICIAIS:
        marcadores = ",".join(
            "?" for _ in COLUNAS_IDENTIFICACAO
        )

        conexao.execute(
            f"""
            INSERT OR IGNORE INTO identificacoes
            ({",".join(COLUNAS_IDENTIFICACAO)})
            VALUES ({marcadores})
            """,
            [
                registro.get(coluna, "")
                for coluna in COLUNAS_IDENTIFICACAO
            ],
        )


def consultar(sql, parametros=()):
    with conectar() as conexao:
        linhas = conexao.execute(
            sql,
            parametros,
        ).fetchall()

        return [dict(linha) for linha in linhas]


def salvar_amostra(registro):
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

    with conectar() as conexao:
        conexao.execute(
            sql,
            [
                registro.get(coluna, "")
                for coluna in COLUNAS_AMOSTRA
            ],
        )


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

    with conectar() as conexao:
        conexao.execute(
            sql,
            [
                registro.get(coluna, "")
                for coluna in COLUNAS_IDENTIFICACAO
            ],
        )


def excluir_amostra(code):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM amostras WHERE code = ?",
            (code,),
        )


def substituir_dados(amostras, identificacoes):
    with conectar() as conexao:
        conexao.execute("DELETE FROM identificacoes")
        conexao.execute("DELETE FROM amostras")

    for registro in amostras:
        salvar_amostra(registro)

    for registro in identificacoes:
        salvar_identificacao(registro)


# ============================================================
# CONSULTAS
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
    dados = consultar(
        """
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
            i.end_date
        FROM amostras a

        LEFT JOIN identificacoes i
            ON i.code = a.code

        ORDER BY a.code
        """
    )

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
    st.title("Dashboard")

    df = obter_amostras()

    if df.empty:
        st.info("Cadastre a primeira amostra.")
        return

    total = len(df)

    pendentes = (
        df["resultado_final"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    mensais = (
        df["frequencia"] == "Mensal"
    ).sum()

    nao_conformes = (
        df["resultado_final"] == "Não Conforme"
    ).sum()

    coluna1, coluna2, coluna3, coluna4 = st.columns(4)

    coluna1.metric(
        "Total de amostras",
        total,
    )

    coluna2.metric(
        "Coletas pendentes",
        int(pendentes),
    )

    coluna3.metric(
        "Frequências mensais",
        int(mensais),
    )

    coluna4.metric(
        "Não conformes",
        int(nao_conformes),
    )

    esquerda, direita = st.columns(2)

    frequencias = (
        df["frequencia"]
        .replace("", "Não informado")
        .value_counts()
        .rename_axis("Frequência")
        .reset_index(name="Amostras")
    )

    grafico_frequencia = px.bar(
        frequencias,
        x="Frequência",
        y="Amostras",
        color="Frequência",
        text_auto=True,
        title="Distribuição por frequência",
    )

    esquerda.plotly_chart(
        grafico_frequencia,
        use_container_width=True,
    )

    status = (
        df["resultado_final"]
        .replace("", "Pendente")
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Amostras")
    )

    grafico_status = px.pie(
        status,
        names="Status",
        values="Amostras",
        hole=0.45,
        title="Status das coletas",
    )

    direita.plotly_chart(
        grafico_status,
        use_container_width=True,
    )

    tendencia = df.copy()

    tendencia["data"] = pd.to_datetime(
        tendencia["data"],
        errors="coerce",
    )

    tendencia = tendencia.dropna(subset=["data"])

    if not tendencia.empty:
        tendencia["Mês"] = (
            tendencia["data"]
            .dt.to_period("M")
            .astype(str)
        )

        resumo_mensal = (
            tendencia.groupby("Mês")
            .size()
            .reset_index(name="Amostras")
        )

        grafico_tendencia = px.line(
            resumo_mensal,
            x="Mês",
            y="Amostras",
            markers=True,
            title="Amostras por mês",
        )

        st.plotly_chart(
            grafico_tendencia,
            use_container_width=True,
        )

    st.subheader("Registros recentes")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# REGISTRO
# ============================================================

def pagina_registro():
    st.title("Registro de Monitoramento")

    df = obter_amostras()

    codigos = (
        df["code"].tolist()
        if not df.empty
        else []
    )

    modo = st.radio(
        "Ação",
        [
            "Novo registro",
            "Editar registro",
        ],
        horizontal=True,
    )

    registro_atual = {}

    if modo == "Editar registro":
        if not codigos:
            st.info("Não existem registros para editar.")
            return

        codigo_selecionado = st.selectbox(
            "Selecione o CODE",
            codigos,
        )

        registro_atual = (
            df[df["code"] == codigo_selecionado]
            .iloc[0]
            .fillna("")
            .to_dict()
        )

    with st.form("formulario_amostra"):
        coluna1, coluna2, coluna3 = st.columns(3)

        code = coluna1.text_input(
            "CODE *",
            registro_atual.get("code", ""),
            disabled=modo == "Editar registro",
        )

        ponto = coluna2.text_input(
            "PONTO",
            registro_atual.get("ponto", ""),
        )

        analista = coluna3.text_input(
            "ANALISTA",
            registro_atual.get("analista", ""),
        )

        coluna1, coluna2, coluna3 = st.columns(3)

        with coluna1:
            origin = campo_selecao(
                "ORIGIN",
                "ORIGIN",
                registro_atual.get("origin", ""),
            )

            area = campo_selecao(
                "AREA",
                "AREA",
                registro_atual.get("area", ""),
            )

        with coluna2:
            sample = campo_selecao(
                "SAMPLE",
                "SAMPLE",
                registro_atual.get("sample", ""),
            )

            collection_point = campo_selecao(
                "COLLECTION POINT",
                "COLLECTION POINT",
                registro_atual.get(
                    "collection_point",
                    "",
                ),
            )

        with coluna3:
            sampling = campo_selecao(
                "SAMPLING",
                "SAMPLING",
                registro_atual.get("sampling", ""),
            )

            method = campo_selecao(
                "METHOD",
                "METHOD",
                registro_atual.get("method", ""),
            )

        coluna1, coluna2, coluna3 = st.columns(3)

        with coluna1:
            frequencia = campo_selecao(
                "FREQUÊNCIA",
                "FREQUÊNCIA",
                registro_atual.get("frequencia", ""),
            )

        with coluna2:
            data_atual = pd.to_datetime(
                registro_atual.get("data", ""),
                errors="coerce",
            )

            data = st.date_input(
                "DATA",
                value=(
                    None
                    if pd.isna(data_atual)
                    else data_atual.date()
                ),
                format="DD/MM/YYYY",
            )

        with coluna3:
            resultado_final = campo_selecao(
                "RESULTADO FINAL",
                "RESULTADO_FINAL",
                registro_atual.get(
                    "resultado_final",
                    "",
                ),
            )

        enviado = st.form_submit_button(
            "Salvar registro",
            type="primary",
            use_container_width=True,
        )

    if enviado:
        if not code.strip():
            st.error("O campo CODE é obrigatório.")

        elif (
            modo == "Novo registro"
            and code.strip() in codigos
        ):
            st.error("Este CODE já está cadastrado.")

        else:
            salvar_amostra(
                {
                    "code": code.strip(),
                    "ponto": ponto,
                    "origin": origin,
                    "area": area,
                    "sample": sample,
                    "collection_point": collection_point,
                    "sampling": sampling,
                    "method": method,
                    "frequencia": frequencia,
                    "analista": analista,
                    "data": (
                        data.isoformat()
                        if data
                        else ""
                    ),
                    "resultado_final": resultado_final,
                }
            )

            st.success(
                f"Registro {code} salvo com sucesso."
            )

            st.rerun()

    if codigos:
        with st.expander("Excluir registro"):
            codigo_exclusao = st.selectbox(
                "CODE para excluir",
                codigos,
                key="codigo_exclusao",
            )

            confirmar = st.checkbox(
                "Confirmo a exclusão da amostra "
                "e da identificação vinculada"
            )

            if st.button(
                "Excluir",
                disabled=not confirmar,
            ):
                excluir_amostra(codigo_exclusao)
                st.success("Registro excluído.")
                st.rerun()

    st.subheader("Amostras cadastradas")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# IDENTIFICAÇÃO
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
        f"Área: {registro['area'] or '—'} | "
        f"Ponto: "
        f"{registro['collection_point'] or '—'} | "
        f"Data: {registro['data'] or '—'}"
    )

    with st.form("formulario_identificacao"):
        coluna1, coluna2, coluna3 = st.columns(3)

        with coluna1:
            form = campo_selecao(
                "FORM",
                "FORM",
                registro.get("form", ""),
            )

            margin = campo_selecao(
                "MARGIN",
                "MARGIN",
                registro.get("margin", ""),
            )

            pigment = st.text_input(
                "PIGMENT",
                registro.get("pigment", ""),
            )

        with coluna2:
            gram_stain = campo_selecao(
                "GRAM STAIN",
                "AFFIRMATION",
                registro.get("gram_stain", ""),
            )

            catalase = campo_selecao(
                "CATALASE",
                "AFFIRMATION",
                registro.get("catalase", ""),
            )

            koh = campo_selecao(
                "KOH",
                "AFFIRMATION",
                registro.get("koh", ""),
            )

        with coluna3:
            oxidase = campo_selecao(
                "OXIDASE",
                "AFFIRMATION",
                registro.get("oxidase", ""),
            )

            outsourced_method = st.text_input(
                "OUTSOURCED METHOD",
                registro.get(
                    "outsourced_method",
                    "",
                ),
            )

            identification = st.text_input(
                "IDENTIFICATION",
                registro.get(
                    "identification",
                    "",
                ),
            )

        coluna1, coluna2, coluna3 = st.columns(3)

        report = coluna1.text_input(
            "REPORT",
            registro.get("report", ""),
        )

        company = coluna2.text_input(
            "COMPANY",
            registro.get("company", ""),
        )

        data_final_atual = pd.to_datetime(
            registro.get("end_date", ""),
            errors="coerce",
        )

        end_date = coluna3.date_input(
            "END DATE",
            value=(
                None
                if pd.isna(data_final_atual)
                else data_final_atual.date()
            ),
            format="DD/MM/YYYY",
        )

        enviado = st.form_submit_button(
            "Salvar identificação",
            type="primary",
            use_container_width=True,
        )

    if enviado:
        salvar_identificacao(
            {
                "code": code,
                "form": form,
                "margin": margin,
                "pigment": pigment,
                "gram_stain": gram_stain,
                "catalase": catalase,
                "koh": koh,
                "oxidase": oxidase,
                "outsourced_method": outsourced_method,
                "identification": identification,
                "report": report,
                "company": company,
                "end_date": (
                    end_date.isoformat()
                    if end_date
                    else ""
                ),
            }
        )

        st.success(
            f"Identificação de {code} salva."
        )

        st.rerun()

    st.subheader("Identificações cadastradas")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ARMAZENAMENTO
# ============================================================

def pagina_armazenamento():
    st.title(
        "Armazenamento de Isolados Identificados"
    )

    df = obter_identificacoes()

    if df.empty:
        st.info("Nenhuma amostra cadastrada.")
        return

    armazenamento = df[
        [
            "code",
            "gram_stain",
            "identification",
        ]
    ].copy()

    armazenamento.columns = [
        "CODE",
        "GRAM STAIN",
        "IDENTIFICATION",
    ]

    st.dataframe(
        armazenamento,
        use_container_width=True,
        hide_index=True,
    )

    resumo = (
        armazenamento["IDENTIFICATION"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .rename_axis("IDENTIFICAÇÃO")
        .reset_index(name="OCORRÊNCIAS")
    )

    st.subheader("Resumo de contaminantes")

    if resumo.empty:
        st.info(
            "Ainda não existem identificações preenchidas."
        )
        return

    coluna1, coluna2 = st.columns([1, 2])

    coluna1.dataframe(
        resumo,
        use_container_width=True,
        hide_index=True,
    )

    grafico = px.bar(
        resumo,
        x="OCORRÊNCIAS",
        y="IDENTIFICAÇÃO",
        orientation="h",
        text_auto=True,
        title="Ocorrências por identificação",
    )

    coluna2.plotly_chart(
        grafico,
        use_container_width=True,
    )


# ============================================================
# EXPORTAÇÃO
# ============================================================

def gerar_excel():
    amostras = obter_amostras()
    identificacoes = obter_identificacoes()

    armazenamento = identificacoes[
        [
            "code",
            "gram_stain",
            "identification",
        ]
    ].copy()

    arquivo = BytesIO()

    with pd.ExcelWriter(
        arquivo,
        engine="openpyxl",
    ) as writer:
        amostras.to_excel(
            writer,
            sheet_name="Registro",
            index=False,
        )

        identificacoes.to_excel(
            writer,
            sheet_name="Identification",
            index=False,
        )

        armazenamento.to_excel(
            writer,
            sheet_name="Storage",
            index=False,
        )

        for planilha in writer.book.worksheets:
            planilha.freeze_panes = "A2"
            planilha.auto_filter.ref = planilha.dimensions

            for coluna in planilha.columns:
                maior_tamanho = max(
                    len(str(celula.value or ""))
                    for celula in coluna
                )

                planilha.column_dimensions[
                    coluna[0].column_letter
                ].width = min(
                    maior_tamanho + 2,
                    38,
                )

    return arquivo.getvalue()


# ============================================================
# IMPORTAÇÃO
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
        "RESULTADO FINAL": "resultado_final",
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
        registro["code"]
        .astype(str)
        .str.strip()
        .ne("")
    ]

    identificacao = identificacao[
        identificacao["code"]
        .astype(str)
        .str.strip()
        .ne("")
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


def pagina_dados():
    st.title("Importação e Exportação")

    st.download_button(
        label="Baixar dados em Excel",
        data=gerar_excel(),
        file_name="monitoramento_microbiologico.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

    st.divider()

    st.subheader("Importar arquivo Excel")

    st.warning(
        "A importação substituirá os registros atuais. "
        "Exporte um backup antes de continuar."
    )

    arquivo = st.file_uploader(
        "Selecione o arquivo Excel",
        type=["xlsx"],
    )

    confirmar = st.checkbox(
        "Confirmo a substituição dos dados atuais"
    )

    if (
        arquivo is not None
        and confirmar
        and st.button(
            "Importar dados",
            type="primary",
        )
    ):
        try:
            importar_excel(arquivo)

            st.success(
                "Dados importados com sucesso."
            )

            st.rerun()

        except Exception as erro:
            st.error(
                f"Erro durante a importação: {erro}"
            )


# ============================================================
# INICIALIZAÇÃO
# ============================================================

criar_banco()


# ============================================================
# MENU LATERAL
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

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Dashboard",
        "Registro",
        "Identificação",
        "Armazenamento",
        "Dados",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    "Banco SQLite • dados persistentes"
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="cabecalho">
        <h1>
            Natalia - Monitoramento Microbiológico
        </h1>
        <p>
            Gestão integrada de amostras, identificação
            e armazenamento de isolados.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVEGAÇÃO
# ============================================================

if pagina == "Dashboard":
    pagina_dashboard()

elif pagina == "Registro":
    pagina_registro()

elif pagina == "Identificação":
    pagina_identificacao()

elif pagina == "Armazenamento":
    pagina_armazenamento()

elif pagina == "Dados":
    pagina_dados()