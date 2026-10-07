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
    page_title="Monitoramento Microbiológico",
    page_icon="🧫",
    layout="wide",
)

DB_PATH = Path(__file__).parent / "monitoramento.db"

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: #f2f8f7;
        border-left: 5px solid #16857a;
        padding: 15px;
        border-radius: 8px;
    }

    .block-container {
        padding-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LISTAS DE VALIDAÇÃO
# Equivalente à aba Listas_Validacao
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
# DADOS INICIAIS MIGRADOS DA PLANILHA
# ============================================================

AMOSTRAS_INICIAIS = [
    {
        "code": "B4-001",
        "ponto": "",
        "origin": "Environmental Monitoring",
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
# BANCO DE DADOS SQLITE
# ============================================================

def conectar():
    conexao = sqlite3.connect(DB_PATH)
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
    colunas_amostras = list(AMOSTRAS_INICIAIS[0].keys())
    marcadores = ",".join("?" for _ in colunas_amostras)

    sql_amostras = f"""
        INSERT OR IGNORE INTO amostras
        ({",".join(colunas_amostras)})
        VALUES ({marcadores})
    """

    for registro in AMOSTRAS_INICIAIS:
        conexao.execute(
            sql_amostras,
            [registro[coluna] for coluna in colunas_amostras],
        )

    colunas_identificacao = list(IDENTIFICACOES_INICIAIS[0].keys())
    marcadores = ",".join("?" for _ in colunas_identificacao)

    sql_identificacao = f"""
        INSERT OR IGNORE INTO identificacoes
        ({",".join(colunas_identificacao)})
        VALUES ({marcadores})
    """

    for registro in IDENTIFICACOES_INICIAIS:
        conexao.execute(
            sql_identificacao,
            [registro[coluna] for coluna in colunas_identificacao],
        )


def consultar(sql, parametros=()):
    with conectar() as conexao:
        linhas = conexao.execute(sql, parametros).fetchall()
        return [dict(linha) for linha in linhas]


def salvar_amostra(registro):
    colunas = [
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

    marcadores = ",".join("?" for _ in colunas)

    atualizacoes = ",".join(
        f"{coluna}=excluded.{coluna}"
        for coluna in colunas
        if coluna != "code"
    )

    sql = f"""
        INSERT INTO amostras ({",".join(colunas)})
        VALUES ({marcadores})
        ON CONFLICT(code) DO UPDATE SET
            {atualizacoes},
            atualizado_em=CURRENT_TIMESTAMP
    """

    with conectar() as conexao:
        conexao.execute(
            sql,
            [registro.get(coluna, "") for coluna in colunas],
        )


def salvar_identificacao(registro):
    colunas = [
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

    marcadores = ",".join("?" for _ in colunas)

    atualizacoes = ",".join(
        f"{coluna}=excluded.{coluna}"
        for coluna in colunas
        if coluna != "code"
    )

    sql = f"""
        INSERT INTO identificacoes ({",".join(colunas)})
        VALUES ({marcadores})
        ON CONFLICT(code) DO UPDATE SET
            {atualizacoes},
            atualizado_em=CURRENT_TIMESTAMP
    """

    with conectar() as conexao:
        conexao.execute(
            sql,
            [registro.get(coluna, "") for coluna in colunas],
        )


def excluir_amostra(code):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM amostras WHERE code = ?",
            (code,),
        )


# ============================================================
# LEITURA DOS DADOS
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


def selecao(label, lista, valor_atual=""):
    opcoes = [""] + LISTAS[lista]

    if valor_atual and valor_atual not in opcoes:
        opcoes.append(valor_atual)

    indice = opcoes.index(valor_atual) if valor_atual in opcoes else 0

    return st.selectbox(
        label,
        opcoes,
        index=indice,
    )


# ============================================================
# DASHBOARD
# Equivalente à aba Dashboard
# ============================================================

def pagina_dashboard():
    st.title("🧫 Dashboard de Monitoramento Microbiológico")

    df = obter_amostras()

    if df.empty:
        st.info("Nenhuma amostra cadastrada.")
        return

    total_amostras = len(df)

    coletas_pendentes = (
        df["resultado_final"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    frequencias_mensais = (
        df["frequencia"] == "Mensal"
    ).sum()

    nao_conformes = (
        df["resultado_final"] == "Não Conforme"
    ).sum()

    coluna1, coluna2, coluna3, coluna4 = st.columns(4)

    coluna1.metric(
        "Total de amostras",
        total_amostras,
    )

    coluna2.metric(
        "Coletas pendentes",
        int(coletas_pendentes),
    )

    coluna3.metric(
        "Frequências mensais",
        int(frequencias_mensais),
    )

    coluna4.metric(
        "Não conformes",
        int(nao_conformes),
    )

    grafico1, grafico2 = st.columns(2)

    frequencias = (
        df["frequencia"]
        .replace("", "Não informado")
        .value_counts()
        .rename_axis("Frequência")
        .reset_index(name="Amostras")
    )

    figura_frequencias = px.bar(
        frequencias,
        x="Frequência",
        y="Amostras",
        color="Frequência",
        text_auto=True,
        title="Distribuição por frequência",
    )

    grafico1.plotly_chart(
        figura_frequencias,
        use_container_width=True,
    )

    status = (
        df["resultado_final"]
        .replace("", "Pendente")
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Amostras")
    )

    figura_status = px.pie(
        status,
        names="Status",
        values="Amostras",
        hole=0.45,
        title="Status das coletas",
    )

    grafico2.plotly_chart(
        figura_status,
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

        figura_tendencia = px.line(
            resumo_mensal,
            x="Mês",
            y="Amostras",
            markers=True,
            title="Amostras por mês",
        )

        st.plotly_chart(
            figura_tendencia,
            use_container_width=True,
        )

    st.subheader("Registros")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# REGISTRO
# Equivalente à aba Registro
# ============================================================

def pagina_registro():
    st.title("Registro de Monitoramento Microbiológico")

    df = obter_amostras()

    codigos = (
        df["code"].tolist()
        if not df.empty
        else []
    )

    acao = st.radio(
        "Ação",
        ["Novo registro", "Editar registro"],
        horizontal=True,
    )

    registro_atual = {}

    if acao == "Editar registro":
        if not codigos:
            st.info("Não há registros para editar.")
            return

        codigo_escolhido = st.selectbox(
            "Selecione o CODE",
            codigos,
        )

        registro_atual = (
            df[df["code"] == codigo_escolhido]
            .iloc[0]
            .fillna("")
            .to_dict()
        )

    with st.form("formulario_amostra"):
        coluna1, coluna2, coluna3 = st.columns(3)

        code = coluna1.text_input(
            "CODE *",
            registro_atual.get("code", ""),
            disabled=acao == "Editar registro",
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
            origin = selecao(
                "ORIGIN",
                "ORIGIN",
                registro_atual.get("origin", ""),
            )

            area = selecao(
                "AREA",
                "AREA",
                registro_atual.get("area", ""),
            )

        with coluna2:
            sample = selecao(
                "SAMPLE",
                "SAMPLE",
                registro_atual.get("sample", ""),
            )

            collection_point = selecao(
                "COLLECTION POINT",
                "COLLECTION POINT",
                registro_atual.get("collection_point", ""),
            )

        with coluna3:
            sampling = selecao(
                "SAMPLING",
                "SAMPLING",
                registro_atual.get("sampling", ""),
            )

            method = selecao(
                "METHOD",
                "METHOD",
                registro_atual.get("method", ""),
            )

        coluna1, coluna2, coluna3 = st.columns(3)

        with coluna1:
            frequencia = selecao(
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
            resultado_final = selecao(
                "RESULTADO FINAL",
                "RESULTADO_FINAL",
                registro_atual.get("resultado_final", ""),
            )

        enviado = st.form_submit_button(
            "Salvar registro",
            type="primary",
            use_container_width=True,
        )

    if enviado:
        if not code.strip():
            st.error("O campo CODE é obrigatório.")

        elif acao == "Novo registro" and code.strip() in codigos:
            st.error("Já existe um registro com esse CODE.")

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
                    "data": data.isoformat() if data else "",
                    "resultado_final": resultado_final,
                }
            )

            st.success(f"Registro {code} salvo.")
            st.rerun()

    if codigos:
        with st.expander("Excluir registro"):
            codigo_exclusao = st.selectbox(
                "CODE para excluir",
                codigos,
                key="codigo_exclusao",
            )

            confirmar = st.checkbox(
                "Confirmo a exclusão da amostra e da identificação"
            )

            if st.button(
                "Excluir registro",
                disabled=not confirmar,
            ):
                excluir_amostra(codigo_exclusao)
                st.success("Registro excluído.")
                st.rerun()

    st.subheader("Registros cadastrados")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# IDENTIFICAÇÃO
# Equivalente à aba Identification
# ============================================================

def pagina_identificacao():
    st.title("Identificação Microbiológica")

    df = obter_identificacoes()

    if df.empty:
        st.info("Cadastre uma amostra antes da identificação.")
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
        f"Ponto: {registro['collection_point'] or '—'} | "
        f"Data: {registro['data'] or '—'}"
    )

    with st.form("formulario_identificacao"):
        coluna1, coluna2, coluna3 = st.columns(3)

        with coluna1:
            form = selecao(
                "FORM",
                "FORM",
                registro.get("form", ""),
            )

            margin = selecao(
                "MARGIN",
                "MARGIN",
                registro.get("margin", ""),
            )

            pigment = st.text_input(
                "PIGMENT",
                registro.get("pigment", ""),
            )

        with coluna2:
            gram_stain = selecao(
                "GRAM STAIN",
                "AFFIRMATION",
                registro.get("gram_stain", ""),
            )

            catalase = selecao(
                "CATALASE",
                "AFFIRMATION",
                registro.get("catalase", ""),
            )

            koh = selecao(
                "KOH",
                "AFFIRMATION",
                registro.get("koh", ""),
            )

        with coluna3:
            oxidase = selecao(
                "OXIDASE",
                "AFFIRMATION",
                registro.get("oxidase", ""),
            )

            outsourced_method = st.text_input(
                "OUTSOURCED METHOD",
                registro.get("outsourced_method", ""),
            )

            identification = st.text_input(
                "IDENTIFICATION",
                registro.get("identification", ""),
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
                "end_date": end_date.isoformat() if end_date else "",
            }
        )

        st.success(f"Identificação de {code} salva.")
        st.rerun()

    st.subheader("Identificações cadastradas")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ARMAZENAMENTO
# Equivalente à aba Storage
# ============================================================

def pagina_armazenamento():
    st.title("Armazenamento de Isolados Identificados")

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
        st.info("Ainda não existem identificações preenchidas.")
        return

    coluna1, coluna2 = st.columns([1, 2])

    coluna1.dataframe(
        resumo,
        use_container_width=True,
        hide_index=True,
    )

    figura = px.bar(
        resumo,
        x="OCORRÊNCIAS",
        y="IDENTIFICAÇÃO",
        orientation="h",
        text_auto=True,
        title="Ocorrências por identificação",
    )

    coluna2.plotly_chart(
        figura,
        use_container_width=True,
    )


# ============================================================
# EXPORTAÇÃO PARA EXCEL
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
    ]

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

                largura = min(maior_tamanho + 2, 40)

                planilha.column_dimensions[
                    coluna[0].column_letter
                ].width = largura

    return arquivo.getvalue()


# ============================================================
# IMPORTAÇÃO DO EXCEL
# ============================================================

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
        str(coluna).strip().lower().replace(" ", "_")
        for coluna in registro.columns
    ]

    identificacao.columns = [
        str(coluna).strip().lower().replace(" ", "_")
        for coluna in identificacao.columns
    ]

    with conectar() as conexao:
        conexao.execute("DELETE FROM identificacoes")
        conexao.execute("DELETE FROM amostras")

    for _, linha in registro.fillna("").iterrows():
        registro_dict = linha.to_dict()

        if registro_dict.get("code"):
            salvar_amostra(registro_dict)

    for _, linha in identificacao.fillna("").iterrows():
        registro_dict = linha.to_dict()

        if registro_dict.get("code"):
            salvar_identificacao(registro_dict)


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
        "A importação substitui os registros atuais. "
        "Faça uma exportação antes."
    )

    arquivo = st.file_uploader(
        "Selecione o arquivo",
        type=["xlsx"],
    )

    confirmar = st.checkbox(
        "Confirmo a substituição dos dados"
    )

    if (
        arquivo is not None
        and confirmar
        and st.button("Importar dados", type="primary")
    ):
        try:
            importar_excel(arquivo)
            st.success("Dados importados.")
            st.rerun()

        except Exception as erro:
            st.error(f"Erro durante a importação: {erro}")


# ============================================================
# EXECUÇÃO
# ============================================================

criar_banco()

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

st.sidebar.caption(
    "Banco de dados SQLite • dados persistentes"
)

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