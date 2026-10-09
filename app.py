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
    "ORIGIN": [
        "Environmental Monitoring",
        "Storage Tanks",
        "M.A",
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
    "resultado",
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
    for amostra in AMOSTRAS_INICIAIS:
        valores = [
            amostra.get(coluna, "")
            for coluna in COLUNAS_AMOSTRA
        ]

        conexao.execute(
            f"""
            INSERT OR IGNORE INTO amostras
            ({",".join(COLUNAS_AMOSTRA)})
            VALUES ({",".join("?" for _ in COLUNAS_AMOSTRA)})
            """,
            valores,
        )

    for identificacao in IDENTIFICACOES_INICIAIS:
        valores = [
            identificacao.get(coluna, "")
            for coluna in COLUNAS_IDENTIFICACAO
        ]

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

    st.markdown(
        """
        <div class="logo-login">
            <div class="logo-icone">🧫</div>
            <h1>Natalia</h1>
            <p>Monitoramento Microbiológico</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    esquerda, centro, direita = st.columns(
        [1.15, 1, 1.15]
    )

    with centro:
        st.markdown(
            '<div class="caixa-login">',
            unsafe_allow_html=True,
        )

        with st.form("formulario_login"):
            usuario = st.text_input(
                "Usuário",
                placeholder="Digite seu usuário",
            )

            senha = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha",
            )

            entrar = st.form_submit_button(
                "Entrar",
                type="primary",
                use_container_width=True,
            )

        st.caption(
            "Acesso restrito ao laboratório de microbiologia."
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

        if entrar:
            usuario_correto = hmac.compare_digest(
                usuario.strip(),
                USUARIO_PADRAO,
            )

            senha_correta = hmac.compare_digest(
                senha,
                SENHA_PADRAO,
            )

            if usuario_correto and senha_correta:
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
        f"Área: {registro['area'] or '—'} | "
        f"Ponto: "
        f"{registro['collection_point'] or '—'} | "
        f"Data: {registro['data'] or '—'}"
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

        with coluna2:
            company = st.text_input(
                "COMPANY",
                registro.get("company", ""),
            )

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

            # Entrada para upload dos relatórios e fotos
            arquivo_anexo = st.file_uploader(
                "ATTACH REPORT (Word, Excel, Foto ou PDF)",
                type=["doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "pdf"]
            )
            
            # 🆕 NOVA OPÇÃO: Caixinha para autorizar a remoção do arquivo atual
            remover_anexo = st.checkbox("❌ Remover anexo atual desta amostra")

        enviado = st.form_submit_button(
            "Salvar identificação",
            type="primary",
            use_container_width=True,
        )

    # 📥 EXTRAÇÃO E DOWNLOAD DOS BYTES REAIS DO BANCO DE DADOS
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
        # Lógica para definir se o arquivo será mantido, atualizado ou excluído completamente
        if remover_anexo:
            nome_relatorio = ""
            bytes_arquivo = None
            atualizar_dados_arquivo = True
        elif arquivo_anexo is not None:
            nome_relatorio = arquivo_anexo.name
            bytes_arquivo = arquivo_anexo.getvalue()
            atualizar_dados_arquivo = True
        else:
            # Mantém o arquivo antigo se nada foi mexido e a caixa de remoção está desmarcada
            nome_relatorio = registro.get("report", "")
            bytes_arquivo = None
            atualizar_dados_arquivo = False

        with conectar() as conexao:
            try:
                conexao.execute("ALTER TABLE identificacoes ADD COLUMN report_data BLOB")
                conexao.commit()
            except sqlite3.OperationalError:
                pass 

        # Mudança na QUERY SQL para aceitar a limpeza forçada de arquivos (NULL)
        sql_salvar = f"""
            INSERT INTO identificacoes (
                code, form, margin, pigment, gram_stain, catalase, koh, oxidase,
                outsourced_method, identification, report, company, end_date, report_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                form=excluded.form,
                gram_stain=excluded.gram_stain,
                identification=excluded.identification,
                company=excluded.company,
                end_date=excluded.end_date,
                report={"excluded.report" if atualizar_dados_arquivo else "identificacoes.report"},
                report_data={"excluded.report_data" if atualizar_dados_arquivo else "identificacoes.report_data"},
                atualizado_em=CURRENT_TIMESTAMP
        """

        valores = (
            code, form, registro.get("margin", ""), registro.get("pigment", ""), gram_stain,
            registro.get("catalase", ""), registro.get("koh", ""), registro.get("oxidase", ""),
            registro.get("outsourced_method", ""), identification, nome_relatorio, company,
            (end_date.isoformat() if end_date else ""), bytes_arquivo
        )

        with conectar() as conexao:
            conexao.execute(sql_salvar, valores)

        st.success(f"Identificação de {code} atualizada com sucesso!")
        st.rerun()

    st.subheader("Identificações cadastradas")

    colunas_visiveis = [
        "code", "area", "collection_point", "data", 
        "form", "gram_stain", "identification", "report", "company", "end_date"
    ]
    df_filtrado = df[[col for col in colunas_visiveis if col in df.columns]]

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
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

            # 🆕 NOVO: Lista suspensa de método terceirizado em inglês
            opcoes_metodo = ["", "NGS Sequencing", "Maldi TOF", "Others"]
            valor_salvo = registro.get("outsourced_method", "")
            
            # Traduz termos antigos em português caso existam no banco para não travar o índice
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
        if arquivo_anexo is not None:
            nome_relatorio = arquivo_anexo.name
            bytes_arquivo = arquivo_anexo.getvalue()
        else:
            nome_relatorio = ""
            bytes_arquivo = None

        with conectar() as conexao:
            try:
                conexao.execute("ALTER TABLE identificacoes ADD COLUMN report_data BLOB")
                conexao.commit()
            except sqlite3.OperationalError:
                pass
            try:
                conexao.execute("ALTER TABLE identificacoes ADD COLUMN start_date TEXT")
                conexao.commit()
            except sqlite3.OperationalError:
                pass

        sql_salvar = """
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
                report=excluded.report,
                report_data=excluded.report_data,
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

    # Inclusão da coluna outsourced_method na visualização do quadro inferior
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
            "outsourced_method": "OUTSOURCED METHOD", # Nome ajustado em inglês na tabela!
            "report": "ATTACH REPORT",
            "company": "COMPANY",
            "start_date": "START DATE",
            "end_date": "END DATE"
        }
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
        "Painel",
        "Registro",
        "Identificação",
        "Armazenamento",
        "Dados",
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

st.markdown(
    """
    <div class="cabecalho">
        <h1>
            BANCO DE BIOLOGICOS - NATALIA
        </h1>
        <p>
            Gestão integrada de cepas, identidade
            e armazenamento.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ABERTURA DAS PÁGINAS (ORQUESTRADOR DAS ABAS)
# ============================================================

if pagina == "Painel":
    pagina_dashboard()

elif pagina == "Registro":
    pagina_registro()

elif pagina == "Identificação":
    pagina_identificacao()

elif pagina == "Armazenamento":
    pagina_armazenamento()

elif pagina == "Dados":
    pagina_dados()

