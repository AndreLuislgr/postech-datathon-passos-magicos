"""
Datathon Passos Mágicos — App Streamlit de Predição de Risco de Defasagem
--------------------------------------------------------------------------
Carrega o modelo treinado (modelo_risco_defasagem.pkl) e disponibiliza um
formulário simples: o usuário informa os indicadores do aluno e o app
retorna a probabilidade de risco de defasagem no ano seguinte.

Rodar localmente:
    streamlit run app.py

Deploy: ver instruções no final desta conversa (Streamlit Community Cloud).
"""

import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Risco de Defasagem — Passos Mágicos", page_icon="🎯", layout="centered")

# -----------------------------------------------------------------------
# Carregar modelo (cacheado para não recarregar a cada interação)
# -----------------------------------------------------------------------
@st.cache_resource
def carregar_modelo():
    return joblib.load("modelo_risco_defasagem.pkl")

modelo = carregar_modelo()

FEATURES_NUMERICAS = ["IAN", "IDA", "IEG", "IAA", "IPS", "IPP", "IPV", "INDE",
                       "DEFASAGEM", "IDADE", "GAP_ENGAJAMENTO_APRENDIZAGEM",
                       "TEMPO_NA_PM"]
FEATURES_CATEGORICAS = ["PEDRA", "GENERO"]

st.title("🎯 Risco de Defasagem — Passos Mágicos")
st.markdown(
    "Informe os indicadores do aluno no ano atual para estimar a "
    "**probabilidade de risco de defasagem no ano seguinte** "
    "(Fase abaixo da Fase Ideal)."
)

st.divider()

# -----------------------------------------------------------------------
# Formulário de entrada
# -----------------------------------------------------------------------
with st.form("form_aluno"):
    st.subheader("Indicadores do aluno")

    col1, col2 = st.columns(2)
    with col1:
        ian = st.slider("IAN — Adequação ao Nível", 0.0, 10.0, 7.0, 0.1)
        ida = st.slider("IDA — Aprendizagem", 0.0, 10.0, 7.0, 0.1)
        ieg = st.slider("IEG — Engajamento", 0.0, 10.0, 7.0, 0.1)
        iaa = st.slider("IAA — Autoavaliação", 0.0, 10.0, 7.0, 0.1)
        ips = st.slider("IPS — Psicossocial", 0.0, 10.0, 7.0, 0.1)
        ipp = st.slider("IPP — Psicopedagógico", 0.0, 10.0, 7.0, 0.1)

    with col2:
        ipv = st.slider("IPV — Ponto de Virada", 0.0, 10.0, 7.0, 0.1)
        inde = st.slider("INDE — Índice geral", 0.0, 10.0, 7.0, 0.1)
        defasagem = st.slider("Defasagem atual (Fase - Fase Ideal)", -5, 3, 0)
        idade = st.number_input("Idade", min_value=5, max_value=25, value=12)
        pedra = st.selectbox("Pedra", ["Quartzo", "Ágata", "Ametista", "Topázio"])
        genero = st.selectbox("Gênero", ["Feminino", "Masculino"])

    col3, col4 = st.columns(2)
    with col3:
        ano_ingresso = st.number_input("Ano de ingresso na Passos Mágicos", min_value=2010, max_value=2024, value=2022)
    with col4:
        ano_referencia = st.number_input("Ano de referência (ano atual)", min_value=2020, max_value=2030, value=2024)

    enviado = st.form_submit_button("Calcular risco", use_container_width=True)

# -----------------------------------------------------------------------
# Predição
# -----------------------------------------------------------------------
if enviado:
    entrada = pd.DataFrame([{
        "IAN": ian, "IDA": ida, "IEG": ieg, "IAA": iaa, "IPS": ips, "IPP": ipp,
        "IPV": ipv, "INDE": inde, "DEFASAGEM": defasagem, "IDADE": idade,
        "GAP_ENGAJAMENTO_APRENDIZAGEM": ieg - ida,
        "TEMPO_NA_PM": ano_referencia - ano_ingresso,
        "PEDRA": pedra, "GENERO": genero,
    }])

    probabilidade = modelo.predict_proba(entrada)[0, 1]
    classe = modelo.predict(entrada)[0]

    st.divider()
    st.subheader("Resultado")

    pct = probabilidade * 100
    if pct >= 60:
        st.error(f"⚠️ Risco ALTO de defasagem: **{pct:.1f}%**")
    elif pct >= 35:
        st.warning(f"🟡 Risco MODERADO de defasagem: **{pct:.1f}%**")
    else:
        st.success(f"✅ Risco BAIXO de defasagem: **{pct:.1f}%**")

    st.progress(min(int(pct), 100))

    st.caption(
        "Este é um indicador de apoio à decisão, baseado em padrões históricos "
        "da base PEDE. Não substitui a avaliação pedagógica/psicossocial da "
        "equipe da Passos Mágicos — use como sinal de atenção, não como "
        "veredito único."
    )

st.divider()
st.caption("Modelo: Random Forest treinado sobre a base PEDE 2022–2024 · Datathon PosTech")
