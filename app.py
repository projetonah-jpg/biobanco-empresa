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
        /* 💜 NOVO GRADIENTE ROXO SUAVE E PROFISSIONAL */
        background: linear-gradient(
            120deg,
            #4a3f75,
            #6c5b9b
        );
        color: white;
        border-radius: 18px;
        margin-bottom: 20px;
        box-shadow: 0 12px 30px rgba(74, 63, 117, 0.14);
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
    "ORIGIN": ["Environmental Monitoring", "Storage Tanks", "Processes"],
    "AREA": ["Laboratory", "Dissolution", "1940", "1920", "1910", "1710", "1720", "Line 2", "Line 3", "Line 4", "Line 5", "SBTA", "SBTA 1", "SBTA 2", "Autoclave"],
    "SAMPLE": ["Inoculation Room Anteroom", "Inoculation Room", "Flow Room", "Dissolution", "Preparation", "Weighing", "Team Member", "Sterile"],
    "COLLECTION POINT": ["Laminar Flow FLA001", "Laminar Flow FLA002", "Laminar Flow FLA003", "Laminar Flow FLA004", "Laminar Flow FLA005", "Laminar Flow FLA006", "Dissolution Room", "Inoculation Room", "Inoculation Anteroom", "Molasses", "Blend", "VHP", "CIP", "Flow Room", "Dissolution Tank", "Pump Outlet Filter", "Weighing Bench", "Becker", "Bucket", "Spatula", "Floor", "Wall", "Hands (glove)", "Lab Coat", "Drain Dissolution", "Weighing Drain", "Hand-Washing Sink", "Feedstock", "Aseptic Salts", "Collection Point"],
    "SAMPLING": ["Swab", "Passive", "MAS-100", "Palating"],
    "METHOD": ["Petrifilm AC", "Petrifilm EB", "TSAC", "YPD", "Petrifilm YM"],
    "FORM": ["Cocos", "Bacilos", "Strepto", "Staphylo", "Cocobacilos", "Vibrio"],
    "AFFIRMATION": ["Positive", "Negative", "N/A"],
    "MARGIN": ["Round", "Wavy", "Lobulated", "Filamentous", "Spiral"],
    "RESULTADO": ["Conforme", "Não Conforme"],
    "FREQUÊNCIA": ["Semanal", "Mensal"],
}

COLUNAS_AMOSTRA = ["code", "ponto", "origin", "area", "sample", "collection_point", "sampling", "method", "frequencia", "analista", "data", "resultado_final"]
COLUNAS_IDENTIFICACAO = ["code", "form", "margin", "pigment", "gram_stain", "catalase", "koh", "oxidase", "outsourced_method", "identification", "report", "company", "end_date"]


# ============================================================
# BANCO DE DADOS E CONEXÕES
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
                FOREIGN KEY (code) REFERENCES amostras(code) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS dados_brutos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tsb TEXT,
                glicerina TEXT,
                tsa TEXT,
                criotubo TEXT,
                placa_de_petri TEXT,
                fluxo_laminar TEXT,
                ultrafreezer TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def consultar(sql, parametros=()):
    with conectar() as conexao:
        linhas = conexao.execute(sql, parametros).fetchall()
        return [dict(linha) for linha in linhas]


def salvar_amostra(registro):
    marcadores = ",".join("?" for _ in COLUNAS_AMOSTRA)
    atualizacoes = ",".join(f"{coluna}=excluded.{coluna}" for coluna in COLUNAS_AMOSTRA if coluna != "code")
    sql = f"INSERT INTO amostras ({','.join(COLUNAS_AMOSTRA)}) VALUES ({marcadores}) ON CONFLICT(code) DO UPDATE SET {atualizacoes}, atualizado_em=CURRENT_TIMESTAMP"
    valores = [registro.get(coluna, "") for coluna in COLUNAS_AMOSTRA]
    with conectar() as conexao:
        conexao.execute(sql, valores)


def salvar_identificacao(registro):
    marcadores = ",".join("?" for _ in COLUNAS_IDENTIFICACAO)
    atualizacoes = ",".join(f"{coluna}=excluded.{coluna}" for coluna in COLUNAS_IDENTIFICACAO if coluna != "code")
    sql = f"INSERT INTO identificacoes ({','.join(COLUNAS_IDENTIFICACAO)}) VALUES ({marcadores}) ON CONFLICT(code) DO UPDATE SET {atualizacoes}, atualizado_em=CURRENT_TIMESTAMP"
    valores = [registro.get(coluna, "") for coluna in COLUNAS_IDENTIFICACAO]
    with conectar() as conexao:
        conexao.execute(sql, valores)


def excluir_amostra(code):
    with conectar() as conexao:
        conexao.execute("DELETE FROM amostras WHERE code = ?", (code,))


def substituir_dados(amostras, identificacoes):
    with conectar() as conexao:
        conexao.execute("DELETE FROM identificacoes")
        conexao.execute("DELETE FROM amostras")
    for amostra in amostras:
        salvar_amostra(amostra)
    for identificacao in identificacoes:
        salvar_identificacao(identificacao)


def obter_amostras():
    return pd.DataFrame(consultar("SELECT code, ponto, origin, area, sample, collection_point, sampling, method, frequencia, analista, data, resultado_final FROM amostras ORDER BY data DESC, code"))


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

=========================================================================================================


LOGIN


=========================================================================================================

defmor_login():
if st.session_state.get("autenticado"):
retorno True
st.markdown('🧫NataliaMonitoramento Microbiológico', unsafe_allow_html=True)
_, centro, _ = st.columns([1.15, 1,15])
com centro:
st.markdown('', unsafe_allow_html=True) (em inglês)
com st.form("formulario_login"):
usuário = st.text_input("Usuário", placeholder="Digite usuário")
senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
int = st.form_submit_button("Entrar", type="primary", use_container_width=True) (em inglês)
st.caption("Acstão ao laboratório de microbiologia.")
st.markdown("", unsafe_allow_html=True)
se entrar:
se hmac.compare_digest(usaurio.strip(), USUARIO_PADRAO) e hmac.compare_digest(senha, SENHA_PADRAO):
st.session_state.autenticado = Verdadeiro
st.session_state.usario = USUARIO_PADRAO
st.rerun()
mais:
st.error("Usuário ou senha inválidos.")
retorno Falso

=========================================================================================================


PAINEL


=========================================================================================================

def pagina_dashboard():
st.title("Dashboard")
df_amostras =_amostras()
df_identificacoes =_identificacoes()
se df_amostras.empty:
st.info("Sem dados cadastrados.")
retorno
total_amostras = len(df_amostras)
codigos_identificados = []
se não df_identificacoes.empty e "identificação" em df_identificacoes.columns:
df_validas = df_identificacoes[df_identificacoes["identification"].fillna("").str.strip().ne("")]
codigos_identificados = df_validas["code"].tolist()
totalifique_idents = len(codigos_identificados)
total_nao_idents = max(0, total_amostras - total_identificadas)
pctificada_idents = (total_identificados / total_amostras * 100) if total_amostras > 0 else 0
pct_nao_identificadas = (total_nao_identificadas / total_amostras * 100) if total_amostras > 0 else 0
se "filtro_clique" não em st.session_state:
st.session_state.filtro_clique = "Todos"
se st.session_state.filtro_clique ! = "Todos":
if st.button("🔄 Todos Gráfico oss / Resetar Filtro"):
st.session_state.filtro_clique = "Todos"
st.rerun()
col1, col2, col3 = st.columns(3)
com col1:
st.metric(label="Total de amostras", value=f"{total_amostras} un")
if st.button("👁️ Ver", todas key="btn_todas", use_container_width=True):
st.session_state.filtro_clique = "Todos"
st.rerun()
com col2:
st.metric(label="Amostras Identificadas", value=f"{total_identificadas} un", delta=f"{pct_identificadas:.1f}% do total", delta_color="off")
if st.button("🔍 Ver", key="btn_iden", use_container_width=True):
st.session_state.filtro_clique = "Identificadas"
st.rerun()
com col3:
st.metric(label="Aguardando Identificação", value=f"{total_nao_identificadas} un", delta=f"{pct_nao_ificadaidents:.1f}% do total", delta_color="off")
if st.button("🔎 Ver não", key="btn_nao_iden", use_container_width=True):
st.session_state.filtro_clique = "Nao_Identificadas"
st.rerun()
st.markdown("
", insafe_allow_html=True)Tradução
config_colunas = {"code": "CODE", "ponto": "OBSERVATION", "origin": "ORIGIN", "area": "AREA", "sample": "SAMPLE", "collection_point": "COLLECTION POINT", "sampling": "SAMPLING", "method": "METHOD", "REQUE", "freque"
if st.session_state.filtro_clique == "Identificadas":
st.subheader("📋 Amostras Identificadas")
st.dataframe(df_amostras[df_amostras["code"].isin(codigos_identificados)], use_container_width=True, hide_index=True, column_config=config_colunas)
elif st.session_state.filtro_clique == "Nao_Identificadas":
st.subheader("📋 Amostras Aguardando Identificação")
st.dataframe(df_amostras[~df_amostras["code"].isin(codigos_identificados)], use_container_width=True, hide_index=True, column_config=config_colunas)
mais:
esquerda, direita = st.columns(2)
com o esquerda:
se não df_identificacoes.empty e "identificação" em df_identificacoes.columns:
resumo_micro = df_identificacoes["identification"].replace("", pd.NA).dropna().value_counts().rename_axis("IDENTIFICAÇÃO").reset_index(name="OCORRÊNCIAS")
se não resumo_micro.empty:
st.plotly_chart(px.bar(resumo_micro, x="OCORRÊNCIAS", y="IDENTIFICAÇÃO", guidance="h", text_auto=True, title"=Os por", color_discrete_sequence=["#13877c"]), use_container_width=True)
mais:
st.info(Número" microrgan identificadoismo.") ainda
mais:
st.info("Aguardando de registros.")
com os seguintes:
grafico_pizza = px.pie(df_amostras, names="resultado_final", title="Status das Coletas (Conformidade)", hole=0.45, color_discrete_sequence=["#13877c", "#12343b"])
grafico_pizza.update_traces(textinfo="percent+label", textposition="inside", insintetextorientation="radial")
st.plotly_chart(grafico_pizza, use_container_width=True) (em inglês)
st.markdown("
", insafe_allow_html=True)Tradução
st.subheader("📊 Histórico de Tendência Microbiológica")
dados_tendencia =("SELECT a.origin, a.data, i.identification FROM samples a INNER JOIN identificacoes i ON a.code = i.code ONDE a identificação i.identIFICA NÃO É NULA E i.identification! = ''"")
se dados_tendencia:
df_t = pd.DataFrame(dados_tendencia)
df_t["datetime"] = pd.to_datetime(df_t["data"], errors="coerce")
df_t = df_t.dropna(subset=["datetime"]) (em inglês)
se não df_t.empty:
lista_origens = ["Todas as Origens"] + sorted(df_t["origin"].unique().tolist()))
origem_selecionada = st.selectbox("Filtrar gráfico por: origem", lista,_origens)
if origem_selecionada ! = "Todas como Orígenes":
df_t = df_t[df_t["origin"] == origem_sele]
df_t["mes_num"] = df_t["datetime"].dt.month
nomes_meses = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
df_t["Mês"] = df_t["mes_num"].map(nomes_meses)
df_agrupado = df_t.groupby(["mes_num", "Mês", "identification"]).size().reset_index(name="Colônias").sort_values(by="mes_num")
se não df_agrupado.empty:
grafico_linha = px.line(df_agrupado, x="Mês", y="Colônias", color="identification", marcadores=True, title=f"Bacterial Identification by Genus — {origem_selecionada}", labels={"identification": "Genus"}, color_discrete_sequence=px.colors.qualitative
grafico_linha.update_layout(xaxis_title="Month", yaxis_title="# of Colonies Observed", xaxis={'categoryorder': 'array', 'categoryarray': list(nomes_meses.values())})
st.plotly_chart(grafico_linha, use_container_width=True) (em inglês)
mais:
st.info(f"número de fundo para a origem: {origem_selecionada}")

=========================================================================================================


REGISTRO DE MONITORAMENTO


=========================================================================================================

def pagina_registro():
st.title("Registro de Monitoramento")
df = observar_amostras()
codigos = df["code"].tolist() se não df.empty else []
= st.radio("Ação", ["No registrovo", "Editar registro", "Excluir registro"], horizontal=True)
reg = df[df["code"] == st.selectbox("Selecione o CODE", codigos)].iloc[0].fillna("").to_dict() se em ["Editar registro", "Excluir registro"] e codigos else {}
se == "Excluir registro":
se não codigos:
st.info(Nom" encontrado registro para excluir.")
retorno
st.warning(f"⚠️: Você está está prestes a exclui definitivamente uma amostra {reg.get('code')}.)
confirmar_exclusao = st.checkbox(f"Confirmo que quere permanentemente deletar a amostra {reg.get('code')}")
if st.button("❌ Deletar Registro Permanentemente", type="primary", disabled=not_exclusao, use_container_width=True):
excluir_amostra(reg.get("código"))
st.success(f"Amostra {reg.get('code')} deletada!")
st.rerun()
mais:
com st.form("form_amostra"):
col1, col2, col3 = st.columns(3)
se == modo "Novo registro":
ultimo_registro =(cons:"SELECT code FROM sampleSOR BY code DESC LIMIT 1")
se ultimo_registro:
ultimo_code = ultimo_registro[0]["code"]
tentar:
prefixo, numero = ultimo_code.split("-")
code_sugerido = f"{prefixo}-{int(numero) + 1:03d}"
exceto ValueError: code_sugerido = "B4-006"
mais: code_sugerido = "B4-001"
código = col1.text_input("CODE *", value=code_sugerido)
mais:
código = col1.text_input("CODE *", reg.get("code", ""), desativado=True)
ponto = col2.text_input("OBSERVAÇÃO", reg.get("ponto", ""))
analista = col3.text_input("ANALYST", reg.get("analista", ""))
col4, col5, col6 = st.columns(3)
com col4: origem = campo_selecao("ORIGIN", "ORIGIN", reg.get("origin", ""))
com col5: amostra = campo_selecao("SAMPLE", "SAMPLE", reg.get("sample", ""))
com col6: amostragem = campo_selecao("AMOSTRAGEM", "AMOSTRAGEM", reg.get("amostragem", ""))
col7, col8, col9 = st.columns(3)
com col7: area = campo_selecao("AREA", "AREA", reg.get("areae", ""))
com col8: collection_point = campo_selecao("COLLECTION POINT", "COLLECTION POINT", reg.get("collection_point", ""))
com col9: method = campo_selecao("METHOD", "METHOD", reg.get("method", ""))
col10, col11, col12 = st.columns(3)
com col10: frequencia = st.selectbox("FREQUENCY", ["", "Semanal", "Mensal"], index=["", "Semanal", "Mensal"].index(reg.get("frequencia", "")) if reg.get("frequencia", "") in ["", "Semanal", "Mensal"] else 0)
com col11:
dt_at = pd.to_datetime(reg.get("data", ""), errors="coerce")
dados = st.date_input("DATA", value=None if pd.isna(dt_at) else dt_at.date(), format="DD/MM/YYYY")
com col12: result_final = st.selectbox("RESULT", ["", "Conforme", "Não Conform"], index=["", "Conforme", "No Conform"].index(reg.get("resultado_final", "")) if reg.get("resultado_final", "") in ["", "Conforme", "Não”] else 0)
enviado_reg = st.form_submit_button("Salvar Registro", type="primary")
if enviado_reg e code.strip():
salvar_amostra({"code": code.strip(), "poton": ponto, "origin": origin, "area": area, "sample": sample, "collection_point": collection_point, "sampling": sampling, "method": method, "frequencia": frequencia, "analista": analista: "data": data.isoformat()
st.success("Registro Corretamente Salvo!")
st.rerun()
st.subheader("Amostras cadastradas")
st.dataframe(df, use_container_width=True, hide_index=True, column_config={"code": "CODE", "ponto": "OBSERVATION", "origin": "ORIGIN", "area": "AREA", "sample": "SAMPLE", "collection_point": "COLLECTION POINT", "sampling": "A

=========================================================================================================


IDENTIFICAÇÃO MICROBIOLÓGICA


=========================================================================================================

def pagina_identificacao():
st.title("Ident Microbiológica")
df = obter_identificacoes() Em inglês
se df.empty:
st.info("Cadaste uma amostra antes de a preencher.")
retorno
código = st.selectbox("Selecione o CODE", df["code"].tolist())
registro = df[df["code"] == código].iloc[0].fillna("").to_dict()
st.info(f"Área: {registro.get('area', '—')} | Ponto: {registro.get('collection_point', '—')} | Dados: {registro.get('data', '—')}")
com st.form("formulario_identificacao"):
1,1,2 = st.columns(2)
com1 coluna:
form = campo_selecao("MORPHOLOGY", "FORM", registro.get("form", ""))
gram_stain = campo_selecao("GRAM STAIN", "AFFIRMATION", logot.get("gram_stain", ""))
identificação = st.text_input("IDENTIFICATION", registro.get("identification", ""))
opcoes_metodo = ["", "Sequenciamento de NGS", "Maldi TOF", "Outros"]
valor_salvo = registro.get("outsourced_method", "")
if valor_salvo == "Sequenciamento NGS": valor_salvo = "Sequenciamento de NGS"
if valor_salvo == "Outros": valor_salvo = "Outros"
if valor_salvo não em opcoes_metodo: opcoes_metodo.append(valor_salvo)
outsourced_method = st.selectbox("OUTSOURCED METHOD", opcoes_metodo, index=opcoes_metodo.index(valor_salvo) if valor_salvo in opcoes_metodo else 0)
com a coluna2:
empresa = st.text_input("COMPANY", registro.get("company", ""))
col_data1, col_data2 = st.columns(2)
com col_data1:
dt_ini = pd.to_datetime(registro.get("start_date", ""), errors="coerce")
start_date = st.date_input("START DATE", value=None if pd.isna(dt_ini) else dt_ini.date(), format="DD/MM/YYYY")
com col_data2:
dt_fim = pd.to_datetime(registro.get("end_date", ""), errors="coerce")
end_date = st.date_input("END DATE", value=None if pd.isna(dt_fim) else dt_fim.date(), format="DD/MM/YYYYY")
arquivo_anexo = st.file_uploader("ATTACH REPORT", type=["doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "pdf"])
removedre_anexo = st.checkbox("❌ Removedor de execução atual")
enviado = st.form_submit_button("Salvar", idote="primary", use_container_width=True)
se enviado:
nome_relatorio = "" if removeder_anexo else (arquivo_anexo.name if arquivo_anexo else registro.get("report", ""))
bytes_arquivo = Nenhum se remover_anexo else (arquivo_anexo.getvalue() if arquivo_anexo else Nenhum)
sql_salvar = """
INSERIR INTO identificacoes (código, formulário, grama_mancha, outsourced_method, identificação, relatório, empresa, start_date, end_date, report_data)
VALORES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) EM CONFLITO(cóDIGO) FAZER ATUALIZAÇÃO SET
form=excluded.form, gram_stain=excluded.gram_stain, outsourced_method=excluded.outsourced_method, identificatificly=excluded.identification,
company=excluded.company, start_date=excluded.start_date, end_date=excluded.end_date,
relatório=CASO QUANDO ? EM SEGUIDA, excluído.report ELSE identificacoes.report END,
report_data=CASE QUANDO? EM SEGUIDA, excluído.report_data ELSE identificacoes.report_data END
"""
com o connecto() como conexao:
conexao.execute(sql_salvar, (código, formulário, gram_stain, outsourced_method, identificação, nome_relatorio, empresa, start_date.isoformat() se start_date else "", end_date.isoformat() if end_date else "", bytes_arquivo,_anexo is not None or removedre_anexo
st.success("Ident salvaificação!")
st.rerun()

=========================================================================================================


ARMAZENAMENTO


=========================================================================================================

def pagina_armazenamento():
st.title("Armazenamento de Isolados Identificados")
df = obter_identificacoes() Em inglês
se df.empty:
st.info(Número" amostra cadastrada.")
retorno
= armazenamento df[["code", "gram_stain", "identification"]].copy()
armazenamentos.columns = ["CÓDIGO", "GRAM STAIN", "IDENTIFICAÇÃO"]
st.dataframe(armazenamento, use_container_width=True, hide_index=True) (em inglês)

=========================================================================================================


DADOS BRUTOS (NOVA ABA)


=========================================================================================================

def pagina_dados_brutos():
st.title("🗃️ Registro de Dados de Brutos (Dados Brutos)")
st.caption("Gerenciamento de lotes de insumos, meios de equipamentos culturais e mapeados na.")
com o connecto() como conexao:
conexao.execute("CREATE TABLE IF NOT EXISTS dados_brutos (id INTEGER PRIMARY KEY AUTOINCREMENT, tsb TEXT, glicerina TEXT, tsa TEXT, criotubo TEXT, placa_de_petri TEXT, fluxo_laminar TEXT, ultrafreezer TEXT,_em TEXT DEFAULT CUR
tentar:
linhas =("SELECTid, tsb, glicerina, tsa, criotubo, placa_de_petri,_laminar, ultrafreezer FROM dados_brutos ORDER BY id DESC")
exceto Exceção: lnhas = []
df_brutos = pd.DataFrame(linhas)
lista_ids = df_brutos["id"].tolist() se não não df_brutos.empty else []
= st.radio("Ação", ["📋 Visualizar Planilha", "➕ Manual da Linha Inserir", "✏️ Editar Linha", "❌ Excluir Linha"], horizontal=True)
se == «📋 Visualizar Planilha»:
se df_brutos.empty:
st.info(Número" dado doado. Use um manual de inserção ou via.")
mais:
st.markdown(## 🧪 Status de Insumos Cíticos e Equipamentos)
ultimo_registro = df_brutos.iloc[0]
c1, c2, c3 = st.columns(3)
com c1: st.metric(label="🧫 Meio TSB", value=str(ultimo_registro['tsb'])[:12] if ultimo_registro['tsb'] else "Sem Lote")
com c2: st.metric(label="🧫 Meio TSA", value=str(ultimo_registro['tsa'])[:12] if ultimo_registro['tsa'] else "Pendente")
com c3: st.metric(label="❄️ Ultra-Freezer", value=str(ultimo_registro['ultrafreezer'])[:10], delta="-80°C Garantido")
st.markdown("
", insafe_allow_html=True)Tradução
st.dataframe(df_brutos, use_container_width=True, hide_index=True, column_config={"id": "ID", "tsb": "TSB", "glicerina": "GLICERINA", "tsa": "TSA", "criotubo": "CRIOTUBO", "placa_de_petri": "PLACA"
elif == modo "❌ Excluir Linha":
if not lista_ids: return
id_sel = st.selectbox("Selecione o ID para removedor:", listo_ids)
if st.button("❌ Deletar Permanentemente", type="primary", use_container_width=True):
com conetro() como conexao: conexao.execute("DELETE F de dados_brutos WHERE id = ?", (id_sel,))
st.success("Deletado!")
st.rerun()
mais:
reg = df_brutos[df_brutos["id"] == st.selectbox("Selecione o ID para:", listes_ids)].iloc[0].to_dict() if == "✏️ Editar Linha" and lists_ids else {}
com st.form("form_brutos"):
c1, c2, c3 = st.columns(3)
tsb = c1.text_input("TSB", value=reg.get("tsb", ""))
glicerina = c2.text_input("GLICERINA", value=reg.get("glicerina", ""))
tsa = c3.text_input("TSA", value=reg.get("tsa", ""))
c4, c5, c6 = st.columns(3)
criotubo = c4.text_input("CRIOTUBO", value=reg.get("criotubo", ""))
placa = c5.text_input("PLACA DE PETRI", value=reg.get("placa_de_petri", ""))
fluxo = c6.text_input("FLUXO LAMINAR", value=reg.get("fluxo_laminar", ""))
ultrafreezer = st.text_input("ULTRAFREEZER", value=reg.get("ultrafreezer", ""))
if st.form_submit_button("Salvar Brutos", type="primary"):
com o connecto() como conexao:
if == modo "✏️ Editar Linha":
conexao.execute("UPDATE dados_brutos SET tsb=?, glicerina=?, tsa=?, criotubo=?, placa_de_petri=? fluxo,_laminar=?, ultrafreezer=? WHERE id=?", (tsb, glicerina, tsa, criotubo, placa, fluxo, ultrafreezer, id_sel))
mais:
conexao.execute("INSERT INTO dados_brutos (tsb, glicerina, tsa, criotubo, placa_de_petri, fluxo_laminar, ultrafreezer) VALORES (?, ?, ?, ?, ?, ?, ?, ?)", (tsb, glicerina, tsa, criotubo, placa, fluxo, ultrafreezer)
st.success("Salvo com sucesso!")
st.rerun()

=========================================================================================================


PAGINA DE IMPORTAÇÃO E EXPORTAÇÃO (RESTAURADA)


=========================================================================================================

def normalizar_coluna(nome):
conversas = {
"CÓDIGO": "código", "PONTO": "ponto", "ORIGEM": "origem", "ÁREA": "Área", "AMOSTRA": "amostra",
"PONTO DE COLEÇÃO": "collection_point", "AMOSTRAGEM": "amostragem", "MÉTODO": "método",
"FREQUÊNCIA": "frequencia", "FREQUENCIA": "frequencia", "ANALISTA": "analista", "DATA": "data",
"RESULTADO": "resultado", "FORM": "forma", "MARGEM": "margem", "PIGMENT": "pigmento",
"GRAM STAIN": "gram_stain", "CATALASE": "catalase", "KOH": "koh", "OXIDASE": "oxidase",
"MÉTODO TERCEIRIZADO": "outsourced_method", "IDENTIFICAÇÃO": "identificação", "REPORT": "report",
"COMPANHIA": "empresa", "END DATE": "end_date",
"TSB": "tsb", "GLICERINA": "glicerina", "TSA": "tsa", "CRIOTUBO": "criotubo",
"PLACA DE PETRI": "placa_de_petri", "FLUXO LAMINAR": "fluxo_laminar", "ULTRAFREEZER": "ultrafreezer"
}
retorno conversoes.get(str(nome).strip().upper(), str(nome).strip().lower().replace(" ", "_"))
def_excel(arquivo):
com o connecto() como conexao:
tentar:
df_brutos = pd.read_excel(arquivo, sheet_name="Dados Brutos")
df_brutos.columns = [normalizar_coluna(col) para col em df_brutos.columns]
colonos_obrigatorias = ["tsb", "glicerina", "tsa", "criotubo", "placa_de_petri", "fluxo_laminar", "ultrafreezer"]
para col in colunas_obrigatorias:
se não estiver em df_brutos.columns: df_brutos[col] = ""
df_brutos = df_brutos.fillna("")
conexao.execute("EXCLUIR DE dados_brutos")
para _, linha em df_brutos.iterrows():
conexao.execute("INSERT INTO dados_brutos (tsb, glicerina, tsa, criotubo, placa_de_petri, fluxo_laminar, ultrafreezer) VALORES (?, ?, ?, ?, ?, ?, ?)", (str(get(tsb", "tsb", ")), str(get(get("glicerina"),
st.success("✔️ Dados Brutos automaticamente atualizado!")
exceto Exceção: st.info("i️ Aba 'Dados Brutos' não no localizada Excel.")
tentar:
arquivo.seek(0)
registro = pd.read_excel(arquivo, sheet_name="Registro")
arquivo.seek(0)
identificacao = pd.read_excel(arquivo, sheet_name="Identification")
registro.coluns = [normalizar_coluna(c) para c no registro.columns]
identificacao.columns = [normalizar_coluna(c) para c em identificacao.columns]
registro = registro.fillna("").loc[lambda d: d["code"].ne("")]
identificacao = identificacao.fillna("").loc[lambda d: d["code"].ne("")]
conexao.execute("EXCLUIR DE identificacoes")
conexao.execute("EXCLUIR DE"EMOSTRAS")
para _, r em registro.iterrows():
conexao.execute(f"INSERTE INTO (semasms ({','.join(COLUNAS_AMOSTRA)}) VALORES ({','.join('?' for _ in COLUNAS_AMOSTRA)})", [r.get(c, "") para c em COLUNAS_AMOSTRA])
para _, i em identificacao.iterrows():
conexao.execute(f"INSERTE EM identificacoes ({','.join(COLUNAS_IDENTIFICACAO))) VALORES ({','.join('?' para _ em COLUNAS_IDENTIFICACAO)})", [i.get(c, ") para c em COLUNAS_IDENTIFICACAO])
st.success("✔️ Colesinchatas schingasizadas!")
exceto Exceção como e: st.error(f"Erro nas padrões: {e}")
def pagina_dados():
st.title("Importação e Exportação")
st.download_button(label="Baixar dados em Excel", data=gerar_excel(), file_name="monitoramento_microbiologico.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
st.divider()Tradução
st.subheader("Importar arquivo Excel")
st.warning("A importaçãoá os atuais registros. Faça backup antes.")
arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
= st.checkbox("Confirmo a total")
se arquivo não é Nenhum e confirmar e st.button("Importar dados", type="primary"):
tentar:
importador_excel(arquivo)
st.success("Dados importados com sucesso.")
st.rerun()
exceto Exceção como erro: st.error(f"Erro na importar: {erro}")

=========================================================================================================


INICIALIZAÇÃO E ROTEAR ABAS


=========================================================================================================

se não mostrar_login():
st.stop()
criar_banco()
st.sidebar.markdown('🧫 NataliaMonitoramento Microbiológico', unsafe_allow_html=True)
st.sidebar.caption(f"Conectado como {st.session_state.get('usaurio', 'Natalia')}")
pagina = st.sidebar.radio("Navegação", ["Dashboard", "Registro", "Identificação", "Armazenamento", "Dados", "Dados Brutos"])
st.sidebar.divider() Em inglês
if st.sidebar.button("Sair", use_container_width=True):
st.session_state.autenticado = Falso
st.rerun()
st.markdown('BIOBANK - NATALIAGestãos de integrada cepas, identificação e armazenamento.', unsafe_allow_html=True)
if pagina == "Dashboard": pagina_dashboard()
elif pagina ==Se
elif pagina == "Identificação": pagina_identificacao()
elif pagina ==Sestejamento: "Armazenamento": pagina_armazenamento()
elif pagina ==Seguidas Brutos: pagina_dados_brutos()
elif pagina == "Dados": pagina_dados()
